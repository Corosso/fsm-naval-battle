import socket
import sys
from typing import List, Tuple, Set
from common.constants import *
from common.logger import Logger
from .fsm_server import FSMServer
from .gui import ServerGUI
import pygame

class Server:
    """
    Clase que maneja la lógica del servidor del juego.
    """
    def __init__(self):
        """
        Inicializa el servidor con sus componentes.
        """
        pygame.init()
        self.gui = ServerGUI()
        self.logger = Logger(logs_dir=LOGS_DIR)
        self.impactos_recibidos = {}  # coord -> código de resultado
        self.ultimo_disparo = ""      # texto a mostrar debajo
        self.fsm = None
        self.conn = None
        self.addr = None

    def __del__(self):
        """
        Limpieza al destruir la instancia.
        """
        pygame.quit()

    def seleccionar_barcos(self) -> List[List[str]]:
        """
        Permite al usuario colocar los barcos en el tablero.
        
        Returns:
            List[List[str]]: Lista de barcos colocados
        """
        barcos_def = [("Destroyer", 1), ("Submarine", 2), ("Battleship", 3)]
        barcos_colocados = []
        todos_ocupados = set()
        index_barco = 0
        orientacion = "H"  # H: Horizontal, V: Vertical
        mouse_hover = None

        def coord_a_str(fila: int, col: int) -> str:
            return f"{chr(65 + fila)}{col + 1}"

        def str_a_coord(coord: str) -> Tuple[int, int]:
            return (ord(coord[0]) - 65, int(coord[1]) - 1)

        def get_preview_coords(start_row: int, start_col: int, size: int, orient: str) -> List[str]:
            coords = []
            for i in range(size):
                r = start_row + (i if orient == "V" else 0)
                c = start_col + (i if orient == "H" else 0)
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    coords.append(coord_a_str(r, c))
                else:
                    return []
            return coords

        def validar_barco(coords_idx: List[Tuple[int, int]], tamaño: int) -> bool:
            if len(coords_idx) != tamaño:
                return False
            filas_set = set(r for r, c in coords_idx)
            cols_set = set(c for r, c in coords_idx)

            if len(filas_set) == 1:  # Horizontal
                return len(cols_set) == tamaño and (max(cols_set) - min(cols_set) + 1) == tamaño
            elif len(cols_set) == 1:  # Vertical
                return len(filas_set) == tamaño and (max(filas_set) - min(filas_set) + 1) == tamaño
            return False

        running = True
        while running:
            preview_coords = []
            if mouse_hover:
                fila_logic, col_logic = mouse_hover
                preview_coords = get_preview_coords(fila_logic, col_logic, 
                                                  barcos_def[index_barco][1], 
                                                  orientacion)

            self.gui.draw_grid_placement(todos_ocupados, preview_coords, 
                                       index_barco, barcos_def, orientacion)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return list(barcos_colocados)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        orientacion = "V" if orientacion == "H" else "H"

                elif event.type == pygame.MOUSEMOTION:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (mouse_x > HEADER_OFFSET and mouse_y > HEADER_OFFSET and 
                        mouse_x < SCREEN_WIDTH_GAME and mouse_y < (SCREEN_HEIGHT_GAME - 60)):
                        fila = (mouse_y - HEADER_OFFSET) // TILE_SIZE
                        col = (mouse_x - HEADER_OFFSET) // TILE_SIZE
                        if 0 <= fila < GRID_SIZE and 0 <= col < GRID_SIZE:
                            mouse_hover = (fila, col)
                        else:
                            mouse_hover = None
                    else:
                        mouse_hover = None

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if preview_coords and all(c not in todos_ocupados for c in preview_coords):
                        coords_idx_for_validation = [str_a_coord(c) for c in preview_coords]
                        if validar_barco(coords_idx_for_validation, barcos_def[index_barco][1]):
                            barcos_colocados.append(preview_coords.copy())
                            todos_ocupados.update(preview_coords)
                            index_barco += 1
                            mouse_hover = None
                            if index_barco == len(barcos_def):
                                return list(barcos_colocados)

            self.gui.update_display()

        return list(barcos_colocados)

    def main(self):
        """
        Función principal que ejecuta el servidor.
        """
        barcos = self.seleccionar_barcos()
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        
        self.logger.registrar_evento("inicio_servidor", {
            "host": HOST,
            "port": PORT
        })

        ocupadas = set(c for barco in barcos for c in barco)
        conectado = [False]

        server_socket.setblocking(False)
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            try:
                if not conectado[0]:
                    try:
                        self.conn, self.addr = server_socket.accept()
                        conectado[0] = (self.conn, self.addr)
                        self.logger.registrar_evento("nueva_conexion", {
                            "addr": f"{self.addr[0]}:{self.addr[1]}"
                        })
                    except BlockingIOError:
                        pass
                else:
                    self.conn, self.addr = conectado[0]
                    self.conn.setblocking(False)
                    try:
                        mensaje = self.conn.recv(1024).decode()
                        if mensaje:
                            self.logger.registrar_evento("mensaje_recibido", {
                                "mensaje": mensaje,
                                "addr": f"{self.addr[0]}:{self.addr[1]}"
                            })
                            
                            if mensaje == "A0":
                                self.conn.sendall("200 OK".encode())
                            elif mensaje == "GET_SHIPS":
                                barcos_flat = [c for barco in barcos for c in barco]
                                self.conn.sendall(",".join(barcos_flat).encode())
                                self.logger.registrar_evento("barcos_enviados", {
                                    "addr": f"{self.addr[0]}:{self.addr[1]}",
                                    "barcos": barcos_flat
                                })
                            elif mensaje.startswith("DISPARO:"):
                                if self.fsm is None:
                                    self.fsm = FSMServer(barcos)
                                coord = mensaje.split(":")[1]
                                respuesta = self.fsm.process_message(coord)
                                self.impactos_recibidos[coord] = respuesta
                                self.ultimo_disparo = f"Disparo en {coord} → {respuesta}"
                                self.conn.sendall(respuesta.encode())
                                self.logger.registrar_evento("disparo_procesado", {
                                    "addr": f"{self.addr[0]}:{self.addr[1]}",
                                    "coordenada": coord,
                                    "respuesta": respuesta
                                })

                                if self.fsm.juego.estado == EstadoJuego.DERROTA:
                                    self.conn.sendall("FIN".encode())
                                    self.logger.registrar_evento("juego_terminado", {
                                        "addr": f"{self.addr[0]}:{self.addr[1]}",
                                        "razon": "derrota",
                                        "estado": self.fsm.juego.estado.value
                                    })

                    except BlockingIOError:
                        pass
                    except ConnectionResetError:
                        self.logger.registrar_evento("error", {
                            "tipo": "conexion",
                            "addr": f"{self.addr[0]}:{self.addr[1]}" if self.addr else "desconocido",
                            "mensaje": "Cliente desconectado"
                        })
                        conectado[0] = False
                        self.fsm = None
                        continue

            except BlockingIOError:
                pass

            self.gui.draw_grid_server(self.impactos_recibidos, ocupadas, 
                                    conectado, self.ultimo_disparo)
            self.gui.update_display()

        # Registrar el cierre del servidor
        self.logger.registrar_evento("servidor_cerrado", {
            "razon": "usuario",
            "estado_final": self.fsm.juego.estado.value if self.fsm else "no_iniciado"
        })

        pygame.quit()
        if self.conn:
            self.conn.close()
        server_socket.close()

def main():
    """
    Punto de entrada principal del servidor.
    """
    server = Server()
    server.main()

if __name__ == "__main__":
    main()
