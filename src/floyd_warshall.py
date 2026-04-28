# src/floyd_warshall.py
import copy

# ============================================================
# NODOS DEL MAPA (para depuración y trazabilidad)
# ============================================================
NOMBRES_NODOS = {
    0: "Almacén",
    1: "Cervantes",
    2: "Estación",
    3: "Campus",
    4: "Magna",
    5: "Ensanche",
    6: "Chorrillo",
    7: "Reyes Católicos",
    8: "Nueva Alcalá",
    9: "Cuatro Caños",
    10: "Hospital",
}


def floyd_warshall(matriz):
    """
    Implementa el algoritmo de Floyd-Warshall para calcular los caminos
    mínimos entre TODOS los pares de nodos de un grafo dirigido y ponderado.

    Transforma una matriz de adyacencia (posiblemente incompleta, con inf)
    en una matriz de costes mínimos reales, utilizando nodos intermedios.

    Complejidad temporal: O(n³)
    Complejidad espacial: O(n²)

    ENTRADAS:
        matriz : list[list[float]]
            Matriz de adyacencia n×n (o n×m con m >= n).
            float('inf') indica que no existe conexión directa entre dos nodos.
            Se asume que la diagonal principal es 0.

    SALIDAS:
        dist : list[list[float]]
            Matriz n×n con el coste mínimo entre cada par de nodos.
            dist[i][j] == float('inf') indica que j no es alcanzable desde i.
        pred : list[list[int | None]]
            Matriz n×n de predecesores.
            pred[i][j] = nodo anterior a j en el camino mínimo desde i.
            pred[i][j] = None si no hay camino o si i == j.
    """
    n = len(matriz)

    # ----------------------------------------------------------
    # 1. INICIALIZACIÓN
    #    Truncar a n×n para garantizar una matriz cuadrada,
    #    independientemente de si la original tiene columnas extra.
    # ----------------------------------------------------------
    dist = [[matriz[i][j] if j < len(matriz[i]) else float('inf')
             for j in range(n)]
            for i in range(n)]

    #pred[i][j] = predecesor inmediato de j en el camino i→j
    pred = [[None] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                pred[i][j] = i  # Conexión directa: el predecesor de j es i

    # ----------------------------------------------------------
    # 2. NÚCLEO DEL ALGORITMO
    #    Para cada nodo intermedio k, comprueba si ir de i a j
    #    pasando por k mejora el coste.
    # ----------------------------------------------------------
    for k in range(n):
        for i in range(n):
            # Optimización: si i no puede alcanzar k, ningún j mejorará
            if dist[i][k] == float('inf'):
                continue
            for j in range(n):
                nuevo_coste = dist[i][k] + dist[k][j]
                if nuevo_coste < dist[i][j]:
                    dist[i][j] = nuevo_coste
                    # El predecesor de j en el camino i→j es el mismo que en k→j
                    pred[i][j] = pred[k][j]

    return dist, pred


def reconstruir_camino(pred, origen, destino):
    """
    Reconstruye el camino mínimo entre dos nodos a partir de la
    matriz de predecesores generada por floyd_warshall().

    ENTRADAS:
        pred    : list[list[int | None]]  — matriz de predecesores.
        origen  : int                     — índice del nodo de partida.
        destino : int                     — índice del nodo de llegada.

    SALIDAS:
        list[int]
            Lista de índices que forman el camino mínimo, incluyendo
            tanto el nodo de origen como el de destino.
            Lista vacía si no existe ningún camino.
    """
    if origen == destino:
        return [origen]

    if pred[origen][destino] is None:
        return []  # No hay camino posible

    camino = []
    nodo = destino

    # Recorrer hacia atrás usando los predecesores
    while nodo != origen:
        camino.append(nodo)
        anterior = pred[origen][nodo]
        if anterior is None:
            return []  # Camino roto (no debería ocurrir en un grafo consistente)
        nodo = anterior

    camino.append(origen)
    camino.reverse()
    return camino


def expandir_ruta_completa(ruta_tsp, pred):
    """
    Expande una ruta TSP (lista de nodos clave) a su trayecto real completo,
    insertando todos los nodos intermedios calculados por Floyd-Warshall.

    Por ejemplo, si el TSP devuelve [0, 3, 9, 0] pero para ir de 0 a 3
    Floyd-Warshall determinó que el camino óptimo pasa por [0, 2, 3],
    la ruta expandida será [0, 2, 3, 9, 0].

    ENTRADAS:
        ruta_tsp : list[int]              — nodos clave devueltos por el TSP.
        pred     : list[list[int | None]] — matriz de predecesores.

    SALIDAS:
        list[int]
            Secuencia completa de nodos (sin repeticiones en las uniones
            entre tramos consecutivos).
            Devuelve una copia de ruta_tsp si algún tramo no puede expandirse.
    """
    if len(ruta_tsp) < 2:
        return ruta_tsp[:]

    ruta_expandida = []

    for i in range(len(ruta_tsp) - 1):
        origen_tramo  = ruta_tsp[i]
        destino_tramo = ruta_tsp[i + 1]
        tramo = reconstruir_camino(pred, origen_tramo, destino_tramo)

        if not tramo:
            # Tramo no reconstruible: devolvemos la ruta sin expandir
            return ruta_tsp[:]

        # Añadir todos los nodos del tramo excepto el último,
        # para evitar duplicar el nodo de unión con el siguiente tramo
        ruta_expandida.extend(tramo[:-1])

    # Añadir el nodo final de la ruta completa
    ruta_expandida.append(ruta_tsp[-1])

    return ruta_expandida


def nombres_ruta(ruta, nombres=NOMBRES_NODOS):
    """
    Convierte una lista de índices de nodos a sus nombres legibles.

    ENTRADAS:
        ruta   : list[int]        — lista de índices de nodos.
        nombres: dict[int, str]   — diccionario de mapeo índice → nombre.

    SALIDAS:
        list[str]  — lista de nombres de nodos en el mismo orden.
    """
    return [nombres.get(n, f"Nodo_{n}") for n in ruta]
