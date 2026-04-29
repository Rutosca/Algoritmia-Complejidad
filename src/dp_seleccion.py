# src/dp_seleccion.py

def seleccion_pedidos_dp(pedidos, capacidad_peso, capacidad_volumen):
    """
    Resuelve el problema de selección de pedidos usando Programación Dinámica.
    Mochila 0/1 bidimensional: restricción de PESO y VOLUMEN simultáneamente.

    :param pedidos: Lista de tuplas (id_pedido, peso, volumen, beneficio)
    :param capacidad_peso:    Capacidad máxima de peso del vehículo (entero)
    :param capacidad_volumen: Capacidad máxima de volumen del vehículo (entero)
    :return: Tupla (beneficio_maximo, lista_ids_seleccionados)

    Complejidad temporal: O(n * W * V)
    Complejidad espacial: O(n * W * V)
    donde n = número de pedidos, W = cap. peso, V = cap. volumen.
    """
    # ========================================================
    # 1. VALIDACIÓN DE ENTRADA
    # ========================================================
    if not pedidos or capacidad_peso <= 0 or capacidad_volumen <= 0:
        return 0, []

    n = len(pedidos)

    # ========================================================
    # 2. INICIALIZACIÓN DE LA TABLA DP (3D)
    # dp[i][w][v] = máximo beneficio usando los primeros i pedidos
    #               con w unidades de peso y v unidades de volumen disponibles.
    # ========================================================
    dp = [[[0] * (capacidad_volumen + 1) for _ in range(capacidad_peso + 1)]
          for _ in range(n + 1)]

    # ========================================================
    # 3. RELLENADO DE LA TABLA (Relación de recurrencia)
    # ========================================================
    for i in range(1, n + 1):
        id_pedido, peso_i, volumen_i, beneficio_i = pedidos[i - 1]

        for w in range(capacidad_peso + 1):
            for v in range(capacidad_volumen + 1):
                # Opción 1: no incluir el pedido i
                opcion_no_meter = dp[i - 1][w][v]

                # Opción 2: incluir el pedido i (si cabe en ambas dimensiones)
                opcion_si_meter = 0
                if peso_i <= w and volumen_i <= v:
                    opcion_si_meter = beneficio_i + dp[i - 1][w - peso_i][v - volumen_i]

                dp[i][w][v] = max(opcion_no_meter, opcion_si_meter)

    beneficio_maximo = dp[n][capacidad_peso][capacidad_volumen]

    # ========================================================
    # 4. RECONSTRUCCIÓN DE LA SOLUCIÓN (backtracking)
    # ========================================================
    pedidos_seleccionados = []
    w_actual = capacidad_peso
    v_actual = capacidad_volumen

    for i in range(n, 0, -1):
        # Si el valor cambió respecto a la fila anterior, este pedido fue incluido
        if dp[i][w_actual][v_actual] != dp[i - 1][w_actual][v_actual]:
            id_pedido, peso_i, volumen_i, beneficio_i = pedidos[i - 1]
            pedidos_seleccionados.append(id_pedido)
            w_actual -= peso_i
            v_actual -= volumen_i

    pedidos_seleccionados.reverse()
    return beneficio_maximo, pedidos_seleccionados
