import json
import os

from dp_seleccion import seleccion_pedidos_dp
from greedy_seleccion import seleccion_pedidos_greedy
from backtracking_ruta import calcular_ruta_optima_tsp
from floyd_warshall import floyd_warshall, expandir_ruta_completa, nombres_ruta


def cargar_escenario(ruta_archivo):
    """Carga un escenario desde un archivo JSON, convirtiendo null → inf."""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    inf = float('inf')
    # Convertir null de JSON a inf en la matriz de adyacencia
    raw['matriz_adyacencia'] = [
        [inf if v is None else v for v in fila]
        for fila in raw['matriz_adyacencia']
    ]
    return raw


def seleccionar_escenario(archivos):
    """Permite al usuario seleccionar uno o todos los escenarios disponibles."""
    print("Escenarios disponibles:")
    for i, nombre in enumerate(archivos):
        print(f"  [{i+1}] {nombre}")
    print(f"  [0] Ejecutar todos")

    opcion = input("\nSelecciona un escenario (número): ").strip()
    if opcion == '0':
        return archivos
    try:
        idx = int(opcion) - 1
        if 0 <= idx < len(archivos):
            return [archivos[idx]]
    except ValueError:
        pass
    print("Opción no válida, ejecutando todos los escenarios.")
    return archivos


def ejecutar_vehiculo(nombre, vehiculo_data, pedidos_totales, dist_fw, pred_fw, metodo):
    """
    Ejecuta el pipeline completo (selección + TSP + expansión) para un vehículo
    usando el método de selección indicado ('DP' o 'Greedy').

    :return: dict con los resultados, o None si el vehículo no puede completar ningún pedido.
    """
    capacidad_peso    = vehiculo_data["capacidad_peso"]
    capacidad_volumen = vehiculo_data["capacidad_volumen"]

    # Preparar lista unificada (id, peso, volumen, beneficio)
    pedidos_para_alg = [
        (p['id'], p['peso'], p['volumen'], p['beneficio'])
        for p in pedidos_totales
    ]

    # PASO A: SELECCIÓN
    if metodo == 'DP':
        beneficio, seleccionados = seleccion_pedidos_dp(
            pedidos_para_alg, capacidad_peso, capacidad_volumen
        )
    else:  # Greedy
        beneficio, seleccionados = seleccion_pedidos_greedy(
            pedidos_para_alg, capacidad_peso, capacidad_volumen
        )

    if not seleccionados:
        return None

    # PASO B: RUTA (TSP Backtracking)
    nodos_ruta = [0]  # Siempre empezar en almacén
    for sel in seleccionados:
        for p in pedidos_totales:
            if p['id'] == sel:
                nodos_ruta.append(p['destino'])

    tiempo_total, ruta = calcular_ruta_optima_tsp(dist_fw, nodos_ruta)

    # PASO C: EFICIENCIA
    eficiencia = beneficio / tiempo_total if tiempo_total > 0 else 0

    # PASO D: EXPANSIÓN DE RUTA (Floyd-Warshall)
    ruta_expandida = expandir_ruta_completa(ruta, pred_fw)

    return {
        "vehiculo":      nombre,
        "metodo":        metodo,
        "beneficio":     beneficio,
        "tiempo":        tiempo_total,
        "eficiencia":    eficiencia,
        "seleccionados": seleccionados,
        "ruta":          ruta,
        "ruta_expandida": ruta_expandida
    }


