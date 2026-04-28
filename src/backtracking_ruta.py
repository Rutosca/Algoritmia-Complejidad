def calcular_ruta_optima_tsp(matriz_tiempos: list, destinos_unicos: list):
    """
    Resuelve el TSP para los destinos_unicos seleccionados minimizando el coste.
    ENTRADAS:   -matriz_tiempos, grafo ponderado modelado como matriz de adyacencia
                 (lista de listas), donde matriz_tiempos[i][j] es el coste del
                 tramo i -> j. El valor 0 indica que no existe conexión directa
                 (salvo el diagonal).
                -destinos_unicos, lista de índices de nodos a visitar (incluye el
                 índice del almacén/origen, que siempre debe ser el primer elemento).
    SALIDAS:    Devuelve una tupla con la ruta optimizada en la primera posición y
                el coste total de esa ruta en la segunda.
    """
    # El origen es el primer elemento de la lista (índice del almacén)
    origen = destinos_unicos[0]
    # Los nodos intermedios son el resto
    nodos_intermedios = destinos_unicos[1:]

    mejor_coste_global = float('inf')
    mejor_ruta_global = []

    # Función recursiva interna
    def explorar_rutas(lugar_actual, visitados, ruta_actual, coste_actual):
        nonlocal mejor_coste_global, mejor_ruta_global

        # PODA. Si ya hemos gastado más tiempo que nuestro récord, abortamos esta rama
        if coste_actual >= mejor_coste_global:
            return

        # CASO BASE: todos los nodos intermedios han sido visitados
        if len(visitados) == len(nodos_intermedios):
            # Comprobar si existe camino de vuelta al almacén desde donde estamos
            coste_retorno = matriz_tiempos[lugar_actual][origen]
            if coste_retorno > 0:
                coste_total = coste_actual + coste_retorno
                if coste_total < mejor_coste_global:
                    mejor_coste_global = coste_total
                    mejor_ruta_global = ruta_actual + [origen]
            return

        # RETROCESO
        for siguiente_destino in nodos_intermedios:
            # Visitamos nodos pendientes
            if siguiente_destino not in visitados:

                # Comprobamos que existe conexión directa al siguiente destino
                coste_tramo = matriz_tiempos[lugar_actual][siguiente_destino]
                if coste_tramo > 0:

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

    return mejor_coste_global, mejor_ruta_global