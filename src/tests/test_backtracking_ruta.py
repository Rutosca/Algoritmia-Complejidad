import sys
import os

# Añadir la carpeta src al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtracking_ruta import calcular_ruta_optima_tsp

def test_ruta_basica_triangulo():
    """Prueba una ruta sencilla de 3 nodos (0, 1, 2) y vuelta al origen."""
    # Matriz de distancias 3x3
    dist_fw = [
        [0, 10, 15],
        [10, 0,  5],
        [15, 5,  0]
    ]
    nodos_a_visitar = [0, 1, 2]
    
    # Opciones desde el almacén (0):
    # 0 -> 1 -> 2 -> 0 = 10 + 5 + 15 = 30
    # 0 -> 2 -> 1 -> 0 = 15 + 5 + 10 = 30
    coste, ruta, metricas = calcular_ruta_optima_tsp(dist_fw, nodos_a_visitar)
    
    assert coste == 30.0, f"Error: coste esperado 30.0, obtenido {coste}"
    assert ruta in ([0, 1, 2, 0], [0, 2, 1, 0]), f"Error: ruta incorrecta {ruta}"
    print("[OK] test_ruta_basica_triangulo superado")

def test_un_solo_destino():
    """Prueba una ruta donde solo hay que ir a un sitio y volver."""
    dist_fw = [
        [0, 10],
        [10, 0]
    ]
    nodos_a_visitar = [0, 1]
    coste, ruta, metricas = calcular_ruta_optima_tsp(dist_fw, nodos_a_visitar)
    
    assert coste == 20.0, f"Error: coste esperado 20.0, obtenido {coste}"
    assert ruta == [0, 1, 0], f"Error: ruta esperada [0, 1, 0], obtenida {ruta}"
    print("[OK] test_un_solo_destino superado")

def test_almacen_vacio():
    """Prueba qué pasa si no hay destinos."""
    dist_fw = [[0]]
    nodos_a_visitar = [0]
    coste, ruta, metricas = calcular_ruta_optima_tsp(dist_fw, nodos_a_visitar)
    
    assert coste == 0.0, f"Error: coste esperado 0.0, obtenido {coste}"
    assert ruta == [0, 0], f"Error: ruta esperada [0, 0], obtenida {ruta}"
    print("[OK] test_almacen_vacio superado")

if __name__ == '__main__':
    print("Ejecutando tests de backtracking_ruta...")
    test_ruta_basica_triangulo()
    test_un_solo_destino()
    test_almacen_vacio()
    print("Todos los tests de backtracking_ruta han pasado correctamente.")
