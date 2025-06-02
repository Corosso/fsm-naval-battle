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

# --- NUEVAS CONSTANTES PARA EL TAMAÑO DE LA PANTALLA Y EL OFFSET ---
HEADER_OFFSET = TILE_SIZE # Espacio para números y letras (igual al tamaño de una celda)
SCREEN_WIDTH_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET # Ancho del tablero + espacio para letras
SCREEN_HEIGHT_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET + 60 # Alto del tablero + espacio para números + espacio para mensajes/botones
# -------------------------------------------------------------------
impactos_recibidos = {}  # coord -> código de resultado
ultimo_disparo = ""      # texto a mostrar debajo


def esperar_cliente(barcos):
    pygame.init()
    # Usamos las nuevas constantes de tamaño para la ventana del juego
    screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
    pygame.display.set_caption("Servidor FSM - Esperando conexión")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    font_header = pygame.font.SysFont(None, 24) # Fuente más pequeña para encabezados

    ocupadas = set(c for barco in barcos for c in barco)

    conectado = [False]  # Será (conn, addr) cuando se conecte

    def draw_grid_server(): # Renombrado para claridad, ya que tendrás otra draw_grid
        screen.fill((0, 0, 200))

        # --- DIBUJAR NÚMEROS (ENCABEZADOS DE COLUMNA) ---
        for col in range(GRID_SIZE):
            text_surface = font_header.render(str(col + 1), True, (255, 255, 255))
            screen.blit(text_surface, (HEADER_OFFSET + col * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_width() // 2,
                                       HEADER_OFFSET // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR LETRAS (ENCABEZADOS DE FILA) ---
        for fila in range(GRID_SIZE):
            text_surface = font_header.render(chr(65 + fila), True, (255, 255, 255))
            screen.blit(text_surface, (HEADER_OFFSET // 2 - text_surface.get_width() // 2,
                                       HEADER_OFFSET + fila * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR EL TABLERO PROPIAMENTE DICHO ---
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = f"{chr(65 + fila)}{col + 1}"
                # Ajustamos la posición de dibujo de cada celda para el offset
                rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, HEADER_OFFSET + fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if coord in impactos_recibidos:
                    resultado = impactos_recibidos[coord]
                    if resultado.startswith("500") or resultado.startswith("200"):
                        color = (255, 0, 0)  # hundido
                    elif resultado.startswith("202"):
                        color = (255, 200, 0)  # impacto
                    else:
                        color = (50, 50, 255)  # agua
                elif coord in ocupadas:
                    color = (0, 200, 0)  # barco sin tocar
                else:
                    color = (70, 70, 70)  # vacío

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        # --- MENSAJES DE ESTADO (ABAJO DEL TABLERO) ---
        if conectado[0]:
            conn, addr = conectado[0]
            texto = font.render(f"Cliente conectado: {addr[0]}:{addr[1]}", True, (255, 255, 255))
        else:
            texto = font.render(f"Esperando conexión en {HOST}:{PORT}...", True, (255, 255, 255))
        # Ajustamos la posición para que esté debajo del tablero y los encabezados
        screen.blit(texto, (10, SCREEN_HEIGHT_GAME - 50)) # Ajusta este 50 si necesitas más espacio

        if ultimo_disparo:
            texto_disparo = font.render(ultimo_disparo, True, (255, 255, 0))
            # Ajustamos la posición para que esté debajo del mensaje anterior
            screen.blit(texto_disparo, (10, SCREEN_HEIGHT_GAME - 25))


    def aceptar_conexion(socket_servidor):
        conn, addr = socket_servidor.accept()
        conectado[0] = (conn, addr)

    # Devolvemos la nueva función de dibujo
    return screen, clock, draw_grid_server, conectado, aceptar_conexion

def seleccionar_barcos():
    pygame.init()
    # Usamos las nuevas constantes de tamaño para la ventana del juego
    screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
    pygame.display.set_caption("Coloca tus 3 barcos: 1, 2 y 3 casillas")
    clock = pygame.time.Clock()

    barcos_def = [("Destroyer", 1), ("Submarine", 2), ("Battleship", 3)]
    barcos_colocados = []
    todos_ocupados = set()
    index_barco = 0
    orientacion = "H"  # H: Horizontal, V: Vertical
    mouse_hover = None

    font = pygame.font.SysFont(None, 28)
    font_header = pygame.font.SysFont(None, 24) # Fuente más pequeña para encabezados

    def coord_a_str(fila, col):
        return f"{chr(65 + fila)}{col + 1}"

    def str_a_coord(coord):
        return (ord(coord[0]) - 65, int(coord[1]) - 1)

    def get_preview_coords(start_row, start_col, size, orient):
        coords = []
        for i in range(size):
            r = start_row + (i if orient == "V" else 0)
            c = start_col + (i if orient == "H" else 0)
            # Asegurarse de que la previsualización no salga de la cuadrícula
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                coords.append(coord_a_str(r, c))
            else:
                return []  # Se sale del tablero
        return coords

    # No estoy seguro de dónde usas validar_barco, pero asegúrate que las coordenadas
    # que le pasas ya sean las lógicas (0-indexed). Si vienen de un clic, necesitan el offset.
    def validar_barco(coords_idx, tamaño): # Cambiado para aceptar coords_idx directamente
        if len(coords_idx) != tamaño:
            return False
        filas_set = set(r for r, c in coords_idx)
        cols_set = set(c for r, c in coords_idx)

        # Check for single row or single column alignment
        if len(filas_set) == 1: # Horizontal
            return len(cols_set) == tamaño and (max(cols_set) - min(cols_set) + 1) == tamaño
        elif len(cols_set) == 1: # Vertical
            return len(filas_set) == tamaño and (max(filas_set) - min(filas_set) + 1) == tamaño
        return False

    def draw_grid_placement(preview_coords=None): # Renombrado
        screen.fill((0, 0, 200))

        # --- DIBUJAR NÚMEROS (ENCABEZADOS DE COLUMNA) ---
        for col in range(GRID_SIZE):
            text_surface = font_header.render(str(col + 1), True, (255, 255, 255))
            screen.blit(text_surface, (HEADER_OFFSET + col * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_width() // 2,
                                       HEADER_OFFSET // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR LETRAS (ENCABEZADOS DE FILA) ---
        for fila in range(GRID_SIZE):
            text_surface = font_header.render(chr(65 + fila), True, (255, 255, 255))
            screen.blit(text_surface, (HEADER_OFFSET // 2 - text_surface.get_width() // 2,
                                       HEADER_OFFSET + fila * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_height() // 2))


        # --- DIBUJAR EL TABLERO PROPIAMENTE DICHO ---
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = coord_a_str(fila, col)
                # Ajustamos la posición de dibujo de cada celda para el offset
                rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, HEADER_OFFSET + fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                if coord in todos_ocupados:
                    color = (0, 200, 0) # Barco ya colocado
                elif preview_coords and coord in preview_coords:
                    color = (255, 200, 0) # Previsualización del barco
                else:
                    color = (70, 70, 70) # Espacio vacío

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        # Mensaje con nombre del barco y orientación (abajo del tablero)
        if index_barco < len(barcos_def):
            nombre, tamaño = barcos_def[index_barco]
            texto = font.render(f"{nombre} ({tamaño}): orientacion {orientacion}", True, (255, 255, 255))
            screen.blit(texto, (10, SCREEN_HEIGHT_GAME - 50)) # Ajusta la posición

    running = True
    while running:
       

        preview_coords = []
        if mouse_hover:
            # get_preview_coords ya espera filas/columnas lógicas
            fila_logic, col_logic = mouse_hover
            preview_coords = get_preview_coords(fila_logic, col_logic, barcos_def[index_barco][1], orientacion)

        draw_grid_placement(preview_coords) # Llamamos a la función renombrada

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientacion = "V" if orientacion == "H" else "H"

            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # ¡Importante! Resta el HEADER_OFFSET para obtener las coordenadas lógicas
                if mouse_x > HEADER_OFFSET and mouse_y > HEADER_OFFSET and \
                   mouse_x < SCREEN_WIDTH_GAME and mouse_y < (SCREEN_HEIGHT_GAME - 60): # Limita el área de hover
                    fila = (mouse_y - HEADER_OFFSET) // TILE_SIZE
                    col = (mouse_x - HEADER_OFFSET) // TILE_SIZE
                    # Asegúrate de que las coordenadas estén dentro del GRID_SIZE
                    if 0 <= fila < GRID_SIZE and 0 <= col < GRID_SIZE:
                        mouse_hover = (fila, col)
                    else:
                        mouse_hover = None
                else:
                    mouse_hover = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if preview_coords and all(c not in todos_ocupados for c in preview_coords):
                    # Validamos las coordenadas lógicas, no las de píxeles
                    # Las 'preview_coords' ya están en formato 'A1', 'B2', etc.
                    # Necesitamos convertirlas a (fila, col) para 'validar_barco'
                    coords_idx_for_validation = [str_a_coord(c) for c in preview_coords]
                    
                    if validar_barco(coords_idx_for_validation, barcos_def[index_barco][1]):
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
                            global impactos_recibidos, ultimo_disparo
                            if fsm is None:
                                fsm = FSMServer(barcos)
                            coord = mensaje.split(":")[1]
                            respuesta = fsm.process_message(coord)
                            impactos_recibidos[coord] = respuesta
                            ultimo_disparo = f"Disparo en {coord} → {respuesta}"
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
