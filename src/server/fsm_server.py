from typing import List, Dict, Optional
from common.game_logic import Juego, EstadoJuego, ResultadoDisparo
from common.logger import Logger

class FSMServer:
    """
    Clase que implementa la máquina de estados finitos para el servidor del juego.
    Maneja la lógica de estado y las transiciones del juego.
    """
    def __init__(self, barcos: List[List[str]]):
        """
        Inicializa la FSM del servidor.
        
        Args:
            barcos (List[List[str]]): Lista de barcos con sus coordenadas
        """
        self.juego = Juego(barcos)
        self.logger = Logger(logs_dir="logs")
        self.estado_actual = "ESPERANDO_DISPARO"
        self.ultimo_disparo: Optional[str] = None
        self.ultimo_resultado: Optional[str] = None
        self.juego_terminado = False

    def process_message(self, mensaje: str) -> str:
        """
        Procesa un mensaje recibido y determina la respuesta según el estado actual.
        
        Args:
            mensaje (str): Mensaje recibido del cliente
            
        Returns:
            str: Respuesta al cliente
        """
        self.logger.registrar_evento("mensaje_recibido", {
            "estado_actual": self.estado_actual,
            "mensaje": mensaje
        })

        if self.estado_actual == "ESPERANDO_DISPARO":
            return self._procesar_disparo(mensaje)
        else:
            return "400 Bad Request"

    def _procesar_disparo(self, coord: str) -> str:
        """
        Procesa un disparo recibido y actualiza el estado del juego.
        
        Args:
            coord (str): Coordenada del disparo (ej: "A1")
            
        Returns:
            str: Código de respuesta según el resultado
        """
        self.ultimo_disparo = coord
        resultado = self.juego.procesar_disparo(coord)
        self.ultimo_resultado = resultado.value

        # Registrar el resultado del disparo
        self.logger.registrar_evento("disparo_procesado", {
            "coordenada": coord,
            "resultado": resultado.value,
            "estado_juego": self.juego.estado.value
        })

        # Determinar el código de respuesta según el resultado
        if resultado == ResultadoDisparo.VICTORIA:
            self.juego_terminado = True
            return "500 GAME OVER"
        elif resultado == ResultadoDisparo.HUNDIDO:
            return "200 HUNDIDO"
        elif resultado == ResultadoDisparo.IMPACTADO:
            return "202 IMPACTO"
        else:
            return "404 AGUA"

    def obtener_estado_actual(self) -> Dict:
        """
        Obtiene el estado actual del juego.
        
        Returns:
            Dict: Diccionario con el estado actual
        """
        return {
            "estado": self.estado_actual,
            "ultimo_disparo": self.ultimo_disparo,
            "ultimo_resultado": self.ultimo_resultado,
            "estado_juego": self.juego.estado.value
        }

    def obtener_barcos(self) -> List[List[str]]:
        """
        Obtiene la lista de barcos y su estado.
        
        Returns:
            List[List[str]]: Lista de barcos con sus coordenadas
        """
        return self.juego.barcos
