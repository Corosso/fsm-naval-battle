from enum import Enum
from typing import List, Set, Optional, Tuple

class EstadoJuego(Enum):
    FLOTA_INTACTA = "q1"
    BARCO_IMPACTADO = "q2"
    BARCO_HUNDIDO = "q3"
    DERROTA = "q4"

class ResultadoDisparo(Enum):
    OK = "200 OK"
    IMPACTADO = "202-impactado"
    HUNDIDO = "200-hundido"
    VICTORIA = "500-hundido"
    FALLO = "404-fallido"
    NO_ENCONTRADO = "404 Not Found"

class Barco:
    def __init__(self, coordenadas: List[str]):
        self.coordenadas: Set[str] = set(coordenadas)
        self.impactos: Set[str] = set()

    def recibir_impacto(self, coord: str) -> bool:
        """
        Registra un impacto en el barco.
        
        Args:
            coord: Coordenada del impacto (ej: "A1")
            
        Returns:
            bool: True si el impacto fue en el barco, False en caso contrario
        """
        if coord in self.coordenadas:
            self.impactos.add(coord)
            return True
        return False

    def esta_hundido(self) -> bool:
        """
        Verifica si el barco ha sido hundido.
        
        Returns:
            bool: True si todas las coordenadas del barco han sido impactadas
        """
        return self.coordenadas == self.impactos

class Juego:
    """
    Clase que maneja la lógica principal del juego en el servidor.
    Gestiona el estado del juego, los barcos y los disparos.
    """

    def __init__(self, barcos: List[List[str]]):
        """
        Inicializa una nueva instancia del juego.
        
        Args:
            barcos (List[List[str]]): Lista de barcos, donde cada barco es una lista
                de coordenadas en formato 'A1', 'B2', etc.
        """
        self.estado = EstadoJuego.FLOTA_INTACTA
        self.barcos = [Barco(coords) for coords in barcos]
        self.historial: Set[str] = set()
        self.coordenadas_validas = self._generar_coordenadas_validas()

    def _generar_coordenadas_validas(self) -> Set[str]:
        """Genera el conjunto de coordenadas válidas para el tablero."""
        return {f"{chr(r)}{c}" for r in range(65, 70) for c in range(1, 6)}

    def procesar_disparo(self, coord: str) -> ResultadoDisparo:
        """
        Procesa un disparo en una coordenada específica.
        
        Args:
            coord (str): Coordenada del disparo en formato 'A1', 'B2', etc.
            
        Returns:
            ResultadoDisparo: Resultado del disparo (AGUA, IMPACTO, HUNDIDO)
        """
        if coord == "A0":  # Mensaje de prueba
            return ResultadoDisparo.OK
            
        if coord == "GET_SHIPS":  # Solicitud de posiciones
            todas = [c for barco in self.barcos for c in barco.coordenadas]
            return ",".join(sorted(todas))

        if coord not in self.coordenadas_validas:
            return ResultadoDisparo.NO_ENCONTRADO
            
        if coord in self.historial:
            return ResultadoDisparo.FALLO

        self.historial.add(coord)

        for barco in self.barcos:
            if barco.recibir_impacto(coord):
                if barco.esta_hundido():
                    if all(b.esta_hundido() for b in self.barcos):
                        self.estado = EstadoJuego.DERROTA
                        return ResultadoDisparo.VICTORIA
                    else:
                        self.estado = EstadoJuego.BARCO_HUNDIDO
                        return ResultadoDisparo.HUNDIDO
                else:
                    self.estado = EstadoJuego.BARCO_IMPACTADO
                    return ResultadoDisparo.IMPACTADO

        return ResultadoDisparo.FALLO

class JuegoCliente:
    """
    Clase que maneja la lógica del juego en el cliente.
    Gestiona el estado del tablero y la interacción con el servidor.
    """

    def __init__(self):
        """
        Inicializa una nueva instancia del juego del cliente.
        Crea un tablero vacío y establece el estado inicial.
        """
        self.disparos = {}  # coord -> código de resultado
        self.coordenadas_validas = self._generar_coordenadas_validas()
        self.juego_activo = True

    def _generar_coordenadas_validas(self) -> Set[str]:
        """Genera el conjunto de coordenadas válidas para el tablero."""
        return {f"{chr(r)}{c}" for r in range(65, 70) for c in range(1, 6)}

    def coord_a_str(self, fila: int, col: int) -> str:
        """
        Convierte coordenadas numéricas a formato de string.
        
        Args:
            fila (int): Número de fila (0-4)
            col (int): Número de columna (0-4)
            
        Returns:
            str: Coordenada en formato 'A1', 'B2', etc.
        """
        return f"{chr(65 + fila)}{col + 1}"

    def str_a_coord(self, coord: str) -> Tuple[int, int]:
        """
        Convierte una coordenada en formato string a coordenadas numéricas.
        
        Args:
            coord (str): Coordenada en formato 'A1', 'B2', etc.
            
        Returns:
            Tuple[int, int]: Tupla (fila, columna) en formato numérico
        """
        return (ord(coord[0]) - 65, int(coord[1]) - 1)

    def es_coordenada_valida(self, coord: str) -> bool:
        """
        Verifica si una coordenada es válida para el tablero.
        
        Args:
            coord: Coordenada a verificar
            
        Returns:
            bool: True si la coordenada es válida
        """
        return coord in self.coordenadas_validas

    def registrar_disparo(self, coord: str, resultado: str):
        """
        Registra el resultado de un disparo en el tablero.
        
        Args:
            coord (str): Coordenada del disparo
            resultado (str): Resultado del disparo recibido del servidor
        """
        self.disparos[coord] = resultado
        if resultado.startswith("500"):  # Victoria
            self.juego_activo = False

    def obtener_color_celda(self, coord: str) -> Tuple[int, int, int]:
        """
        Obtiene el color correspondiente a una celda según su estado.
        
        Args:
            coord (str): Coordenada de la celda
            
        Returns:
            Tuple[int, int, int]: Color RGB de la celda
        """
        if coord not in self.disparos:
            return (70, 70, 70)  # COLOR_GRID_EMPTY
            
        resultado = self.disparos[coord]
        if resultado.startswith("202"):
            return (255, 200, 0)  # COLOR_GRID_HIT
        elif resultado.startswith("200") or resultado.startswith("500"):
            return (255, 0, 0)    # COLOR_GRID_SUNK
        elif resultado == "PENDING":
            return (100, 100, 255)  # COLOR_GRID_PENDING
        elif resultado.startswith("404"):
            return (0, 0, 255)    # COLOR_GRID_MISS
        else:
            return (120, 120, 120)  # COLOR_GRID_FAILED

    def puede_disparar(self, coord: str) -> bool:
        """
        Verifica si se puede realizar un disparo en la coordenada especificada.
        
        Args:
            coord (str): Coordenada a verificar
            
        Returns:
            bool: True si se puede disparar, False en caso contrario
        """
        return coord not in self.disparos and self.es_coordenada_valida(coord)

