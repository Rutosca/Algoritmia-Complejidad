def calcular_ruta_optima_tsp(matriz_tiempos: dict, destinos_unicos: list):
    """
    Resuelve el TSP para los destinos_unicos seleccionados minimizando el coste.
    ENTRADAS:   -matriz_tiempos, grafo ponderado modelado en lista de adyacencia
                -destinos_unicos, lista de destinos_unicos generados en el módulo de selección de destinos_unicos
    SALIDAS:    Devuelve una tupla con la ruta optimizada en la primera posición y el coste de tiempo de esa ruta
    """
    # Variables globales para mantener el récord y inicializar el origen
    origen = "La Garena (Almacén)"
    mejor_coste_global = float('inf')
    mejor_ruta_global = []

    # Función recursiva interna 
    def explorar_rutas(lugar_actual, visitados, ruta_actual, coste_actual):
        nonlocal mejor_coste_global, mejor_ruta_global

        # PODA. Si ya hemos gastado más tiempo que nuestro récord, abortamos esta rama
        if coste_actual >= mejor_coste_global:
            return 

        # CASO BASE
        if len(visitados) == len(destinos_unicos):
           # Comprobar si existe camino de vuelta al almacén desde donde estamos
            conexiones_actuales = matriz_tiempos.get(lugar_actual, {})
            
            if origen in conexiones_actuales:
                coste_retorno = conexiones_actuales[origen]
                coste_total = coste_actual + coste_retorno

                if coste_total < mejor_coste_global:
                    mejor_coste_global = coste_total
                    mejor_ruta_global = ruta_actual + [origen]
            return

        # RETROCESO
        for siguiente_destino in destinos_unicos:
            # Visitamos nodos pendientes
            if siguiente_destino not in visitados:
                
                # Extraemos el sub-diccionario de calles desde nuestro lugar actual
                conexiones_actuales = matriz_tiempos.get(lugar_actual, {})
                
                # Comprobamos que la calle al siguiente destino existe
                if siguiente_destino in conexiones_actuales:
                    coste_tramo = conexiones_actuales[siguiente_destino]
                    
                    # Se avanza al siguiente nodo
                    visitados.add(siguiente_destino)
                    ruta_actual.append(siguiente_destino)
                    
                    # Recursión, bajar un nivel en el árbol
                    explorar_rutas(
                        lugar_actual=siguiente_destino, 
                        visitados=visitados, 
                        ruta_actual=ruta_actual, 
                        coste_actual=coste_actual + coste_tramo
                    )
                    
                    # Deshacer, quitamos el destino para que el bucle pueda probar con el siguiente
                    ruta_actual.pop()
                    visitados.remove(siguiente_destino)

    # Inicialización del algoritmo
    estado_visitados = set()
    estado_ruta = [origen]  # Empezamos desde el almacén
    
    explorar_rutas(origen, estado_visitados, estado_ruta, 0.0)

    return mejor_ruta_global, mejor_coste_global