"""
PROBLEMA DEL AGENTE VIAJERO (TSP)
Matemática Computacional · 1AMA0475 · UPC

Idea general del programa
-------------------------
1. Se construye un grafo no dirigido y ponderado (aleatorio o ingresado a mano).
2. Se busca el ciclo hamiltoniano de menor costo: una ruta que sale del nodo 0,
   visita cada nodo exactamente una vez y vuelve al nodo 0.
3. Para resolverlo se usa el algoritmo de fuerza bruta: se prueban todas las
   rutas posibles (permutaciones de los nodos) y se guarda cada camino válido.
   Es exacto (siempre encuentra el óptimo) y además permite mostrar todos los
   caminos existentes con su etiqueta (C1, C2, ...) y su costo.
"""

import itertools
import math
import os
import random
import threading
import time

import customtkinter as ctk
from tkinter import messagebox
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image


# =====================================================================
#  DATOS DEL PROYECTO
# =====================================================================
UNIVERSIDAD = "Universidad Peruana de Ciencias Aplicadas"
FACULTAD = "Facultad de Ingeniería"
CURSO = "1AMA0475 · Matemática Computacional"
SECCION = "2911"
DOCENTE = "Mattos Quevedo, Juan Manuel"
CICLO = "2026-02"
INTEGRANTES = [            # (nombre, código)
    ("Coras Zelada, Bruno Enrique", "u202424853"),
    ("Condori Ramos, Aldo", "u202419673"),
    ("Lopez Atencia, Jhonatan Ismael", "u202416648"),
    ("Romero Pasache, Rolando Miguel", "u202313521"),
    ("Lorenzo Nicolas, Luana Suhey", "u202414362"),
]
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "upc_logo.png")

MIN_NODOS, MAX_NODOS = 5, 10
PESO_MIN, PESO_MAX = 9, 100

# =====================================================================
#  ESTILO
# =====================================================================
F = "Segoe UI"            # fuente general
MONO = "Consolas"         # fuente para la matriz y la ruta

BG = "#0e1117"
PANEL = "#161b22"
PANEL2 = "#1f2630"
BORDE = "#2a323d"
TEXTO = "#e6edf3"
SUAVE = "#8b949e"
ACENTO = "#5b8cff"
ACENTO_H = "#4776e6"
EXITO = "#2ecc8f"
EXITO_H = "#25a877"
RUTA = "#ff7849"
NODO = "#3b4a63"
ARISTA = "#6e7681"


# =====================================================================
#  LÓGICA (independiente de la interfaz)
# =====================================================================

