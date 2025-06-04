import sys
import os

# Añadir el directorio src al path de Python
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """
    Punto de entrada principal del juego.
    Permite elegir entre ejecutar el servidor o el cliente.
    """
    print("Bienvenido a FSM Naval Battle")
    print("1. Iniciar Servidor")
    print("2. Iniciar Cliente")
    
    opcion = input("Seleccione una opción (1/2): ")
    
    if opcion == "1":
        from server.server import main as server_main
        server_main()
    elif opcion == "2":
        from client.gui import main as client_main
        client_main()
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()
