# Importamos nuestros dos módulos
from dp_seleccion import seleccion_pedidos_dp
from backtracking_ruta import calcular_ruta_optima_tsp

# main.py
from dp_seleccion import seleccion_pedidos_dp
from backtracking_ruta import calcular_ruta_optima_tsp

def ejecutar_sistema_logistico():
    """Sistema de optimización logística con DP + Backtracking."""
    
    # ========================================================
    # 1. DATOS INICIALES
    # ========================================================
    capacidad_camion = 8  # kg
    
    # Formato: (ID, peso_kg, beneficio_euros)
    pedidos_disponibles = [
        ("P1", 2, 10),
        ("P2", 3, 15),
        ("P3", 4, 30),
        ("P4", 5, 20)
    ]
    
    # Matriz de distancias (km)
    # Nodos: 0=Almacén, 1=P1, 2=P2, 3=P3, 4=P4
    matriz_distancias = [
        [0, 5, 2, 8, 1],  # Desde Almacén
        [5, 0, 3, 4, 6],  # Desde P1
        [2, 3, 0, 7, 2],  # Desde P2
        [8, 4, 7, 0, 5],  # Desde P3
        [1, 6, 2, 5, 0]   # Desde P4
    ]
    
    # Mapeo ID_pedido -> Índice_nodo
    mapa_nodos = {"P1": 1, "P2": 2, "P3": 3, "P4": 4}
    
    # ========================================================
    # 2. MÓDULO DE SELECCIÓN (Programación Dinámica)
    # ========================================================
    print("\n🔍 FASE 1: Selección de pedidos (Mochila)")
    beneficio, pedidos_seleccionados = seleccion_pedidos_dp(
        pedidos_disponibles, 
        capacidad_camion
    )
    
    if not pedidos_seleccionados:
        print("⚠️ Ningún pedido cabe en el camión. Operación cancelada.")
        return
    
    peso_usado = sum(p[1] for p in pedidos_disponibles if p[0] in pedidos_seleccionados)
    print(f"   ✓ Pedidos seleccionados: {pedidos_seleccionados}")
    print(f"   ✓ Capacidad usada: {peso_usado}/{capacidad_camion} kg")
    print(f"   ✓ Beneficio esperado: {beneficio}€")
    
    # ========================================================
    # 3. TRADUCCIÓN: Pedidos → Nodos del grafo
    # ========================================================
    nodos_a_visitar = [0]  # Siempre empezamos en el almacén
    for pedido_id in pedidos_seleccionados:
        nodos_a_visitar.append(mapa_nodos[pedido_id])
    
    print(f"\n🗺️  Nodos a visitar: {nodos_a_visitar}")
    
    # ========================================================
    # 4. MÓDULO DE RUTA (Backtracking - TSP)
    # ========================================================
    print("\n🚚 FASE 2: Cálculo de ruta óptima (TSP)")
    distancia_minima, mejor_ruta = calcular_ruta_optima_tsp(
        matriz_distancias, 
        nodos_a_visitar
    )
    
    print(f"   ✓ Ruta óptima: {mejor_ruta}")
    print(f"   ✓ Distancia total: {distancia_minima} km")
    
    # ========================================================
    # 5. RESUMEN FINAL
    # ========================================================
    print(f"\n{'='*50}")
    print(f"📊 RESUMEN DE LA OPERACIÓN")
    print(f"{'='*50}")
    print(f"   Beneficio: {beneficio}€")
    print(f"   Distancia: {distancia_minima} km")
    print(f"   Eficiencia: {beneficio/distancia_minima:.2f} €/km")
    print(f"{'='*50}\n")


def test_integracion():
    """Prueba rápida del flujo completo."""
    # Caso trivial: 1 pedido que cabe justo
    cap = 5
    pedidos = [("P1", 5, 10)]
    matriz = [[0, 3], [3, 0]]
    mapa = {"P1": 1}
    
    ben, sel = seleccion_pedidos_dp(pedidos, cap)
    assert sel == ["P1"], f"DP falló: {sel}"
    
    nodos = [0] + [mapa[p] for p in sel]
    dist, ruta = calcular_ruta_optima_tsp(matriz, nodos)
    assert ruta == [0, 1] or ruta == [0, 1, 0], f"TSP falló: {ruta}"
    
    print("✅ Test de integración pasado")

# test_integracion()  # Descomentar para probar

if __name__ == "__main__":
    ejecutar_sistema_logistico()