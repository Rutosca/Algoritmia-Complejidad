import sys
import os

# Añadir la carpeta src al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dp_seleccion import seleccion_pedidos_dp

def test_seleccion_basica():
    """Prueba que el algoritmo de DP maximice el beneficio sin pasarse de peso ni volumen."""
    # Formato: (id, peso, volumen, beneficio)
    pedidos = [
        ("P1", 2, 3, 10),
        ("P2", 3, 2, 15),
        ("P3", 5, 2, 20)
    ]
    cap_peso = 5
    cap_vol = 5
    
    # Opciones:
    # P1 + P2 = peso 5, vol 5 -> Beneficio = 25 (Cabe perfecto)
    # P3 = peso 5, vol 2 -> Beneficio = 20
    # Por tanto, debe elegir P1 y P2.
    beneficio, seleccion = seleccion_pedidos_dp(pedidos, cap_peso, cap_vol)
    
    assert beneficio == 25, f"Error: beneficio esperado 25, obtenido {beneficio}"
    assert set(seleccion) == {"P1", "P2"}, f"Error: selección esperada {{'P1', 'P2'}}, obtenida {set(seleccion)}"
    print("[OK] test_seleccion_basica superado")
    
def test_sin_pedidos_que_quepan():
    """Prueba qué pasa si ningún pedido cabe en el vehículo."""
    pedidos = [
        ("P1", 10, 10, 50)
    ]
    beneficio, seleccion = seleccion_pedidos_dp(pedidos, 5, 5)
    
    assert beneficio == 0, f"Error: beneficio esperado 0, obtenido {beneficio}"
    assert seleccion == [], f"Error: selección esperada [], obtenida {seleccion}"
    print("[OK] test_sin_pedidos_que_quepan superado")

def test_mochila_vacia():
    """Prueba comportamiento con lista de pedidos vacía."""
    beneficio, seleccion = seleccion_pedidos_dp([], 10, 10)
    assert beneficio == 0, f"Error: beneficio esperado 0, obtenido {beneficio}"
    assert seleccion == [], f"Error: selección esperada [], obtenida {seleccion}"
    print("[OK] test_mochila_vacia superado")

if __name__ == '__main__':
    print("Ejecutando tests de dp_seleccion...")
    test_seleccion_basica()
    test_sin_pedidos_que_quepan()
    test_mochila_vacia()
    print("Todos los tests de dp_seleccion han pasado correctamente.")
