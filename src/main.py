import json
import os

from dp_seleccion import seleccion_pedidos_dp
from backtracking_ruta import calcular_ruta_optima_tsp
from floyd_warshall import floyd_warshall, expandir_ruta_completa, nombres_ruta

def cargar_escenario(ruta_archivo):
    """Lee el JSON y convierte 'null' en 'inf'."""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    matriz_cruda = datos['matriz_adyacencia']
    matriz_procesada = [
        [valor if valor is not None else float('inf') for valor in fila]
        for fila in matriz_cruda
    ]
    datos['matriz_adyacencia'] = matriz_procesada
    return datos

def seleccionar_escenario(archivos):
    """Presenta un menú al usuario y devuelve el archivo elegido."""
    print("\n--- ESCENARIOS DISPONIBLES ---")
    for i, archivo in enumerate(archivos):
        print(f"[{i + 1}] {archivo}")
    print(f"[{len(archivos) + 1}] EJECUTAR TODOS")
    
    while True:
        try:
            opcion = int(input(f"\nSelecciona una opción (1-{len(archivos) + 1}): "))
            if 1 <= opcion <= len(archivos):
                return [archivos[opcion - 1]] # Devolvemos una lista con un solo archivo
            elif opcion == len(archivos) + 1:
                return archivos # Devolvemos la lista completa
            else:
                print("Error: Opción fuera de rango.")
        except ValueError:
            print("Error: Por favor, introduce un número válido.")

def simulacion_mejor_vehiculo():    
    # Catálogo de vehículos y sus capacidades 
    vehiculos = {
        "A pie": 5,
        "Patinete": 15,
        "Furgoneta": 50
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

        resultados_simulacion = []

        # ========================================================
        # PRE-PROCESO: FLOYD-WARSHALL
        # Calcula los caminos mínimos reales entre todos los pares
        # de nodos, resolviendo los saltos con inf (sin conexión
        # directa). A partir de aquí, el TSP trabaja con distancias
        # reales en lugar de costes directos incompletos.
        # Complejidad: O(n³), se ejecuta UNA SOLA VEZ.
        # ========================================================
        dist_fw, pred_fw = floyd_warshall(escenario['matriz_adyacencia'])

        print("=== INICIANDO SIMULACIÓN DE REPARTO PARA RUBEN ===\n")

        # BUCLE PRINCIPAL: Probar cada vehículo
        for nombre, capacidad in vehiculos.items():
            print(f"Probando {nombre} (Capacidad: {capacidad}kg)...")

            # PASO A: SELECCIÓN (DP) 
            # Pasar solo (id, peso, beneficio) a la función DP
            pedidos_para_dp = [(p['id'], p['peso'], p['beneficio']) for p in escenario['pedidos']]
            beneficio, seleccionados = seleccion_pedidos_dp(pedidos_para_dp, capacidad)

            if not seleccionados:
                print(f"   - {nombre} no tiene capacidad para ningún pedido.")
                continue

            # PASO B: RUTA (TSP) 
            nodos_ruta = [0] # Siempre empezar en almacén
            for sel in seleccionados:
                for p in escenario['pedidos']:
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
                "ruta": ruta,                   # Nodos clave (TSP)
                "ruta_expandida": ruta_expandida # Trayecto físico completo (FW)
            })
            
            print(f"   [OK] Beneficio: {beneficio} EUR | Tiempo: {tiempo_total}min | Eficiencia: {eficiencia:.2f} EUR/min")

        # 2. COMPARACIÓN FINAL 
        if not resultados_simulacion:
            print("\nNo se ha podido completar ninguna ruta.")
            return

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
