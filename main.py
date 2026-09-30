"""
PROBLEMA DEL AGENTE VIAJERO (TSP)
Matemática Computacional · 1AMA0475 · UPC

Idea general del programa
-------------------------
1. Se construye un grafo no dirigido y ponderado (aleatorio o ingresado a mano).
2. Se busca el ciclo hamiltoniano de menor costo: una ruta que sale del nodo 0,
   visita cada nodo exactamente una vez y vuelve al nodo 0.
3. Para resolverlo se usa el algoritmo de Held-Karp (programación dinámica),
   que es exacto (siempre encuentra el óptimo) y mucho más rápido que probar
   todas las rutas por fuerza bruta.
"""

import math
import random
import threading
import time

import customtkinter as ctk
from tkinter import messagebox
import networkx as nx
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =====================================================================
#  DATOS DEL PROYECTO
# =====================================================================
CURSO = "Matemática Computacional · 1AMA0475"
UNIVERSIDAD = "Universidad Peruana de Ciencias Aplicadas"
INTEGRANTES = ["Coras Zelada, Bruno Enrique"]
CICLO = "2026-02"

MIN_NODOS, MAX_NODOS = 8, 16
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


def resolver_tsp(M):
    """
    Algoritmo de Held-Karp (programación dinámica con máscaras de bits).

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
        self.resultado = None    # respuesta de resolver_tsp
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

        self.lbl_nodos = ctk.CTkLabel(p, text="Cantidad de nodos: 10",
                                      font=(F, 13), text_color=SUAVE)
        self.lbl_nodos.pack(anchor="w", padx=22)
        self.slider_nodos = ctk.CTkSlider(
            p, from_=MIN_NODOS, to=MAX_NODOS, number_of_steps=MAX_NODOS - MIN_NODOS,
            button_color=ACENTO, progress_color=ACENTO,
            command=lambda v: self.lbl_nodos.configure(text=f"Cantidad de nodos: {int(v)}"))
        self.slider_nodos.set(10)
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
        ctk.CTkLabel(pie, text=INTEGRANTES[0], font=(F, 12),
                     text_color=SUAVE).pack(anchor="w", pady=(10, 0))
        fila = ctk.CTkFrame(pie, fg_color="transparent")
        fila.pack(fill="x", before=pie.winfo_children()[0])
        for texto, cmd in (("¿Cómo funciona?", self.abrir_guia),
                           ("Créditos", self.abrir_creditos)):
            ctk.CTkButton(fila, text=texto, height=32, fg_color=PANEL2,
                          hover_color=BORDE, font=(F, 13), corner_radius=8,
                          command=cmd).pack(side="left", expand=True, fill="x", padx=2)

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
        self.v_tiempo = self._tarjeta(d, "Tiempo de cálculo")

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
            return

        # El cálculo corre en segundo plano para que la ventana no se congele
        self.btn_resolver.configure(state="disabled", text="Calculando…")
        self.btn_generar.configure(state="disabled")
        self.progreso.pack(fill="x", padx=22, pady=(8, 0), after=self.btn_resolver)
        self.progreso.start()

        M = matriz_adyacencia(self.G)
        self._trabajo = {"listo": False}

        def tarea():
            t0 = time.perf_counter()
            self._trabajo["res"] = resolver_tsp(M)
            self._trabajo["seg"] = time.perf_counter() - t0
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
        self._mostrar_resultado(self._trabajo["res"], self._trabajo["seg"])

    def _mostrar_resultado(self, r, segundos):
        self.v_tiempo.configure(text=f"{segundos:.2f} s")
        if r is None:
            self.v_costo.configure(text="Sin ruta", text_color=RUTA)
            self.v_ciclos.configure(text="0")
            self._texto_ruta("No existe ningún ciclo que pase por todos "
                             "los nodos una sola vez.")
            return

        self.resultado = r
        self.v_costo.configure(text=fmt(r["costo"]), text_color=EXITO)
        self.v_ciclos.configure(text=fmt(r["ciclos"]))

        ruta = r["ruta"]
        n = len(ruta) - 1
        lineas = ["TRAMO          COSTO", "─" * 21]
        for a, b in zip(ruta, ruta[1:]):
            lineas.append(f"{a:>2} → {b:<2}  {self.G[a][b]['weight']:>10}")
        lineas += ["─" * 21, f"{'TOTAL':<8}{r['costo']:>13}", "",
                   "Ruta:", " → ".join(map(str, ruta)), "",
                   "¿Por qué Held-Karp?",
                   f"Fuerza bruta: {fmt(math.factorial(n - 1) // 2)} rutas",
                   f"Held-Karp: ≈ {fmt(n * n * 2 ** n)} pasos"]
        self._texto_ruta("\n".join(lineas))

        self._dibujar(ruta)
        self._actualizar_matriz(ruta)
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

        # Pesos: si hay ruta, solo los de la ruta; si no, todos (si no saturan)
        pesos = nx.get_edge_attributes(G, "weight")
        if ruta:
            etiquetas = {e: w for e, w in pesos.items() if frozenset(e) in en_ruta}
        elif G.number_of_edges() <= 45:
            etiquetas = pesos
        else:
            etiquetas = {}
            ax.text(0.5, 0.01, "Hay muchas aristas: revisa los pesos en la pestaña "
                    "«Matriz de adyacencia».", ha="center", color=SUAVE,
                    fontsize=10, transform=ax.transAxes)
        if etiquetas:
            nx.draw_networkx_edge_labels(
                G, pos, edge_labels=etiquetas, font_size=9, font_color=TEXTO,
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
            "1. Elige la cantidad de nodos (8 a 16).\n"
            "2. Elige el tipo de grafo:\n"
            "   • Completo: todos los nodos conectados entre sí.\n"
            "   • Parcial: conexiones al azar según la densidad.\n"
            "   • Manual: escribes cada conexión (origen destino costo).\n"
            "3. Presiona «Calcular ruta óptima».\n"
            "4. Usa «Animar recorrido» para ver la ruta paso a paso.\n\n"
            "EL ALGORITMO: HELD-KARP\n"
            "Probar todas las rutas (fuerza bruta) cuesta (n−1)!/2: con 16 nodos "
            "son más de 650 mil millones de rutas. Held-Karp guarda, para cada "
            "subconjunto de nodos visitados y cada nodo final, el menor costo "
            "encontrado, y reutiliza esos resultados (programación dinámica). "
            "Así baja a unas n²·2ⁿ operaciones y resuelve 16 nodos en segundos, "
            "sin dejar de ser exacto.\n\n"
            "¿CUÁNDO NO HAY SOLUCIÓN?\n"
            "Si el grafo no es conexo o algún nodo tiene menos de 2 conexiones, "
            "no puede existir un ciclo hamiltoniano."), alto=620)

    def abrir_creditos(self):
        self._ventana_info("Créditos", (
            f"Proyecto desarrollado para el curso\n{CURSO}\n\n"
            f"{UNIVERSIDAD}\n\n"
            "Integrante:\n" + "\n".join(f"• {x}" for x in INTEGRANTES) +
            f"\n\nCiclo {CICLO}"), alto=380)

    def _salir(self):
        self._detener_animacion()
        self.quit()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
