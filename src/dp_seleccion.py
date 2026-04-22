def seleccion_pedidos_dp(pedidos, capacidad_maxima):
    """
    Resuelve el problema de selección de pedidos usando Programación Dinámica (Mochila 0/1).
    
    :param pedidos: Lista de tuplas (id_pedido, peso, beneficio)
    :param capacidad_maxima: Entero con la capacidad C del vehículo
    :return: Tupla con (beneficio_maximo, lista_ids_seleccionados)
    """
    # ========================================================
    # VALIDACIÓN DE ENTRADA
    # ========================================================
    if not pedidos:
        return 0, []
    
    if capacidad_maxima <= 0:
        return 0, []
    
    # Validar formato de cada pedido
    for pedido in pedidos:
        if len(pedido) != 3:
            raise ValueError(f"Formato incorrecto en pedido {pedido}. Esperado: (id, peso, beneficio)")
        id_ped, peso, beneficio = pedido
        if peso < 0 or beneficio < 0:
            raise ValueError(f"Pedido {id_ped} tiene peso o beneficio negativo")

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
    # ========================================================
    # VALIDACIÓN DE CONSISTENCIA
    # ========================================================
    # Verificar que los pedidos seleccionados no excedan la capacidad
    peso_total = sum(p[1] for p in pedidos if p[0] in pedidos_seleccionados)
    assert peso_total <= capacidad_maxima, \
        f"ERROR: Peso total ({peso_total}) excede capacidad ({capacidad_maxima})"
    
    # Verificar que el beneficio calculado coincide con la suma real
    beneficio_calculado = sum(p[2] for p in pedidos if p[0] in pedidos_seleccionados)
    assert beneficio_calculado == beneficio_maximo, \
        f"ERROR: Beneficio inconsistente (DP: {beneficio_maximo}, Real: {beneficio_calculado})"
    
    return beneficio_maximo, pedidos_seleccionados


if __name__ == "__main__":
    # Test 1: Caso base del proyecto
    print("🧪 Test 1: Caso base")
    pedidos = [("P1", 2, 10), ("P2", 3, 15), ("P3", 4, 30), ("P4", 5, 20)]
    beneficio, seleccionados = seleccion_pedidos_dp(pedidos, 8)
    print(f"   Beneficio: {beneficio}, Pedidos: {seleccionados}")
    assert beneficio == 45, "Test 1 falló"
    assert set(seleccionados) == {"P2", "P4"} or set(seleccionados) == {"P3", "P2"}, "Test 1 falló"
    
    # Test 2: Lista vacía
    print("🧪 Test 2: Sin pedidos")
    beneficio, seleccionados = seleccion_pedidos_dp([], 10)
    assert beneficio == 0 and seleccionados == [], "Test 2 falló"
    
    # Test 3: Capacidad 0
    print("🧪 Test 3: Capacidad cero")
    beneficio, seleccionados = seleccion_pedidos_dp(pedidos, 0)
    assert beneficio == 0 and seleccionados == [], "Test 3 falló"
    
    # Test 4: Ningún pedido cabe
    print("🧪 Test 4: Ningún pedido cabe")
    beneficio, seleccionados = seleccion_pedidos_dp([("P1", 10, 50)], 5)
    assert beneficio == 0 and seleccionados == [], "Test 4 falló"
    
    print("\n✅ Todos los tests pasaron correctamente")