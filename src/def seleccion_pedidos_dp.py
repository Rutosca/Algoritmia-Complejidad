def seleccion_pedidos_dp(pedidos, capacidad_maxima):
    """
    Resuelve el problema de selección de pedidos usando Programación Dinámica (Mochila 0/1).
    
    :param pedidos: Lista de tuplas (id_pedido, peso, beneficio)
    :param capacidad_maxima: Entero con la capacidad C del vehículo
    :return: Tupla con (beneficio_maximo, lista_ids_seleccionados)
    """
    n = len(pedidos)
    
    # 1. INICIALIZACIÓN DE LA MATRIZ DP (Casos base incluidos al llenar con 0s)
    # Creamos una matriz de (n + 1) filas por (capacidad_maxima + 1) columnas.
    dp = [[0 for _ in range(capacidad_maxima + 1)] for _ in range(n + 1)]
    
    # 2. RELLENADO DE LA MATRIZ (Relación de recurrencia)
    for i in range(1, n + 1):
        id_pedido, peso_i, beneficio_i = pedidos[i - 1]
        
        for w in range(1, capacidad_maxima + 1):
            if peso_i <= w:
                # El pedido cabe: evaluamos si es mejor meterlo o no
                opcion_no_meter = dp[i - 1][w]
                opcion_si_meter = beneficio_i + dp[i - 1][w - peso_i]
                dp[i][w] = max(opcion_no_meter, opcion_si_meter)
            else:
                # El pedido no cabe: nos quedamos con el beneficio anterior
                dp[i][w] = dp[i - 1][w]
                
    # El beneficio máximo total estará en la esquina inferior derecha de la matriz
    beneficio_maximo = dp[n][capacidad_maxima]
    
    # 3. RECONSTRUCCIÓN DE LA SOLUCIÓN (Averiguar qué pedidos forman ese beneficio)
    pedidos_seleccionados = []
    w_actual = capacidad_maxima
    
    # Recorremos la matriz desde abajo hacia arriba
    for i in range(n, 0, -1):
        # Si el valor actual es diferente al de la fila de arriba, significa que 
        # este pedido SE INCLUYÓ para mejorar el beneficio.
        if dp[i][w_actual] != dp[i - 1][w_actual]:
            id_pedido, peso_i, beneficio_i = pedidos[i - 1]
            pedidos_seleccionados.append(id_pedido)
            # Restamos el peso de este pedido a la capacidad que nos quedaba
            w_actual -= peso_i
            
    # Opcional: Invertir la lista para que salgan en el orden original
    pedidos_seleccionados.reverse()
    
    return beneficio_maximo, pedidos_seleccionados
