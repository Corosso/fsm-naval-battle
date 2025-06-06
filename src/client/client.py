import socket
from typing import Tuple, Optional
from common.logger import Logger
from common.game_logic import JuegoCliente
from common.constants import PORT

class Client:
    """
    Clase que maneja la lógica de conexión y comunicación con el servidor.
    """
    def __init__(self, host: str = 'localhost', port: int = 65432):
        """
        Inicializa el cliente con la configuración de conexión.
        
        Args:
            host (str): Dirección IP del servidor
            port (int): Puerto del servidor
        """
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.juego = JuegoCliente()
        self.logger = Logger()

    def conectar(self) -> bool:
        """
        Establece la conexión con el servidor.
        
        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario
        """
        try:
            print(f"Puerto definido en constantes: {PORT}")
            print(f"Intentando conectar a {self.host}:{self.port}")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(2)
            print("Conexión establecida exitosamente")
            print(f"Socket info: {self.socket.getpeername()}")
            self.logger.registrar_evento("conexion_establecida", {
                "host": self.host,
                "port": self.port
            })
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            self.logger.registrar_evento("error_conexion", {
                "error": str(e),
                "host": self.host,
                "port": self.port
            })
            return False

    def probar_conexion(self) -> bool:
        """
        Prueba la conexión con el servidor enviando un mensaje de prueba.
        
        Returns:
            bool: True si la prueba fue exitosa, False en caso contrario
        """
        try:
            self.socket.sendall("A0".encode())
            respuesta = self.socket.recv(1024).decode()
            self.logger.registrar_evento("prueba_conexion", {
                "respuesta": respuesta
            })
            return respuesta == "200 OK"
        except Exception as e:
            self.logger.registrar_evento("error_prueba_conexion", {
                "error": str(e)
            })
            return False

    def obtener_barcos(self) -> list:
        """
        Solicita al servidor las posiciones de los barcos.
        
        Returns:
            list: Lista de coordenadas de los barcos
        """
        try:
            self.socket.sendall("GET_SHIPS".encode())
            barcos_server = self.socket.recv(1024).decode()
            barcos = barcos_server.split(",")
            self.logger.registrar_evento("barcos_recibidos", {
                "barcos": barcos
            })
            return barcos
        except Exception as e:
            self.logger.registrar_evento("error_obtener_barcos", {
                "error": str(e)
            })
            return []

    def enviar_disparo(self, coord: str) -> str:
        """
        Envía un disparo al servidor y procesa la respuesta.
        
        Args:
            coord (str): Coordenada del disparo en formato 'A1', 'B2', etc.
            
        Returns:
            str: Respuesta del servidor
        """
        try:
            self.socket.sendall(f"DISPARO:{coord}".encode())
            respuesta = self.socket.recv(1024).decode()
            self.juego.registrar_disparo(coord, respuesta)
            self.logger.registrar_evento("disparo_enviado", {
                "coordenada": coord,
                "respuesta": respuesta
            })
            return respuesta
        except Exception as e:
            self.logger.registrar_evento("error_disparo", {
                "error": str(e),
                "coordenada": coord
            })
            return ""

    def cerrar_conexion(self):
        """
        Cierra la conexión con el servidor y registra el evento.
        """
        try:
            if self.socket:
                self.socket.sendall("CLOSE_SERVER".encode())
                self.socket.close()
                self.logger.registrar_evento("conexion_cerrada", {})
        except Exception as e:
            self.logger.registrar_evento("error_cerrar_conexion", {
                "error": str(e)
            })
