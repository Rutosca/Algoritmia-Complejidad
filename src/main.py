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


# Factor global de coste de embalaje (EUR por unidad de volumen)
FACTOR_EMBALAJE = 0.5


def ejecutar_vehiculo(nombre, vehiculo_data, pedidos_totales, dist_fw, pred_fw, metodo):
    """
    Ejecuta el pipeline completo usando MULTI-VIAJE (repartiendo todo lo posible en tandas).

    Beneficio neto = beneficio_bruto - coste_embalaje - coste_ruta
      · coste_embalaje = FACTOR_EMBALAJE * volumen_total_cargado
      · coste_ruta     = coste_por_minuto * tiempo_ruta  (varía por vehículo)

    :return: dict con resulta4dos, o None si no hay pedidos que quepan.
    """
    from multi_viaje import repartir_todos_pedidos

    capacidad_peso    = vehiculo_data["capacidad_peso"]
    capacidad_volumen = vehiculo_data["capacidad_volumen"]
    coste_por_minuto  = vehiculo_data.get("coste_por_minuto", 0.0)

    # PASO A: MULTI-VIAJE (repartir todos los pedidos en tandas sucesivas)
    resultado_multi = repartir_todos_pedidos(
        pedidos_totales, capacidad_peso, capacidad_volumen,
        dist_fw, pred_fw, metodo=metodo
    )

    tandas = resultado_multi['tandas']
    if not tandas:
        return None

    # PASO B: Calcular Costes Acumulados
    seleccionados = []
    coste_embalaje = 0.0

    for tanda in tandas:
        ids_tanda = tanda['pedidos']
        seleccionados.extend(ids_tanda)
        id_set = set(ids_tanda)
        volumen_usado = sum(p['volumen'] for p in pedidos_totales if p['id'] in id_set)
        
        tanda_coste_embalaje = volumen_usado * FACTOR_EMBALAJE
        tanda_coste_ruta = coste_por_minuto * tanda['tiempo']
        tanda_neto = tanda['beneficio'] - tanda_coste_embalaje - tanda_coste_ruta
        
        tanda['coste_embalaje'] = tanda_coste_embalaje
        tanda['coste_ruta'] = tanda_coste_ruta
        tanda['neto'] = tanda_neto
        
        coste_embalaje += tanda_coste_embalaje

    beneficio_bruto = resultado_multi['beneficio_total']
    tiempo_total = resultado_multi['tiempo_total']

    # PASO D: COSTE OPERATIVO DEL VEHÍCULO (combustible / desgaste / alquiler)
    coste_ruta = coste_por_minuto * tiempo_total

    # PASO E: BENEFICIO NETO y EFICIENCIA
    beneficio_neto = beneficio_bruto - coste_embalaje - coste_ruta
    eficiencia     = beneficio_neto / tiempo_total if tiempo_total > 0 else 0

    # Retornamos la ruta de la última tanda como representativa (el main original no la imprime)
    ruta = tandas[-1]['ruta'] if tandas else []
    ruta_expandida = tandas[-1]['ruta_expandida'] if tandas else []

    return {
        "vehiculo":        nombre,
        "metodo":          metodo,
        "beneficio_bruto": beneficio_bruto,
        "coste_embalaje":  coste_embalaje,
        "coste_ruta":      coste_ruta,
        "beneficio":       beneficio_neto,
        "tiempo":          tiempo_total,
        "eficiencia":      eficiencia,
        "seleccionados":   seleccionados,
        "ruta":            ruta,
        "ruta_expandida":  ruta_expandida,
        "num_tandas":      resultado_multi['num_tandas'],
        "sin_entregar":    resultado_multi['pedidos_sin_entregar'],
        "tandas":          tandas
    }


def simulacion_mejor_vehiculo():
    # ========================================================
    # DEFINICIÓN DEL CATÁLOGO DE VEHÍCULOS
    # Ahora con capacidad_peso Y capacidad_volumen
    # ========================================================
    # coste_por_minuto: coste operativo EUR/min (combustible, desgaste, alquiler)
    vehiculos = {
        "A pie":    {"capacidad_peso":  5, "capacidad_volumen":  8, "coste_por_minuto": 0.0},
        "Patinete": {"capacidad_peso": 15, "capacidad_volumen": 20, "coste_por_minuto": 0.3},
        "Furgoneta":{"capacidad_peso": 50, "capacidad_volumen": 60, "coste_por_minuto": 1.5},
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
            cap_p  = vehiculo_data["capacidad_peso"]
            cap_v  = vehiculo_data["capacidad_volumen"]
            cpm    = vehiculo_data["coste_por_minuto"]
            print(f"\n  Vehículo: {nombre} "
                  f"(Peso máx: {cap_p}kg | Volumen máx: {cap_v}u | Coste: {cpm} EUR/min)")
            print(f"  {'-'*54}")

            for metodo in ('DP', 'Greedy'):
                res = ejecutar_vehiculo(
                    nombre, vehiculo_data, pedidos_totales, dist_fw, pred_fw, metodo
                )
                if res is None:
                    print(f"    [{metodo:6}] Sin pedidos que quepan.")
                    continue

                print(f"    [{metodo:6}] TOTAL -> Bruto: {res['beneficio_bruto']:.1f} - Emb: {res['coste_embalaje']:.1f} - Veh: {res['coste_ruta']:.1f} = Neto: {res['beneficio']:.1f} EUR | Tiempo: {res['tiempo']:.1f} min | Eficiencia Global: {res['eficiencia']:.2f} EUR/min")
                print(f"             (Se realizaron {res['num_tandas']} tandas de reparto)")
                for tanda in res['tandas']:
                    print(f"               - Tanda {tanda['numero']}: Pedidos {tanda['pedidos']} | Bruto: {tanda['beneficio']:.1f} - Emb: {tanda['coste_embalaje']:.1f} - Veh: {tanda['coste_ruta']:.1f} = Neto: {tanda['neto']:.1f} EUR | Tiempo: {tanda['tiempo']:.1f} min")
                if res['sin_entregar']:
                    print(f"               * Pedidos intransportables: {res['sin_entregar']}")

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