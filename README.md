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

- Grafos de 3 a 16 nodos (arranca en 5), con nodos nombrados por letras (A, B, C…): **completos**, **parciales** (densidad ajustable) o **manuales**.
- Botón **Cargar ejemplo de clase**: el grafo de 5 nodos resuelto en clase.
- Visualización del grafo (con el peso de todas sus aristas) y de su **matriz de adyacencia**.
- Cálculo exacto de la ruta óptima con el algoritmo de **fuerza bruta**.
- Pestaña **Todos los caminos**: tabla con cada camino (C1, C2, …), sus vértices V1…V(n+1), sus pesos P1…Pn y su total; la ruta óptima se marca con ✓ y se escribe al final (por ejemplo `ADCBEA = 38`). Se muestra por páginas de 500.
- Dibujar cualquier camino de la tabla en el grafo escribiendo su número.
- Animación del recorrido óptimo paso a paso.
- Diagnóstico cuando no existe solución (grafo no conexo o nodos con grado < 2).

## Algoritmo: fuerza bruta

Se parte del nodo A y se prueban **todas las opciones de recorrido** (búsqueda exhaustiva con retroceso), sin generar permutaciones:

1. Desde el nodo actual se avanza a cada vecino que aún no se visitó, sumando el costo de la arista.
2. Cuando ya se pasó por los `n` nodos y existe la arista de regreso a A, se cierra el ciclo.
3. Se retrocede un paso y se prueba el siguiente vecino, hasta agotar todas las posibilidades.
4. La ruta óptima es el camino de menor costo.

Cada ciclo aparece dos veces, en un sentido y al revés, con el mismo costo (`ABCDEA` = `AEDCBA`). Solo se anota uno: aquel cuyo 2.º vértice va antes en el alfabeto que el penúltimo. Por eso en un grafo completo quedan **`(n−1)!/2`** caminos.

| Nodos | Caminos `(n−1)!/2` |
|---|---|
| 3 | 1 |
| 4 | 3 |
| 5 | 12 |
| 6 | 60 |
| 7 | 360 |
| 8 | 2 520 |
| 9 | 20 160 |
| 10 | 181 440 |
| 11 | 1 814 400 |
| 12 | 19 958 400 |
| 13 | 239 500 800 |
| 14 | 3 113 510 400 |
| 15 | 43 589 145 600 |
| 16 | 653 837 184 000 |

Complejidad: **O(n!)**.

En un grafo completo la búsqueda termina en segundos hasta unos 10–11 nodos. Si pasa de **60 segundos** se detiene y el programa muestra cuántos caminos revisó, cuánto tardaría en revisarlos todos (con 16 nodos, días o semanas) y el mejor camino hallado hasta ese momento. La tabla guarda hasta 200 000 caminos; la ruta óptima siempre considera todos.

### Ejemplo de clase (5 nodos)

Aristas: AB 10, AC 18, AD 9, AE 6, BC 3, BD 15, BE 4, CD 16, CE 14, DE 5.

`(5−1)!/2 = 24/2 = 12` caminos. La ruta óptima es **`ADCBEA = 9 + 16 + 3 + 4 + 6 = 38`**.

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

En el modo manual, las conexiones se escriben una por línea con el formato `origen destino costo` (por ejemplo `A D 25`).

## Integrantes

| Nombre | Código |
|---|---|
| Coras Zelada, Bruno Enrique | u202424853 |
| Condori Ramos, Aldo | u202419673 |
| Lopez Atencia, Jhonatan Ismael | u202416648 |
| Romero Pasache, Rolando Miguel | u202313521 |
| Lorenzo Nicolas, Luana Suhey | u202414362 |