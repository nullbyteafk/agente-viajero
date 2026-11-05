# Problema del Agente Viajero (TSP)

Aplicación de escritorio en Python que encuentra la **ruta de menor costo** que sale de un nodo, visita todos los demás exactamente una vez y regresa al inicio (**ciclo hamiltoniano mínimo**).

<p align="center"><img src="assets/upc_logo.png" width="90" alt="Logo UPC"></p>

| | |
|---|---|
| **Universidad** | Universidad Peruana de Ciencias Aplicadas (UPC) |
| **Facultad** | Facultad de Ingeniería |
| **Curso** | 1AMA0475 · Matemática Computacional |
| **Sección** | 2911 |
| **Docente** | Mattos Quevedo, Juan Manuel |
| **Ciclo** | 2026-02 |

## Funcionalidades

- Grafos de 5 a 10 nodos: **completos**, **parciales** (densidad ajustable) o **manuales**.
- Visualización del grafo (con el peso de todas sus aristas) y de su **matriz de adyacencia**.
- Cálculo exacto de la ruta óptima con el algoritmo de **fuerza bruta**.
- Comparación con **Held-Karp**: el programa muestra que ambos dan el mismo costo mínimo y cuánto tardó cada uno.
- Pestaña **Todos los caminos**: lista cada ciclo hamiltoniano existente con su etiqueta (C1, C2, …), su recorrido y su costo, y marca la ruta óptima con ★.
- Dibujar cualquier camino de la lista en el grafo escribiendo su número.
- Animación del recorrido óptimo paso a paso.
- Diagnóstico cuando no existe solución (grafo no conexo o nodos con grado < 2).

## Algoritmo

Se fija el nodo 0 como punto de partida y se generan **todas las permutaciones** de los demás nodos con `itertools.permutations`, es decir `(n−1)!` rutas.

Cada ciclo se puede recorrer en dos sentidos con el mismo costo (`0→1→2→0` y `0→2→1→0`), así que solo se evalúa una de las dos versiones y se revisan `(n−1)!/2` rutas.

Para cada ruta se suman los costos de sus tramos; si algún tramo no existe en el grafo, la ruta se descarta. Todas las rutas válidas se guardan como caminos existentes y al final se elige la de menor costo.

| Nodos | Rutas evaluadas `(n−1)!/2` |
|---|---|
| 5 | 12 |
| 6 | 60 |
| 7 | 360 |
| 8 | 2 520 |
| 9 | 20 160 |
| 10 | 181 440 |

### Comparación con Held-Karp

El programa también resuelve el mismo grafo con **Held-Karp** (programación dinámica con máscaras de bits):

```
dp[S][j] = costo mínimo de un camino que sale de 0,
           visita exactamente los nodos del conjunto S
           y termina en el nodo j
```

Su complejidad es **O(n² · 2ⁿ)**, frente a **O(n!)** de la fuerza bruta. Ambos son exactos y dan el mismo costo mínimo, pero Held-Karp no revisa las rutas una por una, por eso la lista de todos los caminos sale de la fuerza bruta.

## Instalación y uso

```bash
pip install -r requirements.txt
python main.py
```

1. Elige la cantidad de nodos y el tipo de grafo.
2. Presiona **Generar grafo**.
3. Presiona **Calcular ruta óptima**.
4. Revisa la pestaña **Todos los caminos** y dibuja el que quieras.
5. Opcional: **Animar recorrido**.

En el modo manual, las conexiones se escriben una por línea con el formato `origen destino costo` (por ejemplo `0 3 25`).

## Integrantes

| Nombre | Código |
|---|---|
| Coras Zelada, Bruno Enrique | u202424853 |
| Condori Ramos, Aldo | u202419673 |
| Lopez Atencia, Jhonatan Ismael | u202416648 |
| Romero Pasache, Rolando Miguel | u202313521 |
| Lorenzo Nicolas, Luana Suhey | u202414362 |