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

- Grafos de 3 a 9 nodos (arranca en 5): **completos**, **parciales** (densidad ajustable) o **manuales**.
- Visualización del grafo (con el peso de todas sus aristas) y de su **matriz de adyacencia**.
- Cálculo exacto de la ruta óptima con el algoritmo de **fuerza bruta**.
- Pestaña **Todos los caminos**: lista cada camino existente con su etiqueta (C1, C2, …), su costo, su recorrido, su inverso y la suma de sus tramos, y marca la ruta óptima con ★. Se muestra por páginas de 500.
- Dibujar cualquier camino de la lista en el grafo escribiendo su número.
- Animación del recorrido óptimo paso a paso.
- Diagnóstico cuando no existe solución (grafo no conexo o nodos con grado < 2).

## Algoritmo: fuerza bruta

Se parte del nodo 0 y se prueban **todas las opciones de recorrido** (búsqueda exhaustiva con retroceso), sin generar permutaciones:

1. Desde el nodo actual se avanza a cada vecino que aún no se visitó, sumando el costo de la arista.
2. Cuando ya se pasó por los `n` nodos y existe la arista de regreso al 0, se cierra el ciclo y se guarda como un camino existente.
3. Se retrocede un paso y se prueba el siguiente vecino, hasta agotar todas las posibilidades.
4. La ruta óptima es el camino de menor costo.

Como solo se avanza por aristas que existen, nunca se arma una ruta imposible. Cada ciclo aparece dos veces (en un sentido y al revés) con el mismo costo; la lista indica cuál es el inverso de cada camino.

En un grafo completo hay `(n−1)!` caminos; en uno parcial, menos.

| Nodos | Caminos en un grafo completo `(n−1)!` |
|---|---|
| 3 | 2 |
| 4 | 6 |
| 5 | 24 |
| 6 | 120 |
| 7 | 720 |
| 8 | 5 040 |
| 9 | 40 320 |

Complejidad: **O(n!)**.

## Instalación y uso

```bash
pip install -r requirements.txt
python main.py
```

1. Elige la cantidad de nodos y el tipo de grafo.
2. Presiona **Generar grafo**.
3. Presiona **Calcular ruta óptima**.
4. Revisa la pestaña **Todos los caminos** (usa ◀ ▶ para cambiar de página) y dibuja el que quieras.
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