def simulacion_mejor_vehiculo():
    # ========================================================
    # DEFINICIÓN DEL CATÁLOGO DE VEHÍCULOS
    # Ahora con capacidad_peso Y capacidad_volumen
    # ========================================================
    vehiculos = {
        "A pie":    {"capacidad_peso": 5,  "capacidad_volumen": 8},
        "Patinete": {"capacidad_peso": 15, "capacidad_volumen": 20},
        "Furgoneta":{"capacidad_peso": 50, "capacidad_volumen": 60},
    }

    directorio_escenarios = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "escenarios"
    )

    if not os.path.exists(directorio_escenarios):
        print(f"Error: No se encuentra la carpeta {directorio_escenarios}")
        return

    todos_los_archivos = sorted(
        [f for f in os.listdir(directorio_escenarios) if f.endswith('.json')]
    )

    if not todos_los_archivos:
        print("No hay archivos JSON en la carpeta de escenarios.")
        return

    archivos_a_ejecutar = seleccionar_escenario(todos_los_archivos)

    for nombre_archivo in archivos_a_ejecutar:

        escenario = cargar_escenario(
            os.path.join(directorio_escenarios, nombre_archivo)
        )
        pedidos_totales = escenario['pedidos']

        print(f"\n{'='*60}")
        print(f"  ESCENARIO: {escenario['nombre']}")
        print(f"  {escenario['descripcion']}")
        print(f"{'='*60}")

        # ====================================================
        # PRE-PROCESO: FLOYD-WARSHALL
        # Complejidad: O(n³), una sola vez por escenario.
        # ====================================================
        dist_fw, pred_fw = floyd_warshall(escenario['matriz_adyacencia'])

        resultados_dp     = []
        resultados_greedy = []

        # BUCLE PRINCIPAL: Probar cada vehículo con AMBOS métodos
        for nombre, vehiculo_data in vehiculos.items():
            cap_p = vehiculo_data["capacidad_peso"]
            cap_v = vehiculo_data["capacidad_volumen"]
            print(f"\n  Vehículo: {nombre} (Peso máx: {cap_p}kg | Volumen máx: {cap_v}u)")
            print(f"  {'-'*54}")

            for metodo in ('DP', 'Greedy'):
                res = ejecutar_vehiculo(
                    nombre, vehiculo_data, pedidos_totales, dist_fw, pred_fw, metodo
                )
                if res is None:
                    print(f"    [{metodo:6}] Sin pedidos que quepan.")
                    continue

                print(
                    f"    [{metodo:6}] "
                    f"Pedidos: {res['seleccionados']} | "
                    f"Beneficio: {res['beneficio']} EUR | "
                    f"Tiempo: {res['tiempo']} min | "
                    f"Eficiencia: {res['eficiencia']:.2f} EUR/min"
                )

                if metodo == 'DP':
                    resultados_dp.append(res)
                else:
                    resultados_greedy.append(res)

        # ====================================================
        # COMPARACIÓN FINAL: mejor vehículo por cada método
        # ====================================================
        print(f"\n{'='*60}")
        print("  COMPARACIÓN FINAL")
        print(f"{'='*60}")

        for metodo, resultados in (('DP', resultados_dp), ('Greedy', resultados_greedy)):
            if not resultados:
                print(f"  [{metodo}] Ningún vehículo completó ninguna ruta.")
                continue
            ganador = max(resultados, key=lambda x: x['eficiencia'])
            print(
                f"  [{metodo:6}] Mejor vehiculo: {ganador['vehiculo'].upper()} -> "
                f"{ganador['eficiencia']:.2f} EUR/min "
                f"(beneficio {ganador['beneficio']} EUR en {ganador['tiempo']} min)"
            )

        # Diferencia entre métodos (vehículo más eficiente de cada uno)
        if resultados_dp and resultados_greedy:
            mejor_dp     = max(resultados_dp,     key=lambda x: x['eficiencia'])
            mejor_greedy = max(resultados_greedy, key=lambda x: x['eficiencia'])
            diff = mejor_dp['beneficio'] - mejor_greedy['beneficio']
            if diff > 0:
                print(f"\n  >> DP obtiene {diff} EUR mas que Greedy en el mejor caso.")
            elif diff < 0:
                print(f"\n  >> Greedy obtiene {-diff} EUR mas que DP en el mejor caso.")
            else:
                print(f"\n  >> Ambos metodos alcanzan el mismo beneficio optimo.")

        print()


if __name__ == "__main__":
    simulacion_mejor_vehiculo()
