import json
import os

from dp_seleccion import seleccion_pedidos_dp
from backtracking_ruta import calcular_ruta_optima_tsp
from floyd_warshall import floyd_warshall, expandir_ruta_completa, nombres_ruta


def cargar_escenario(ruta_archivo):
    """Carga un escenario desde un archivo JSON."""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        return json.load(f)


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

def simulacion_mejor_vehiculo():
    inf = float('inf')
    
    # 1. DEFINICIÓN DEL ESCENARIO (Matriz de Alcalá de la Minuta 1)
    matriz_alcala = [
        [ 0,  15,  10,  12,   8,  14,  11,   9,   6,  18,  16,  13], # 0: Almacén
        [20,   0,   8, inf,  12,  18,  15,  10,  14,   7,   4, inf], # 1: Cervantes
        [10,   6,   0,   7,   5,  12,   9,   8,   7,  11,   8,  10], # 2: Estación
        [12, inf,   7,   0,   9,   8,  14,  16,  15,  22,  18,   3], # 3: Campus
        [ 8,  10,   5,   9,   0,   6,   4,   8,  11,  15,  12,  11], # 4: Magna
        [11,  13,   9,  14,   4,   5,   0,   6,  12,  16,  11,  15], # 5: Ensanche
        [ 9,  12,   8,  16,   8,  11,   6,   0,   5,  14,   9,  18], # 6: Chorrillo
        [ 6,  15,   7,  15,  11,  18,  12,   5,   0,   9,  12,  17], # 7: Reyes Católicos
        [18,   9,  11,  22,  15,  20,  16,  14,   9,   0,   5,  24], # 8: Nueva Alcalá
        [16,   5,   8,  18,  12,  15,  11,   9,  12,   4,   0,  19], # 9: Cuatro Caños
        [13, inf,  10,   4,  11,   9,  15,  18,  17,  24,  19,   0]  # 10: Hospital
    ]

    # Catálogo de vehículos y sus capacidades 
    vehiculos = {
        "A pie": {"capacidad": 5, "coste_min": 0.0},
        "Patinete": {"capacidad": 15, "coste_min": 0.25},
        "Furgoneta": {"capacidad": 50, "coste_min": 1.50}
    }

    directorio_escenarios = "../escenarios/"

    if not os.path.exists(directorio_escenarios):
        print(f"Error: No se encuentra la carpeta {directorio_escenarios}")
        return

    # Obtener lista de archivos disponibles
    todos_los_archivos = sorted([f for f in os.listdir(directorio_escenarios) if f.endswith('.json')])
    
    if not todos_los_archivos:
        print("No hay archivos JSON en la carpeta de escenarios.")
        return
    
    archivos_a_ejecutar = seleccionar_escenario(todos_los_archivos)

    for nombre_archivo in archivos_a_ejecutar:

        escenario = cargar_escenario(os.path.join(directorio_escenarios, nombre_archivo))
        pedidos_totales = escenario['pedidos']

        resultados_simulacion = []

        # ========================================================
        # PRE-PROCESO: FLOYD-WARSHALL
        # Calcula los caminos mínimos reales entre todos los pares
        # de nodos, resolviendo los saltos con inf (sin conexión
        # directa). A partir de aquí, el TSP trabaja con distancias
        # reales en lugar de costes directos incompletos.
        # Complejidad: O(n³), se ejecuta UNA SOLA VEZ.
        # ========================================================
        dist_fw, pred_fw = floyd_warshall(matriz_alcala)

        print(f"\n=== ESCENARIO: {nombre_archivo} ===")
        print("=== INICIANDO SIMULACIÓN DE REPARTO PARA RUBEN ===\n")

        # BUCLE PRINCIPAL: Probar cada vehículo
        for nombre, vehiculo_data in vehiculos.items():
            capacidad = vehiculo_data["capacidad"]
            print(f"Probando {nombre} (Capacidad: {capacidad}kg)...")

            # PASO A: SELECCIÓN (DP)
            # Pasar solo (id, peso, beneficio) a la función DP
            pedidos_para_dp = [(p['id'], p['peso'], p['beneficio']) for p in pedidos_totales]
            beneficio, seleccionados = seleccion_pedidos_dp(pedidos_para_dp, capacidad)

            if not seleccionados:
                print(f"   - {nombre} no tiene capacidad para ningún pedido.")
                continue

            # PASO B: RUTA (TSP)
            nodos_ruta = [0]  # Siempre empezar en almacén
            for sel in seleccionados:
                for p in pedidos_totales:
                    if p['id'] == sel:
                        nodos_ruta.append(p['destino'])

            # La matriz dist_fw ya contiene los costes mínimos reales (con intermediarios)
            tiempo_total, ruta = calcular_ruta_optima_tsp(dist_fw, nodos_ruta)

            # PASO C: MÉTRICA DE EFICIENCIA (€/min)
            eficiencia = beneficio / tiempo_total if tiempo_total > 0 else 0

            # PASO D: EXPANSIÓN DE RUTA (Floyd-Warshall)
            # Reconstruye el trayecto físico completo insertando los nodos
            # intermedios que Floyd-Warshall utilizó para optimizar cada tramo.
            # Se almacena para análisis detallado pero no se muestra en pantalla.
            ruta_expandida = expandir_ruta_completa(ruta, pred_fw)

            resultados_simulacion.append({
                "vehiculo": nombre,
                "beneficio": beneficio,
                "tiempo": tiempo_total,
                "eficiencia": eficiencia,
                "ruta": ruta,                    # Nodos clave (TSP)
                "ruta_expandida": ruta_expandida  # Trayecto físico completo (FW)
            })

            print(f"   [OK] Beneficio: {beneficio} EUR | Tiempo: {tiempo_total}min | Eficiencia: {eficiencia:.2f} EUR/min")

        # 2. COMPARACIÓN FINAL (fuera del bucle de vehículos)
        if not resultados_simulacion:
            print("\nNo se ha podido completar ninguna ruta.")
            continue

        # Encontrar el que tiene mayor eficiencia
        ganador = max(resultados_simulacion, key=lambda x: x['eficiencia'])

        print("\n" + "="*50)
        print("CONSEJO PARA RUBÉN")
        print("="*50)
        print(f"El vehículo más rentable hoy es: {ganador['vehiculo'].upper()}")
        print(f"Genera {ganador['eficiencia']:.2f} euros por cada minuto de trabajo.")
        print(f"Ruta recomendada: {ganador['ruta']}")
        print("="*50)

if __name__ == "__main__":
    simulacion_mejor_vehiculo()
