import pygame
import socket
import sys
import os
from datetime import datetime

HOST = 'localhost'
PORT = 65432
TILE_SIZE = 80
GRID_SIZE = 5
SCREEN_SIZE = TILE_SIZE * GRID_SIZE
LOGS_DIR = "logs"

#crear directorio de logs si no existe
def crear_logger():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_log = os.path.join(LOGS_DIR, f"partida_{ahora}.txt")
    return archivo_log

#funcon para escribir en el log
def escribir_log(archivo, texto):
    with open(archivo, "a") as f:
        f.write(texto + "\n")
#función para dibujar la cuadrícula
def draw_grid(screen, disparos, resultado=None):
    for fila in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            coord = f"{chr(65 + fila)}{col + 1}"
            rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if coord in disparos:
                if disparos[coord] == "HIT" or disparos[coord] == "WIN":
                    color = (255, 0, 0)
                elif disparos[coord] == "PENDING":
                    color = (100, 100, 255)
                else:
                    color = (0, 0, 255)
            else:
                color = (70, 70, 70)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    if resultado:
        font = pygame.font.SysFont(None, 36)
        text = font.render(resultado, True, (255, 255, 0))
        screen.blit(text, (20, SCREEN_SIZE + 10))


#función para mostrar el menú principal
def main_menu(screen, clock, client_socket):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    #bucle del menú principal
    while True:
        screen.fill((10, 10, 50))
        title = font.render("Batalla naval (FSM)", True, (255, 255, 255))
        screen.blit(title, (SCREEN_SIZE // 2 - title.get_width() // 2, 40))

        play_btn = pygame.Rect(SCREEN_SIZE // 2 - 100, 120, 200, 50)
        test_btn = pygame.Rect(SCREEN_SIZE // 2 - 100, 190, 200, 100)
        quit_btn = pygame.Rect(SCREEN_SIZE // 2 - 100, 310, 200, 50)

        pygame.draw.rect(screen, (0, 120, 250), play_btn)
        pygame.draw.rect(screen, (0, 200, 120), test_btn)
        pygame.draw.rect(screen, (200, 50, 50), quit_btn)
        def draw_multiline_text(text, font, color, surface, x, y, line_spacing=5):
            lines = text.split('\n')
            for i, line in enumerate(lines):
                rendered_line = font.render(line, True, color)
                surface.blit(rendered_line, (x, y + i * (rendered_line.get_height() + line_spacing)))


        screen.blit(small_font.render("JUGAR", True, (255, 255, 255)), (play_btn.x + 65, play_btn.y + 10))
        draw_multiline_text("PROBAR\nCONEXIÓN", small_font, (255, 255, 255), screen, test_btn.x + 15, test_btn.y + 10)
        screen.blit(small_font.render("SALIR", True, (255, 255, 255)), (quit_btn.x + 70, quit_btn.y + 10))
        #manejo de eventos
        for event in pygame.event.get():
            #quitar juego y cerrar conexión
            if event.type == pygame.QUIT:
                try:
                    client_socket.sendall("CLOSE_SERVER".encode())
                except:
                    pass
                pygame.quit()
                sys.exit()
            #boton de jugar
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return
                if test_btn.collidepoint(event.pos):
                    client_socket.sendall("A0".encode())
                    respuesta = client_socket.recv(1024).decode()
                    print("Respuesta de prueba:", respuesta)
                if quit_btn.collidepoint(event.pos):
                    try:
                        client_socket.sendall("CLOSE_SERVER".encode())
                    except:
                        pass
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(30)
#función principal del cliente (manejo de la interfaz gráfica y lógica del juego)
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 50))
    pygame.display.set_caption("Cliente FSM Naval Battle")
    clock = pygame.time.Clock()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
    except:
        print("No se pudo conectar al servidor.")
        pygame.quit()
        return

    while True:
        main_menu(screen, clock, client_socket)

        # Crear log para esta partida
        archivo_log = crear_logger()

        # Obtener posiciones de barcos
        client_socket.sendall("GET_SHIPS".encode())
        barcos_server = client_socket.recv(1024).decode()  # ejemplo: "A1,B3,C5,D2,E4"
        escribir_log(archivo_log, "Posiciones de barcos del servidor: " + barcos_server)

        disparos = {}
        juego_activo = True

        # Botón salir durante el juego
        exit_btn = pygame.Rect(SCREEN_SIZE - 110, SCREEN_SIZE + 10, 100, 30)
        font_btn = pygame.font.SysFont(None, 28)

        while juego_activo:
            screen.fill((20, 20, 20))
            draw_grid(screen, disparos)

            # Dibujar botón salir
            pygame.draw.rect(screen, (200, 50, 50), exit_btn)
            screen.blit(font_btn.render("Salir", True, (255, 255, 255)), (exit_btn.x + 25, exit_btn.y + 5))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    try:
                        client_socket.sendall("CLOSE_SERVER".encode())
                    except:
                        pass
                    pygame.quit()
                    client_socket.close()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_btn.collidepoint(event.pos):
                        escribir_log(archivo_log, "Jugador salió de la partida antes de terminar.")
                        juego_activo = False
                    else:
                        if len(disparos) < 25:
                            x, y = pygame.mouse.get_pos()
                            if y < SCREEN_SIZE:
                                fila = y // TILE_SIZE
                                col = x // TILE_SIZE
                                coord = f"{chr(65 + fila)}{col + 1}"
                                if coord not in disparos:
                                    disparos[coord] = "PENDING"
                                    draw_grid(screen, disparos)
                                    pygame.display.flip()

                                    client_socket.sendall(coord.encode())
                                    respuesta = client_socket.recv(1024).decode()
                                    disparos[coord] = respuesta

                                    escribir_log(archivo_log, f"Disparo en {coord}: {respuesta}")

                                    if respuesta == "WIN":
                                        escribir_log(archivo_log, "¡Jugador ganó la partida!")
                                        print("¡Ganaste!")
                                        pygame.time.delay(1000)
                                        juego_activo = False

            pygame.display.flip()
            clock.tick(30)


if __name__ == "__main__":
    main()
