# src/multi_viaje.py
#
# Garantía de reparto completo mediante múltiples tandas.
#
# El algoritmo divide todos los pedidos en tandas sucesivas, cada una
# ajustada a las restricciones del vehículo (peso y volumen). Para cada
# tanda se reutilizan los algoritmos ya existentes:
#   - Selección: DP (mochila 2D) o Greedy (Quicksort + barrido voraz)
#   - Ruta: TSP con backtracking + poda (incluye vuelta al almacén)
#
# Complejidad total (cota superior):
#   - Con DP:     O(T * n * W * V)  siendo T = número de tandas
#   - Con Greedy: O(T * n log n)
#   En el peor caso T = n (una tanda por pedido), pero en la práctica T << n.

from dp_seleccion import seleccion_pedidos_dp
from greedy_seleccion import seleccion_pedidos_greedy
from backtracking_ruta import calcular_ruta_optima_tsp
from floyd_warshall import expandir_ruta_completa


def repartir_todos_pedidos(pedidos, capacidad_peso, capacidad_volumen,
                           dist_fw, pred_fw, metodo='DP'):
    """
    Reparte TODOS los pedidos en tandas sucesivas volviendo al almacén
    entre tanda y tanda. Garantiza que ningún pedido queda sin entregar.

    :param pedidos:           Lista de dicts con claves 'id', 'peso', 'volumen',
                              'beneficio', 'destino'.
    :param capacidad_peso:    Capacidad máxima de peso del vehículo.
    :param capacidad_volumen: Capacidad máxima de volumen del vehículo.
    :param dist_fw:           Matriz de distancias mínimas (Floyd-Warshall).
    :param pred_fw:           Matriz de predecesores (Floyd-Warshall).
    :param metodo:            'DP' o 'Greedy' para la selección de cada tanda.
    :return: dict con:
        - 'tandas':           Lista de dicts, uno por tanda (ver abajo).
        - 'tiempo_total':     Suma de tiempos de todas las tandas.
        - 'beneficio_total':  Suma de beneficios de todos los pedidos entregados.
        - 'num_tandas':       Número de viajes necesarios.
        - 'pedidos_sin_entregar': Lista de IDs de pedidos que no caben en ningún
                              vehículo (pedido individualmente demasiado grande).

    Cada entrada de 'tandas' contiene:
        - 'numero':           Número de tanda (1-indexado).
        - 'pedidos':          IDs de pedidos entregados en esta tanda.
        - 'tiempo':           Tiempo del circuito (almacén → entregas → almacén).
        - 'beneficio':        Beneficio acumulado en esta tanda.
        - 'ruta':             Nodos clave del circuito (TSP).
        - 'ruta_expandida':   Trayecto físico completo (Floyd-Warshall).
    """
    # Convertir dicts a tuplas (id, peso, volumen, beneficio) para los algoritmos
    pendientes = list(pedidos)   # copia para no mutar la lista original
    tandas = []
    tiempo_total = 0.0
    beneficio_total = 0
    pedidos_sin_entregar = []

    while pendientes:
        pedidos_alg = [
            (p['id'], p['peso'], p['volumen'], p['beneficio'])
            for p in pendientes
        ]

        # ── SELECCIÓN DE TANDA ──────────────────────────────────────────────
        if metodo == 'DP':
            beneficio_tanda, ids_tanda = seleccion_pedidos_dp(
                pedidos_alg, capacidad_peso, capacidad_volumen
            )
        else:
            beneficio_tanda, ids_tanda = seleccion_pedidos_greedy(
                pedidos_alg, capacidad_peso, capacidad_volumen
            )

        # Si ningún pedido pendiente cabe individualmente, los marcamos
        # como "sin entregar" (supera las capacidades del vehículo) y paramos.
        if not ids_tanda:
            pedidos_sin_entregar = [p['id'] for p in pendientes]
            break

        # ── RUTA DE LA TANDA (TSP) ──────────────────────────────────────────
        # Construir lista de nodos: almacén + destinos de la tanda
        id_set = set(ids_tanda)
        nodos_tanda = [0] + [
            p['destino'] for p in pendientes if p['id'] in id_set
        ]

        tiempo_tanda, ruta_tanda = calcular_ruta_optima_tsp(dist_fw, nodos_tanda)
        ruta_expandida = expandir_ruta_completa(ruta_tanda, pred_fw)

        # ── ACUMULAR RESULTADOS ─────────────────────────────────────────────
        tiempo_total    += tiempo_tanda
        beneficio_total += beneficio_tanda

        tandas.append({
            'numero':         len(tandas) + 1,
            'pedidos':        ids_tanda,
            'tiempo':         tiempo_tanda,
            'beneficio':      beneficio_tanda,
            'ruta':           ruta_tanda,
            'ruta_expandida': ruta_expandida,
        })

        # ── ELIMINAR PEDIDOS YA ENTREGADOS ──────────────────────────────────
        pendientes = [p for p in pendientes if p['id'] not in id_set]

    return {
        'tandas':               tandas,
        'tiempo_total':         tiempo_total,
        'beneficio_total':      beneficio_total,
        'num_tandas':           len(tandas),
        'pedidos_sin_entregar': pedidos_sin_entregar,
    }
