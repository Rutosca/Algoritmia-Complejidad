# src/greedy_seleccion.py

def _quicksort_pedidos(pedidos, inicio, fin):
    """
    Implementación recursiva de Quicksort in-place sobre la lista de pedidos.

    Criterio de ordenación (DESCENDENTE):
      1. Mayor beneficio primero.
      2. Empate en beneficio → menor peso/volumen combinado (peso + volumen) primero,
         para maximizar el número de pedidos que caben en el vehículo.

    Complejidad: O(n log n) caso promedio, O(n²) peor caso.
    """
    if inicio >= fin:
        return

    pivote = pedidos[fin]
    _, peso_p, volumen_p, beneficio_p = pivote
    bulto_p = peso_p + volumen_p   # "bulto" = peso + volumen del pivote

    i = inicio - 1

    for j in range(inicio, fin):
        _, peso_j, volumen_j, beneficio_j = pedidos[j]
        bulto_j = peso_j + volumen_j

        # Viene antes si: mayor beneficio, o igual beneficio y menor bulto
        if beneficio_j > beneficio_p or (beneficio_j == beneficio_p and bulto_j < bulto_p):
            i += 1
            pedidos[i], pedidos[j] = pedidos[j], pedidos[i]

    pedidos[i + 1], pedidos[fin] = pedidos[fin], pedidos[i + 1]
    particion = i + 1

    _quicksort_pedidos(pedidos, inicio, particion - 1)
    _quicksort_pedidos(pedidos, particion + 1, fin)


def seleccion_pedidos_greedy(pedidos, capacidad_peso, capacidad_volumen):
    """
    Selecciona pedidos con un enfoque voraz (greedy):
    - Ordena los pedidos por beneficio DESC (desempate: menor peso+volumen).
    - Recorre la lista ordenada e incluye cada pedido si cabe en el vehículo.

    :param pedidos: Lista de tuplas (id_pedido, peso, volumen, beneficio)
    :param capacidad_peso:    Capacidad máxima de peso del vehículo
    :param capacidad_volumen: Capacidad máxima de volumen del vehículo
    :return: Tupla (beneficio_total, lista_ids_seleccionados)

    Complejidad: O(n log n) por el Quicksort + O(n) por el barrido = O(n log n)
    """
    if not pedidos or capacidad_peso <= 0 or capacidad_volumen <= 0:
        return 0, []

    # Trabajamos con copia para no alterar la lista original
    pedidos_ordenados = list(pedidos)
    _quicksort_pedidos(pedidos_ordenados, 0, len(pedidos_ordenados) - 1)

    peso_restante    = capacidad_peso
    volumen_restante = capacidad_volumen
    beneficio_total  = 0
    seleccionados    = []

    for id_pedido, peso_i, volumen_i, beneficio_i in pedidos_ordenados:
        if peso_i <= peso_restante and volumen_i <= volumen_restante:
            seleccionados.append(id_pedido)
            beneficio_total  += beneficio_i
            peso_restante    -= peso_i
            volumen_restante -= volumen_i

    return beneficio_total, seleccionados
