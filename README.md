# Problema del Agente Viajero (TSP)

Aplicación de escritorio en Python que encuentra la **ruta de menor costo** que sale de un nodo, visita todos los demás exactamente una vez y regresa al inicio (**ciclo hamiltoniano mínimo**).

Proyecto del curso **Matemática Computacional (1AMA0475)**, Universidad Peruana de Ciencias Aplicadas, ciclo 2026-02.

## Funcionalidades

- Grafos de 8 a 16 nodos: **completos**, **parciales** (densidad ajustable) o **manuales**.
- Visualización del grafo y de su **matriz de adyacencia**.
- Cálculo exacto de la ruta óptima con el algoritmo de **Held-Karp**.
- Conteo total de ciclos hamiltonianos existentes.
- Animación del recorrido paso a paso.
- Diagnóstico cuando no existe solución (grafo no conexo o nodos con grado < 2).

## Algoritmo

Probar todas las rutas (fuerza bruta) requiere revisar `(n−1)!/2` ciclos: con 16 nodos son **653 837 184 000**.

Held-Karp usa **programación dinámica con máscaras de bits**:

```
dp[S][j] = costo mínimo de un camino que sale de 0,
           visita exactamente los nodos del conjunto S
           y termina en el nodo j
```

Así la complejidad baja a **O(n² · 2ⁿ)** (≈ 16,8 millones de pasos con 16 nodos) y el resultado sigue siendo el óptimo exacto.

## Instalación y uso

```bash
pip install -r requirements.txt
python main.py
```

1. Elige la cantidad de nodos y el tipo de grafo.
2. Presiona **Generar grafo**.
3. Presiona **Calcular ruta óptima**.
4. Opcional: **Animar recorrido**.

En el modo manual, las conexiones se escriben una por línea con el formato `origen destino costo` (por ejemplo `0 3 25`).

## Autor

- Coras Zelada, Bruno Enrique