def grafo_aleatorio(n, completo=True, densidad=0.45):
    """Crea un grafo con n nodos. Si no es completo, cada arista existe con
    probabilidad 'densidad'. Todos los nodos existen aunque queden aislados."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if completo or random.random() < densidad:
                G.add_edge(i, j, weight=random.randint(PESO_MIN, PESO_MAX))
    return G


def grafo_desde_texto(n, texto):
    """Lee conexiones con el formato 'origen destino costo' (una por línea).
    Devuelve el grafo y una lista de errores encontrados."""
    G = nx.Graph()
    G.add_nodes_from(range(n))
    errores = []
    for num, linea in enumerate(texto.splitlines(), start=1):
        linea = linea.split("#")[0].strip()          # permite comentarios con #
        if not linea:
            continue
        partes = linea.replace(",", " ").split()
        if len(partes) != 3:
            errores.append(f"Línea {num}: se esperan 3 valores (origen destino costo).")
            continue
        try:
            u, v, w = map(int, partes)
        except ValueError:
            errores.append(f"Línea {num}: solo se aceptan números enteros.")
            continue
        if not (0 <= u < n and 0 <= v < n):
            errores.append(f"Línea {num}: los nodos van de 0 a {n - 1}.")
        elif u == v:
            errores.append(f"Línea {num}: un nodo no puede conectarse consigo mismo.")
        elif w <= 0:
            errores.append(f"Línea {num}: el costo debe ser mayor que 0.")
        else:
            G.add_edge(u, v, weight=w)
    return G, errores


def matriz_adyacencia(G):
    """Matriz n x n ordenada por número de nodo. 0 = no hay arista."""
    n = G.number_of_nodes()
    M = [[0] * n for _ in range(n)]
    for u, v, d in G.edges(data=True):
        M[u][v] = M[v][u] = d["weight"]
    return M


def diagnostico(G):
    """Condiciones necesarias para que exista un ciclo hamiltoniano."""
    if not nx.is_connected(G):
        return "El grafo no es conexo: hay nodos a los que no se puede llegar."
    pocos = [v for v, d in G.degree() if d < 2]
    if pocos:
        return (f"Los nodos {pocos} tienen menos de 2 conexiones. "
                "Un ciclo necesita entrar y salir de cada nodo.")
    return None


def costo_ruta(M, ruta):
    """Suma los costos de los tramos de la ruta. Si algún tramo no existe
    en el grafo (vale 0 en la matriz), la ruta no es válida y devuelve None."""
    total = 0
    for a, b in zip(ruta, ruta[1:]):
        if M[a][b] == 0:
            return None
        total += M[a][b]
    return total


def fuerza_bruta(M):
    """
    Algoritmo de fuerza bruta.

    1. Se fija el nodo 0 como inicio y fin del recorrido.
    2. Se generan todas las permutaciones de los demás nodos: (n-1)! rutas.
    3. Un ciclo recorrido al revés cuesta lo mismo (0→1→2→0 = 0→2→1→0),
       así que solo se evalúa una de las dos versiones: (n-1)!/2 rutas.
    4. Cada ruta válida se guarda como un camino existente.
    5. La ruta óptima es el camino de menor costo.

    Complejidad: O(n!), por eso el programa trabaja de 5 a 10 nodos.
    """
    n = len(M)
    caminos = []           # todos los caminos válidos (ciclos hamiltonianos)
    evaluadas = 0          # cuántas rutas se revisaron
    for perm in itertools.permutations(range(1, n)):
        # descartar la versión invertida del mismo ciclo
        if perm[0] > perm[-1]:
            continue
        evaluadas += 1
        ruta = [0, *perm, 0]               # salir del 0 y volver al 0
        costo = costo_ruta(M, ruta)
        if costo is not None:              # solo si todos los tramos existen
            caminos.append({"ruta": ruta, "costo": costo})

    if not caminos:
        return None

    # la ruta óptima es la de menor costo entre todos los caminos
    mejor = min(caminos, key=lambda c: c["costo"])
    return {
        "costo": mejor["costo"],
        "ruta": mejor["ruta"],
        "ciclos": len(caminos),
        "caminos": caminos,
        "evaluadas": evaluadas,
    }


def held_karp(M):
    """
    Algoritmo de Held-Karp (programación dinámica con máscaras de bits).
    Se usa para comparar: debe dar el mismo costo mínimo que la fuerza bruta,
    pero en mucho menos tiempo.

    Una 'máscara' es un número cuyos bits indican qué nodos ya se visitaron.
      dp[mask][j]  = menor costo de un camino que sale de 0, visita
                     exactamente los nodos de 'mask' y termina en j.
      cnt[mask][j] = cuántos caminos distintos cumplen lo anterior
                     (sirve para contar los ciclos hamiltonianos).
      padre[mask][j] = nodo anterior a j en el mejor camino (para reconstruir).

    Complejidad: O(n² · 2ⁿ), frente a O(n!) de la fuerza bruta.
    """
    n = len(M)
    INF = float("inf")
    TOTAL = 1 << n
    dp = [[INF] * n for _ in range(TOTAL)]
    cnt = [[0] * n for _ in range(TOTAL)]
    padre = [[-1] * n for _ in range(TOTAL)]
    vecinos = [[k for k in range(n) if M[j][k] > 0] for j in range(n)]

    dp[1][0] = 0          # empezamos en el nodo 0 (máscara 000...001)
    cnt[1][0] = 1

    for mask in range(1, TOTAL, 2):           # solo máscaras que incluyen al 0
        for j in range(n):
            costo = dp[mask][j]
            if costo == INF:
                continue
            formas = cnt[mask][j]
            for k in vecinos[j]:
                bit = 1 << k
                if mask & bit:                 # k ya fue visitado
                    continue
                nueva = mask | bit
                cnt[nueva][k] += formas
                if costo + M[j][k] < dp[nueva][k]:
                    dp[nueva][k] = costo + M[j][k]
                    padre[nueva][k] = j

    # Cerrar el ciclo: desde el último nodo volver al 0
    completo = TOTAL - 1
    mejor, ultimo, caminos = INF, -1, 0
    for j in range(1, n):
        if M[j][0] > 0 and dp[completo][j] < INF:
            caminos += cnt[completo][j]
            if dp[completo][j] + M[j][0] < mejor:
                mejor = dp[completo][j] + M[j][0]
                ultimo = j

    if ultimo == -1:
        return None

    # Reconstruir la ruta siguiendo los 'padres' hacia atrás
    camino, mask, j = [], completo, ultimo
    while j != -1:
        camino.append(j)
        anterior = padre[mask][j]
        mask ^= 1 << j
        j = anterior
    ruta = camino[::-1] + [0]

    return {
        "costo": mejor,
        "ruta": ruta,
        # cada ciclo se cuenta 2 veces (en un sentido y en el otro)
        "ciclos": caminos // 2,
    }


def fmt(num):
    """12345678 -> '12 345 678'"""
    return f"{num:,}".replace(",", " ")


def cargar_logo(tamano):
    """Devuelve el logo como CTkImage, o None si el archivo no está."""
    try:
        img = Image.open(LOGO)
        return ctk.CTkImage(light_image=img, dark_image=img, size=(tamano, tamano))
    except (OSError, FileNotFoundError):
        return None


# =====================================================================
#  VENTANAS SECUNDARIAS
# =====================================================================

class VentanaManual(ctk.CTkToplevel):
    """Permite escribir todas las conexiones en una sola pantalla."""

    def __init__(self, master, n, al_aceptar):
        super().__init__(master)
        self.n = n
        self.al_aceptar = al_aceptar
        self.title("Ingreso manual")
        self.geometry("520x580")
        self.configure(fg_color=BG)
        self.transient(master)
        self.after(150, self._enfocar)

        ctk.CTkLabel(self, text="Conexiones del grafo", font=(F, 22, "bold"),
                     text_color=TEXTO).pack(anchor="w", padx=24, pady=(20, 2))
        ctk.CTkLabel(self, justify="left", font=(F, 13), text_color=SUAVE,
                     text=(f"Una conexión por línea:  origen  destino  costo\n"
                           f"Nodos disponibles: 0 a {n - 1}   ·   Ejemplo:  0 3 25")
                     ).pack(anchor="w", padx=24, pady=(0, 10))

        self.caja = ctk.CTkTextbox(self, font=(MONO, 15), fg_color=PANEL,
                                   text_color=TEXTO, border_color=BORDE,
                                   border_width=1, corner_radius=12)
        self.caja.pack(fill="both", expand=True, padx=24)

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=24, pady=16)
        ctk.CTkButton(barra, text="Cargar ejemplo", width=130, fg_color=PANEL2,
                      hover_color=BORDE, command=self._ejemplo).pack(side="left")
        ctk.CTkButton(barra, text="Crear grafo", width=130, fg_color=EXITO,
                      hover_color=EXITO_H, text_color="#0b1a13",
                      font=(F, 14, "bold"), command=self._aceptar).pack(side="right")
        ctk.CTkButton(barra, text="Cancelar", width=100, fg_color="transparent",
                      border_width=1, border_color=BORDE, hover_color=PANEL2,
                      command=self.destroy).pack(side="right", padx=8)

    def _enfocar(self):
        self.lift()
        self.focus_force()
        self.grab_set()

    def _ejemplo(self):
        """Un anillo (garantiza un ciclo) más algunas cuerdas al azar."""
        lineas = [f"{i} {(i + 1) % self.n} {random.randint(PESO_MIN, PESO_MAX)}"
                  for i in range(self.n)]
        for _ in range(self.n):
            u, v = random.sample(range(self.n), 2)
            lineas.append(f"{u} {v} {random.randint(PESO_MIN, PESO_MAX)}")
        self.caja.delete("1.0", "end")
        self.caja.insert("1.0", "\n".join(lineas))

    def _aceptar(self):
        G, errores = grafo_desde_texto(self.n, self.caja.get("1.0", "end"))
        if errores:
            extra = f"\n… y {len(errores) - 8} más" if len(errores) > 8 else ""
            messagebox.showerror("Revisa las conexiones",
                                 "\n".join(errores[:8]) + extra, parent=self)
            return
        if G.number_of_edges() == 0:
            messagebox.showerror("Sin conexiones", "Escribe al menos una conexión.",
                                 parent=self)
            return
        self.grab_release()
        self.destroy()
        self.al_aceptar(G)


# =====================================================================
#  VENTANA PRINCIPAL
# =====================================================================

class App(ctk.CTk):

    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("Problema del Agente Viajero")
        self.geometry("1320x780")
        self.minsize(1150, 700)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._salir)

        self.G = None            # grafo actual
        self.pos = None          # posiciones de los nodos para dibujar
        self.resultado = None    # respuesta de fuerza_bruta
        self._animando = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._crear_panel_izquierdo()
        self._crear_centro()
        self._crear_panel_derecho()
        self._dibujar()
        self._actualizar_matriz()

    # ------------------------------------------------------------------
    #  Construcción de la interfaz
    # ------------------------------------------------------------------
    def _titulo_paso(self, master, numero, texto):
        fila = ctk.CTkFrame(master, fg_color="transparent")
        fila.pack(fill="x", padx=22, pady=(22, 10))
        ctk.CTkLabel(fila, text=numero, width=26, height=26, corner_radius=13,
                     fg_color=ACENTO, text_color="white",
                     font=(F, 13, "bold")).pack(side="left")
        ctk.CTkLabel(fila, text=texto, font=(F, 15, "bold"),
                     text_color=TEXTO).pack(side="left", padx=10)

    def _crear_panel_izquierdo(self):
        p = ctk.CTkFrame(self, width=300, fg_color=PANEL, corner_radius=0)
        p.grid(row=0, column=0, sticky="nsew")
        p.pack_propagate(False)

        ctk.CTkLabel(p, text="Agente Viajero", font=(F, 26, "bold"),
                     text_color=TEXTO).pack(anchor="w", padx=22, pady=(26, 0))
        ctk.CTkLabel(p, text="Ruta más corta que visita todos los nodos",
                     font=(F, 13), text_color=SUAVE).pack(anchor="w", padx=22)

        # --- Paso 1: configurar el grafo ---
        self._titulo_paso(p, "1", "Configura el grafo")

        self.lbl_nodos = ctk.CTkLabel(p, text=f"Cantidad de nodos: {MIN_NODOS}",
                                      font=(F, 13), text_color=SUAVE)
        self.lbl_nodos.pack(anchor="w", padx=22)
        self.slider_nodos = ctk.CTkSlider(
            p, from_=MIN_NODOS, to=MAX_NODOS, number_of_steps=MAX_NODOS - MIN_NODOS,
            button_color=ACENTO, progress_color=ACENTO,
            command=lambda v: self.lbl_nodos.configure(text=f"Cantidad de nodos: {int(v)}"))
        self.slider_nodos.set(MIN_NODOS)
        self.slider_nodos.pack(fill="x", padx=22, pady=(4, 14))

        ctk.CTkLabel(p, text="Tipo de grafo", font=(F, 13),
                     text_color=SUAVE).pack(anchor="w", padx=22)
        self.modo = ctk.CTkSegmentedButton(
            p, values=["Completo", "Parcial", "Manual"], font=(F, 13),
            selected_color=ACENTO, selected_hover_color=ACENTO_H,
            unselected_color=PANEL2, command=self._cambiar_modo)
        self.modo.set("Completo")
        self.modo.pack(fill="x", padx=22, pady=(4, 12))

        self.frame_dens = ctk.CTkFrame(p, fg_color="transparent")
        self.lbl_dens = ctk.CTkLabel(self.frame_dens, text="Densidad de aristas: 45 %",
                                     font=(F, 13), text_color=SUAVE)
        self.lbl_dens.pack(anchor="w")
        self.slider_dens = ctk.CTkSlider(
            self.frame_dens, from_=0.2, to=0.9, number_of_steps=14,
            button_color=ACENTO, progress_color=ACENTO,
            command=lambda v: self.lbl_dens.configure(
                text=f"Densidad de aristas: {round(v * 100)} %"))
        self.slider_dens.set(0.45)
        self.slider_dens.pack(fill="x", pady=(4, 12))

        self.btn_generar = ctk.CTkButton(
            p, text="Generar grafo", height=42, corner_radius=10,
            font=(F, 15, "bold"), fg_color=ACENTO, hover_color=ACENTO_H,
            command=self.generar)
        self.btn_generar.pack(fill="x", padx=22, pady=(4, 0))

        # --- Paso 2: resolver ---
        self._titulo_paso(p, "2", "Encuentra la ruta óptima")

        self.btn_resolver = ctk.CTkButton(
            p, text="Calcular ruta óptima", height=42, corner_radius=10,
            font=(F, 15, "bold"), fg_color=EXITO, hover_color=EXITO_H,
            text_color="#0b1a13", command=self.calcular)
        self.btn_resolver.pack(fill="x", padx=22)

        self.progreso = ctk.CTkProgressBar(p, mode="indeterminate",
                                           progress_color=EXITO, fg_color=PANEL2)

        self.btn_animar = ctk.CTkButton(
            p, text="▶  Animar recorrido", height=38, corner_radius=10,
            font=(F, 14), fg_color="transparent", border_width=1,
            border_color=BORDE, hover_color=PANEL2, command=self.animar)
        self.btn_animar.pack(fill="x", padx=22, pady=(10, 0))

        # --- Pie ---
        pie = ctk.CTkFrame(p, fg_color="transparent")
        pie.pack(side="bottom", fill="x", padx=22, pady=20)

        fila = ctk.CTkFrame(pie, fg_color="transparent")
        fila.pack(fill="x")
        for texto, cmd in (("¿Cómo funciona?", self.abrir_guia),
                           ("Créditos", self.abrir_creditos)):
            ctk.CTkButton(fila, text=texto, height=32, fg_color=PANEL2,
                          hover_color=BORDE, font=(F, 13), corner_radius=8,
                          command=cmd).pack(side="left", expand=True, fill="x", padx=2)

        marca = ctk.CTkFrame(pie, fg_color="transparent")
        marca.pack(fill="x", pady=(14, 0))
        logo = cargar_logo(34)
        if logo:
            ctk.CTkLabel(marca, image=logo, text="").pack(side="left", padx=(0, 10))
        ctk.CTkLabel(marca, text=f"UPC · Sección {SECCION}\n{CURSO.split(' · ')[1]}",
                     font=(F, 12), text_color=SUAVE, justify="left").pack(side="left")

    def _crear_centro(self):
        c = ctk.CTkFrame(self, fg_color="transparent")
        c.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)

        self.lbl_estado = ctk.CTkLabel(c, text="Aún no hay grafo", font=(F, 20, "bold"),
                                       text_color=TEXTO)
        self.lbl_estado.pack(anchor="w")
        self.lbl_sub = ctk.CTkLabel(c, text="Elige los parámetros y presiona «Generar grafo».",
                                    font=(F, 13), text_color=SUAVE)
        self.lbl_sub.pack(anchor="w", pady=(0, 6))

        self.tabs = ctk.CTkTabview(
            c, fg_color=PANEL, corner_radius=16,
            segmented_button_fg_color=PANEL2, segmented_button_selected_color=ACENTO,
            segmented_button_selected_hover_color=ACENTO_H,
            segmented_button_unselected_color=PANEL2)
        self.tabs.pack(fill="both", expand=True)
        tab_grafo = self.tabs.add("Grafo")
        tab_matriz = self.tabs.add("Matriz de adyacencia")

        # Gráfico de matplotlib incrustado en la ventana
        self.fig = Figure(figsize=(6, 6), facecolor=PANEL)
        self.canvas = FigureCanvasTkAgg(self.fig, master=tab_grafo)
        self.canvas.get_tk_widget().configure(bg=PANEL, highlightthickness=0)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.caja_matriz = ctk.CTkTextbox(tab_matriz, font=(MONO, 14), fg_color=PANEL,
                                          text_color=TEXTO, wrap="none")
        self.caja_matriz.pack(fill="both", expand=True, padx=8, pady=8)

        # Pestaña con la lista de todos los caminos existentes
        tab_caminos = self.tabs.add("Todos los caminos")
        barra = ctk.CTkFrame(tab_caminos, fg_color="transparent")
        barra.pack(fill="x", padx=8, pady=(8, 0))
        ctk.CTkLabel(barra, text="Ver camino N°", font=(F, 13),
                     text_color=SUAVE).pack(side="left")
        self.entrada_camino = ctk.CTkEntry(barra, width=90, fg_color=PANEL2,
                                           border_color=BORDE, text_color=TEXTO)
        self.entrada_camino.pack(side="left", padx=8)
        self.entrada_camino.bind("<Return>", lambda e: self.ver_camino())
        ctk.CTkButton(barra, text="Dibujar", width=90, fg_color=ACENTO,
                      hover_color=ACENTO_H, command=self.ver_camino).pack(side="left")
        ctk.CTkButton(barra, text="Ver ruta óptima", width=130, fg_color=PANEL2,
                      hover_color=BORDE, command=self.ver_optima).pack(side="left", padx=8)

        self.caja_caminos = ctk.CTkTextbox(tab_caminos, font=(MONO, 14), fg_color=PANEL,
                                           text_color=TEXTO, wrap="none")
        self.caja_caminos.pack(fill="both", expand=True, padx=8, pady=8)
        self._texto_caminos("Calcula la ruta óptima para ver todos los caminos.")

    def _tarjeta(self, master, titulo):
        f = ctk.CTkFrame(master, fg_color=PANEL2, corner_radius=14)
        f.pack(fill="x", padx=16, pady=6)
        ctk.CTkLabel(f, text=titulo, font=(F, 12), text_color=SUAVE).pack(
            anchor="w", padx=16, pady=(12, 0))
        valor = ctk.CTkLabel(f, text="—", font=(F, 26, "bold"), text_color=TEXTO)
        valor.pack(anchor="w", padx=16, pady=(0, 12))
        return valor

    def _crear_panel_derecho(self):
        d = ctk.CTkFrame(self, width=320, fg_color=PANEL, corner_radius=0)
        d.grid(row=0, column=2, sticky="nsew")
        d.pack_propagate(False)

        ctk.CTkLabel(d, text="Resultado", font=(F, 20, "bold"),
                     text_color=TEXTO).pack(anchor="w", padx=18, pady=(26, 8))

        self.v_costo = self._tarjeta(d, "Costo mínimo")
        self.v_ciclos = self._tarjeta(d, "Ciclos hamiltonianos existentes")
        self.v_tiempo = self._tarjeta(d, "Tiempo de cálculo (fuerza bruta)")

        ctk.CTkLabel(d, text="Recorrido paso a paso", font=(F, 13),
                     text_color=SUAVE).pack(anchor="w", padx=18, pady=(12, 4))
        self.caja_ruta = ctk.CTkTextbox(d, font=(MONO, 14), fg_color=PANEL2,
                                        text_color=TEXTO, corner_radius=14)
        self.caja_ruta.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self._texto_ruta("La ruta aparecerá aquí.")

    # ------------------------------------------------------------------
    #  Acciones
    # ------------------------------------------------------------------
    def _cambiar_modo(self, modo):
        if modo == "Parcial":
            self.frame_dens.pack(fill="x", padx=22, before=self.btn_generar)
        else:
            self.frame_dens.pack_forget()
        self.btn_generar.configure(
            text="Escribir conexiones…" if modo == "Manual" else "Generar grafo")

    def generar(self):
        self._detener_animacion()
        n = int(self.slider_nodos.get())
        modo = self.modo.get()
        if modo == "Manual":
            VentanaManual(self, n, self._usar_grafo)
            return
        G = grafo_aleatorio(n, completo=(modo == "Completo"),
                            densidad=self.slider_dens.get())
        self._usar_grafo(G)

    def _usar_grafo(self, G):
        """Reemplaza el grafo actual (antes se acumulaban aristas viejas)."""
        self.G = G
        self.pos = nx.circular_layout(G)
        self.resultado = None
        n, m = G.number_of_nodes(), G.number_of_edges()
        self.lbl_estado.configure(text=f"Grafo de {n} nodos y {m} aristas")
        self.lbl_sub.configure(text="Nodo verde = punto de partida (0).  "
                                    "Ahora presiona «Calcular ruta óptima».")
        for v in (self.v_costo, self.v_ciclos, self.v_tiempo):
            v.configure(text="—", text_color=TEXTO)
        self._texto_ruta("Presiona «Calcular ruta óptima».")
        self._texto_caminos("Calcula la ruta óptima para ver todos los caminos.")
        self._dibujar()
        self._actualizar_matriz()
        self.tabs.set("Grafo")

    def calcular(self):
        if self.G is None:
            messagebox.showwarning("Falta el grafo", "Primero genera un grafo.")
            return
        self._detener_animacion()

        problema = diagnostico(self.G)
        if problema:
            self.v_costo.configure(text="Sin ruta", text_color=RUTA)
            self.v_ciclos.configure(text="0")
            self._texto_ruta("No existe ciclo hamiltoniano.\n\n" + problema)
            self._texto_caminos("No existe ningún camino.\n\n" + problema)
            return

        # El cálculo corre en segundo plano para que la ventana no se congele
        self.btn_resolver.configure(state="disabled", text="Calculando…")
        self.btn_generar.configure(state="disabled")
        self.progreso.pack(fill="x", padx=22, pady=(8, 0), after=self.btn_resolver)
        self.progreso.start()

        M = matriz_adyacencia(self.G)
        self._trabajo = {"listo": False}

        def tarea():
            # 1) Fuerza bruta: da la ruta óptima y todos los caminos
            t0 = time.perf_counter()
            self._trabajo["res"] = fuerza_bruta(M)
            self._trabajo["seg"] = time.perf_counter() - t0
            # 2) Held-Karp: solo para comparar costo y tiempo
            t0 = time.perf_counter()
            self._trabajo["hk"] = held_karp(M)
            self._trabajo["seg_hk"] = time.perf_counter() - t0
            self._trabajo["listo"] = True

        threading.Thread(target=tarea, daemon=True).start()
        self.after(100, self._esperar_resultado)

    def _esperar_resultado(self):
        if not self._trabajo["listo"]:
            self.after(100, self._esperar_resultado)
            return
        self.progreso.stop()
        self.progreso.pack_forget()
        self.btn_resolver.configure(state="normal", text="Calcular ruta óptima")
        self.btn_generar.configure(state="normal")
        w = self._trabajo
        self._mostrar_resultado(w["res"], w["seg"], w["hk"], w["seg_hk"])

    def _mostrar_resultado(self, r, segundos, hk=None, segundos_hk=0.0):
        self.v_tiempo.configure(text=f"{segundos:.3f} s")
        if r is None:
            self.v_costo.configure(text="Sin ruta", text_color=RUTA)
            self.v_ciclos.configure(text="0")
            self._texto_ruta("No existe ningún ciclo que pase por todos "
                             "los nodos una sola vez.")
            self._texto_caminos("No existe ningún camino que pase por todos "
                                "los nodos una sola vez.")
            return

        self.resultado = r
        self.v_costo.configure(text=fmt(r["costo"]), text_color=EXITO)
        self.v_ciclos.configure(text=fmt(r["ciclos"]))

        ruta = r["ruta"]
        n = self.G.number_of_nodes()
        lineas = ["TRAMO          COSTO", "─" * 21]
        for a, b in zip(ruta, ruta[1:]):
            lineas.append(f"{a:>2} → {b:<2}  {self.G[a][b]['weight']:>10}")
        lineas += ["─" * 21, f"{'TOTAL':<8}{r['costo']:>13}", "",
                   "Ruta:", " → ".join(map(str, ruta)), "",
                   "FUERZA BRUTA",
                   f"(n−1)! rutas:    {fmt(math.factorial(n - 1))}",
                   f"Evaluadas /2:    {fmt(r['evaluadas'])}",
                   f"Caminos válidos: {fmt(r['ciclos'])}",
                   f"Costo mínimo:    {fmt(r['costo'])}",
                   f"Tiempo:          {segundos:.3f} s"]
        # Comparación con Held-Karp: ambos deben dar el mismo costo mínimo
        if hk:
            igual = "✔ Mismo costo mínimo" if hk["costo"] == r["costo"] else "✘ Costos distintos"
            lineas += ["", "HELD-KARP (comparación)",
                       f"≈ n²·2ⁿ pasos:   {fmt(n * n * 2 ** n)}",
                       f"Ciclos:          {fmt(hk['ciclos'])}",
                       f"Costo mínimo:    {fmt(hk['costo'])}",
                       f"Tiempo:          {segundos_hk:.3f} s",
                       "", igual]
        self._texto_ruta("\n".join(lineas))
        self._llenar_caminos(r)

        self._dibujar(ruta)
        self._actualizar_matriz(ruta)
        self.tabs.set("Grafo")

    def _llenar_caminos(self, r):
        """Escribe en la pestaña «Todos los caminos» cada camino con su
        etiqueta (C1, C2, ...), su costo y su recorrido. ★ = ruta óptima."""
        n = self.G.number_of_nodes()
        ancho = len(str(len(r["caminos"]))) + 1
        cab = [f"Fuerza bruta: se evaluaron {fmt(r['evaluadas'])} rutas "
               f"de {n} nodos y existen {fmt(r['ciclos'])} caminos.",
               "★ = ruta óptima (menor costo)", "",
               f"{'N°':<{ancho + 3}}{'COSTO':>7}   RECORRIDO",
               "─" * (ancho + 16 + 5 * n)]
        filas, optimas = [], []    # optimas = líneas que se pintan de verde
        for i, c in enumerate(r["caminos"], start=1):
            marca = "★" if c["costo"] == r["costo"] else " "
            if marca == "★":
                optimas.append(len(cab) + i)
            filas.append(f"{'C' + str(i):<{ancho + 1}}{marca} {c['costo']:>7}   "
                         + " → ".join(map(str, c["ruta"])))
        self._texto_caminos("\n".join(cab + filas), optimas)

    def ver_camino(self):
        """Dibuja en el grafo el camino cuyo número se escribió (ej. 5 o C5)."""
        if not self.resultado:
            messagebox.showinfo("Sin caminos", "Primero calcula la ruta óptima.")
            return
        total = len(self.resultado["caminos"])
        texto = self.entrada_camino.get().strip().upper().lstrip("C")
        if not texto.isdigit() or not 1 <= int(texto) <= total:
            messagebox.showerror("Número inválido",
                                 f"Escribe un número de camino entre 1 y {total}.")
            return
        k = int(texto)
        c = self.resultado["caminos"][k - 1]
        self._detener_animacion()
        self._dibujar(c["ruta"])
        self._actualizar_matriz(c["ruta"])
        extra = "  (es la ruta óptima)" if c["costo"] == self.resultado["costo"] else ""
        self.lbl_sub.configure(text=f"Mostrando camino C{k}: "
                                    f"{' → '.join(map(str, c['ruta']))}  ·  "
                                    f"costo {c['costo']}{extra}")
        self.tabs.set("Grafo")

    def ver_optima(self):
        """Vuelve a dibujar la ruta óptima."""
        if not self.resultado:
            messagebox.showinfo("Sin caminos", "Primero calcula la ruta óptima.")
            return
        self._detener_animacion()
        ruta = self.resultado["ruta"]
        self._dibujar(ruta)
        self._actualizar_matriz(ruta)
        self.lbl_sub.configure(text=f"Ruta óptima: {' → '.join(map(str, ruta))}  ·  "
                                    f"costo {self.resultado['costo']}")
        self.tabs.set("Grafo")

    def animar(self):
        if not self.resultado:
            messagebox.showinfo("Sin ruta", "Primero calcula la ruta óptima.")
            return
        self._detener_animacion()
        ruta = self.resultado["ruta"]
        self.tabs.set("Grafo")

        def paso(i):
            self._dibujar(ruta[:i + 1])
            if i < len(ruta) - 1:
                self._animando = self.after(550, lambda: paso(i + 1))
            else:
                self._animando = None

        paso(0)

    def _detener_animacion(self):
        if self._animando:
            self.after_cancel(self._animando)
            self._animando = None

    # ------------------------------------------------------------------
    #  Dibujo
    # ------------------------------------------------------------------
    def _dibujar(self, ruta=None):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(PANEL)
        ax.axis("off")
        self.fig.subplots_adjust(0, 0, 1, 1)

        if self.G is None:
            ax.text(0.5, 0.5, "Genera un grafo para empezar", ha="center", va="center",
                    color=SUAVE, fontsize=14, transform=ax.transAxes)
            self.canvas.draw_idle()
            return

        G, pos = self.G, self.pos
        tramos = list(zip(ruta, ruta[1:])) if ruta else []
        en_ruta = {frozenset(t) for t in tramos}

        resto = [e for e in G.edges() if frozenset(e) not in en_ruta]
        nx.draw_networkx_edges(G, pos, edgelist=resto, edge_color=ARISTA,
                               width=1, alpha=0.25 if ruta else 0.7, ax=ax)
        if tramos:
            nx.draw_networkx_edges(G, pos, edgelist=tramos, edge_color=RUTA,
                                   width=3.5, ax=ax)

        colores = [EXITO if v == 0 else NODO for v in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=colores, node_size=700,
                               edgecolors=TEXTO, linewidths=1.2, ax=ax)
        nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold",
                                font_size=12, ax=ax)

        # Pesos: se muestran todos; los de la ruta seleccionada en naranja
        pesos = nx.get_edge_attributes(G, "weight")
        normales = {e: w for e, w in pesos.items() if frozenset(e) not in en_ruta}
        de_ruta = {e: w for e, w in pesos.items() if frozenset(e) in en_ruta}
        for etiquetas, color in ((normales, SUAVE if ruta else TEXTO), (de_ruta, RUTA)):
            if etiquetas:
                nx.draw_networkx_edge_labels(
                    G, pos, edge_labels=etiquetas, font_size=9, font_color=color,
                    font_weight="bold" if color == RUTA else "normal",
                    bbox=dict(boxstyle="round,pad=0.25", fc=PANEL2, ec="none"), ax=ax)

        ax.margins(0.1)
        self.canvas.draw_idle()

    def _actualizar_matriz(self, ruta=None):
        caja = self.caja_matriz
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        if self.G is None:
            caja.insert("1.0", "Aún no hay grafo.")
            caja.configure(state="disabled")
            return

        M = matriz_adyacencia(self.G)
        n = len(M)
        lineas = ["    │" + "".join(f"{j:>4}" for j in range(n)),
                  "────┼" + "────" * n]
        for i in range(n):
            lineas.append(f"{i:>3} │" + "".join(
                f"{(M[i][j] if M[i][j] else '·'):>4}" for j in range(n)))
        pie = "\n\n· = no hay conexión directa entre esos nodos"
        if ruta:
            pie += "\nEn naranja: aristas usadas por la ruta óptima"
        caja.insert("1.0", "\n".join(lineas) + pie)

        if ruta:  # resaltar celdas de la ruta (fila i está en la línea i+3)
            for a, b in zip(ruta, ruta[1:]):
                for i, j in ((a, b), (b, a)):
                    caja.tag_add("ruta", f"{i + 3}.{5 + 4 * j}", f"{i + 3}.{9 + 4 * j}")
            caja.tag_config("ruta", foreground=RUTA)
        caja.configure(state="disabled")

    def _texto_ruta(self, texto):
        self.caja_ruta.configure(state="normal")
        self.caja_ruta.delete("1.0", "end")
        self.caja_ruta.insert("1.0", texto)
        self.caja_ruta.configure(state="disabled")

    def _texto_caminos(self, texto, resaltar=()):
        """Reemplaza el texto de la pestaña de caminos y pinta de verde
        las líneas indicadas (las rutas óptimas)."""
        caja = self.caja_caminos
        caja.configure(state="normal")
        caja.delete("1.0", "end")
        caja.insert("1.0", texto)
        for linea in resaltar:
            caja.tag_add("optima", f"{linea}.0", f"{linea}.end")
        caja.tag_config("optima", foreground=EXITO)
        caja.configure(state="disabled")

    # ------------------------------------------------------------------
    #  Ventanas informativas
    # ------------------------------------------------------------------
    def _ventana_info(self, titulo, texto, alto=480):
        v = ctk.CTkToplevel(self)
        v.title(titulo)
        v.geometry(f"580x{alto}")
        v.configure(fg_color=BG)
        v.transient(self)
        v.after(150, v.lift)
        ctk.CTkLabel(v, text=titulo, font=(F, 22, "bold"),
                     text_color=TEXTO).pack(anchor="w", padx=24, pady=(20, 8))
        caja = ctk.CTkTextbox(v, fg_color=PANEL, text_color=TEXTO, font=(F, 14),
                              wrap="word", corner_radius=12)
        caja.pack(fill="both", expand=True, padx=24)
        caja.insert("1.0", texto)
        caja.configure(state="disabled")
        ctk.CTkButton(v, text="Cerrar", fg_color=ACENTO, hover_color=ACENTO_H,
                      corner_radius=10, command=v.destroy).pack(pady=18)

    def abrir_guia(self):
        self._ventana_info("¿Cómo funciona?", (
            "EL PROBLEMA\n"
            "Un agente debe salir de una ciudad (nodo 0), visitar todas las demás "
            "exactamente una vez y regresar, gastando lo menos posible. Esa ruta es "
            "un ciclo hamiltoniano de costo mínimo.\n\n"
            "PASOS\n"
            f"1. Elige la cantidad de nodos ({MIN_NODOS} a {MAX_NODOS}).\n"
            "2. Elige el tipo de grafo:\n"
            "   • Completo: todos los nodos conectados entre sí.\n"
            "   • Parcial: conexiones al azar según la densidad.\n"
            "   • Manual: escribes cada conexión (origen destino costo).\n"
            "3. Presiona «Calcular ruta óptima».\n"
            "4. En la pestaña «Todos los caminos» verás cada camino existente "
            "con su etiqueta (C1, C2, …), su recorrido y su costo. Escribe un "
            "número y presiona «Dibujar» para verlo en el grafo.\n"
            "5. Usa «Animar recorrido» para ver la ruta óptima paso a paso.\n\n"
            "EL ALGORITMO: FUERZA BRUTA\n"
            "Se fija el nodo 0 como inicio y se generan todas las permutaciones "
            "de los demás nodos: (n−1)! rutas. Como recorrer un ciclo en un "
            "sentido o en el otro cuesta lo mismo, solo se evalúa uno de los dos, "
            "así que se revisan (n−1)!/2 rutas. Para cada una se suman los costos "
            "de sus tramos; si algún tramo no existe en el grafo, la ruta se "
            "descarta. Al final se guardan todos los caminos válidos y se elige "
            "el de menor costo. Es exacto, pero crece muy rápido: con 10 nodos "
            "ya son 181 440 rutas.\n\n"
            "COMPARACIÓN: HELD-KARP\n"
            "El programa también resuelve con Held-Karp (programación dinámica). "
            "Guarda, para cada subconjunto de nodos visitados y cada nodo final, "
            "el menor costo encontrado y reutiliza esos resultados. Así baja a "
            "unas n²·2ⁿ operaciones. Debe dar el mismo costo mínimo que la fuerza "
            "bruta pero en menos tiempo; el panel de resultados muestra ambos.\n\n"
            "¿CUÁNDO NO HAY SOLUCIÓN?\n"
            "Si el grafo no es conexo o algún nodo tiene menos de 2 conexiones, "
            "no puede existir un ciclo hamiltoniano."), alto=700)

    def abrir_creditos(self):
        v = ctk.CTkToplevel(self)
        v.title("Créditos")
        v.geometry(f"560x{560 + 40 * len(INTEGRANTES)}")
        v.resizable(False, False)
        v.configure(fg_color=BG)
        v.transient(self)
        v.after(150, v.lift)

        # Encabezado: logo + universidad
        logo = cargar_logo(96)
        if logo:
            ctk.CTkLabel(v, image=logo, text="").pack(pady=(26, 10))
        ctk.CTkLabel(v, text=UNIVERSIDAD.upper(), font=(F, 15, "bold"),
                     text_color=TEXTO).pack(pady=(0 if logo else 26, 0))
        ctk.CTkLabel(v, text=FACULTAD, font=(F, 13),
                     text_color=SUAVE).pack()

        # Datos del curso
        datos = ctk.CTkFrame(v, fg_color=PANEL, corner_radius=14)
        datos.pack(fill="x", padx=28, pady=(18, 12))
        datos.grid_columnconfigure(1, weight=1)
        for fila, (etq, val) in enumerate((("Curso", CURSO),
                                           ("Sección", SECCION),
                                           ("Docente", DOCENTE),
                                           ("Ciclo", CICLO))):
            ctk.CTkLabel(datos, text=etq, font=(F, 13), text_color=SUAVE,
                         anchor="w").grid(row=fila, column=0, sticky="w",
                                          padx=(18, 12), pady=(12 if fila == 0 else 3,
                                                               12 if fila == 3 else 3))
            ctk.CTkLabel(datos, text=val, font=(F, 13, "bold"), text_color=TEXTO,
                         anchor="w").grid(row=fila, column=1, sticky="w",
                                          pady=(12 if fila == 0 else 3,
                                                12 if fila == 3 else 3))

        # Tabla de integrantes
        ctk.CTkLabel(v, text="INTEGRANTES", font=(F, 13, "bold"),
                     text_color=SUAVE).pack(anchor="w", padx=30, pady=(6, 6))
        tabla = ctk.CTkFrame(v, fg_color=PANEL, corner_radius=14)
        tabla.pack(fill="x", padx=28)
        tabla.grid_columnconfigure(0, weight=1)
        for col, txt in enumerate(("Nombre", "Código")):
            ctk.CTkLabel(tabla, text=txt, font=(F, 12, "bold"), text_color=ACENTO,
                         anchor="w").grid(row=0, column=col, sticky="w",
                                          padx=18, pady=(12, 4))
        for i, (nombre, codigo) in enumerate(INTEGRANTES, start=1):
            ultimo = i == len(INTEGRANTES)
            ctk.CTkLabel(tabla, text=nombre, font=(F, 14), text_color=TEXTO,
                         anchor="w").grid(row=i, column=0, sticky="w",
                                          padx=18, pady=(4, 12 if ultimo else 4))
            ctk.CTkLabel(tabla, text=codigo, font=(MONO, 13), text_color=SUAVE,
                         anchor="w").grid(row=i, column=1, sticky="w",
                                          padx=18, pady=(4, 12 if ultimo else 4))

        ctk.CTkButton(v, text="Cerrar", fg_color=ACENTO, hover_color=ACENTO_H,
                      corner_radius=10, command=v.destroy).pack(pady=20)

    def _salir(self):
        self._detener_animacion()
        self.quit()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
