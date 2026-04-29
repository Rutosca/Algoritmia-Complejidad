# src/backtracking_ruta.py

def calcular_ruta_optima_tsp(matriz_tiempos, destinos_unicos):
    """
    Resuelve el TSP para los destinos seleccionados minimizando el coste.
    ENTRADAS:   - matriz_tiempos: lista de listas (matriz de adyacencia).
                  float('inf') indica que no hay conexión directa.
                - destinos_unicos: lista de índices de nodos a visitar.
                  El índice [0] SIEMPRE debe ser el almacén (origen).
    SALIDAS:    Devuelve una tupla (coste_total_minimo, mejor_ruta_encontrada).
    """
    # Convertimos a diccionario para eliminar duplicados y se convierte de nuevo a lista
    destinos_unicos = list(dict.fromkeys(destinos_unicos))
    # El origen es el primer elemento de la lista
    origen = destinos_unicos[0]
    # Los nodos intermedios a visitar son el resto
    nodos_intermedios = destinos_unicos[1:]

    mejor_coste_global = float('inf')
    mejor_ruta_global = []

    # Función recursiva interna
    def explorar_rutas(lugar_actual, visitados, ruta_actual, coste_actual):
        nonlocal mejor_coste_global, mejor_ruta_global

        # ========================================================
        # PODA (Branch & Bound)
        # ========================================================
        # Si ya hemos gastado más tiempo que nuestro récord, abortamos esta rama
        if coste_actual >= mejor_coste_global:
            return

        # ========================================================
        # CASO BASE: Todos los clientes visitados
        # ========================================================
        if len(visitados) == len(nodos_intermedios):
            # Comprobar si existe camino de vuelta al almacén
            coste_retorno = matriz_tiempos[lugar_actual][origen]
            
            # Solo cerramos el ciclo si la calle existe (no es infinito)
            if coste_retorno != float('inf'):
                coste_total = coste_actual + coste_retorno
                if coste_total < mejor_coste_global:
                    mejor_coste_global = coste_total
                    mejor_ruta_global = ruta_actual + [origen]
            return

        # ========================================================
        # RECURSIÓN Y RETROCESO (Backtracking)
        # ========================================================
        for siguiente_destino in nodos_intermedios:
            if siguiente_destino not in visitados:

                # Comprobamos el coste hacia el siguiente destino
                coste_tramo = matriz_tiempos[lugar_actual][siguiente_destino]
                
                # Avanzamos SOLO si la calle existe
                if coste_tramo != float('inf'):
                    
                    # 1. Avanzar
                    visitados.add(siguiente_destino)
                    ruta_actual.append(siguiente_destino)

                    # 2. Explorar (Llamada recursiva)
                    explorar_rutas(
                        lugar_actual=siguiente_destino,
                        visitados=visitados,
                        ruta_actual=ruta_actual,
                        coste_actual=coste_actual + coste_tramo
                    )

                    # 3. Deshacer (Backtracking) para probar otro camino
                    ruta_actual.pop()
                    visitados.remove(siguiente_destino)

    # ========================================================
    # INICIALIZACIÓN DEL ALGORITMO
    # ========================================================
    estado_visitados = set()
    estado_ruta = [origen]  # Empezamos desde el almacén

    # Lanzamos la primera exploración
    explorar_rutas(origen, estado_visitados, estado_ruta, 0.0)

    return mejor_coste_global, mejor_ruta_global
