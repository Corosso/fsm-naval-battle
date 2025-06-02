#LOGICA DEL SERVIDOR PARA EL JUEGO

import pygame
import sys
import socket
from fsm_server import FSMServer
from fsm_server import Barco

HOST = 'localhost'
PORT = 65432
TILE_SIZE = 80
GRID_SIZE = 5
SCREEN_SIZE = TILE_SIZE * GRID_SIZE

def esperar_cliente(barcos):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 60))
    pygame.display.set_caption("Servidor FSM - Esperando conexión")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)

    ocupadas = set(c for barco in barcos for c in barco)

    conectado = [False]  # Será (conn, addr) cuando se conecte

    def draw_grid():
        screen.fill((0, 0, 0))
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = f"{chr(65 + fila)}{col + 1}"
                rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (0, 200, 0) if coord in ocupadas else (70, 70, 70)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        if conectado[0]:
            conn, addr = conectado[0]
            texto = font.render(f"Cliente conectado: {addr[0]}:{addr[1]}", True, (255, 255, 255))
        else:
            texto = font.render(f"Esperando conexión en {HOST}:{PORT}...", True, (255, 255, 255))
        screen.blit(texto, (10, SCREEN_SIZE + 10))

    def aceptar_conexion(socket_servidor):
        conn, addr = socket_servidor.accept()
        conectado[0] = (conn, addr)

    return screen, clock, draw_grid, conectado, aceptar_conexion



def coord_a_str(fila, col):
    return f"{chr(65 + fila)}{col + 1}"

def seleccionar_barcos():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 80))
    pygame.display.set_caption("Coloca tus 3 barcos: 1, 2 y 3 casillas")
    clock = pygame.time.Clock()

    barcos_def = [("Destroyer", 1), ("Submarine", 2), ("Battleship", 3)]
    barcos_colocados = []
    todos_ocupados = set()
    index_barco = 0
    orientacion = "H"  # H: Horizontal, V: Vertical
    mouse_hover = None

    font = pygame.font.SysFont(None, 28)

    def coord_a_str(fila, col):
        return f"{chr(65 + fila)}{col + 1}"

    def str_a_coord(coord):
        return (ord(coord[0]) - 65, int(coord[1]) - 1)

    def get_preview_coords(start_row, start_col, size, orient):
        coords = []
        for i in range(size):
            r = start_row + (i if orient == "V" else 0)
            c = start_col + (i if orient == "H" else 0)
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                coords.append(coord_a_str(r, c))
            else:
                return []  # Se sale del tablero
        return coords

    def validar_barco(coords, tamaño):
        if len(coords) != tamaño:
            return False
        filas = sorted(set(coord[0] for coord in coords))
        cols = sorted(set(coord[1] for coord in coords))
        if len(filas) == 1:
            return cols == list(range(min(cols), max(cols) + 1))
        elif len(cols) == 1:
            return filas == list(range(min(filas), max(filas) + 1))
        return False

    def draw_grid(preview_coords=None):
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = coord_a_str(fila, col)
                rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if coord in todos_ocupados:
                    color = (0, 200, 0)
                elif preview_coords and coord in preview_coords:
                    color = (255, 200, 0)
                else:
                    color = (70, 70, 70)

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        # Mensaje con nombre del barco y orientación
        if index_barco < len(barcos_def):
            nombre, tamaño = barcos_def[index_barco]
            texto = font.render(f"{nombre} ({tamaño}): orientacion {orientacion}", True, (255, 255, 255))
            screen.blit(texto, (10, SCREEN_SIZE + 10))

    running = True
    while running:
        screen.fill((30, 30, 30))

        preview_coords = []
        if mouse_hover:
            fila, col = mouse_hover
            preview_coords = get_preview_coords(fila, col, barcos_def[index_barco][1], orientacion)

        draw_grid(preview_coords)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientacion = "V" if orientacion == "H" else "H"

            elif event.type == pygame.MOUSEMOTION:
                x, y = pygame.mouse.get_pos()
                if y < SCREEN_SIZE:
                    fila = y // TILE_SIZE
                    col = x // TILE_SIZE
                    mouse_hover = (fila, col)
                else:
                    mouse_hover = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if preview_coords and all(c not in todos_ocupados for c in preview_coords):
                    coords_idx = [str_a_coord(c) for c in preview_coords]
                    if validar_barco(coords_idx, barcos_def[index_barco][1]):
                        barcos_colocados.append(preview_coords.copy())
                        todos_ocupados.update(preview_coords)
                        index_barco += 1
                        mouse_hover = None
                        if index_barco == len(barcos_def):
                            pygame.quit()
                            return list(barcos_colocados)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return list(barcos_colocados)




def main():
    barcos = seleccionar_barcos()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    screen, clock, draw_grid, conectado, aceptar_conexion = esperar_cliente(barcos)

    server_socket.setblocking(False)

    fsm = None
    conn = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            if not conectado[0]:
                aceptar_conexion(server_socket)
            else:
                conn, addr = conectado[0]
                conn.setblocking(False)
                try:
                    mensaje = conn.recv(1024).decode()
                    if mensaje:
                        print(f"[CLIENTE]: {mensaje}")
                        if mensaje == "A0":
                            conn.sendall("200 OK".encode())                        
                        elif mensaje == "GET_SHIPS":
                            # Unir todas las coordenadas de los barcos en una cadena
                            barcos_flat = [c for barco in barcos for c in barco]
                            conn.sendall(",".join(barcos_flat).encode())

                        elif mensaje.startswith("DISPARO:"):
                            if fsm is None:
                                fsm = FSMServer(barcos)
                            coord = mensaje.split(":")[1]
                            respuesta = fsm.process_message(coord)
                            conn.sendall(respuesta.encode())

                            if fsm.state == "q4":  # derrota
                                conn.sendall("FIN".encode())
                                print("Todos los barcos han sido hundidos.")


                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    print("El cliente se desconectó.")
                    conectado[0] = False
                    fsm = None
                    continue
        except BlockingIOError:
            pass

        draw_grid()
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    if conn:
        conn.close()
    server_socket.close()


if __name__ == "__main__":
    main()
