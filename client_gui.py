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

def crear_logger():
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    ahora = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_log = os.path.join(LOGS_DIR, f"partida_{ahora}.txt")
    return archivo_log

def escribir_log(archivo, texto):
    with open(archivo, "a") as f:
        f.write(texto + "\n")

def draw_grid(screen, disparos, resultado=None):
    for fila in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            coord = f"{chr(65 + fila)}{col + 1}"
            respuesta = disparos.get(coord)

            if respuesta:
                if respuesta.startswith("202"):
                    color = (255, 200, 0)  # impacto
                elif respuesta.startswith("200") or respuesta.startswith("500"):
                    color = (255, 0, 0)  # hundido
                elif respuesta == "PENDING":
                    color = (100, 100, 255)
                elif respuesta.startswith("404"):
                    color = (0, 0, 255)  # agua
                else:
                    color = (50, 50, 50)
            else:
                color = (70, 70, 70)

            rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    if resultado:
        font = pygame.font.SysFont(None, 36)
        text = font.render(resultado, True, (255, 255, 0))
        screen.blit(text, (20, SCREEN_SIZE + 10))

def main_menu(screen, clock, client_socket):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    client_socket.sendall("CLOSE_SERVER".encode())
                except:
                    pass
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn.collidepoint(event.pos):
                    return
                if test_btn.collidepoint(event.pos):
                    try:
                        client_socket.settimeout(2)
                        client_socket.sendall("A0".encode())
                        respuesta = client_socket.recv(1024).decode()
                        print("Respuesta de prueba:", respuesta)
                    except socket.timeout:
                        print("Timeout: El servidor no respondió a la prueba de conexión.")
                    except Exception as e:
                        print("Error durante la prueba de conexión:", e)
                    finally:
                        client_socket.settimeout(2)  # aseguramos que siga en 2s
                if quit_btn.collidepoint(event.pos):
                    try:
                        client_socket.sendall("CLOSE_SERVER".encode())
                    except:
                        pass
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(30)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 50))
    pygame.display.set_caption("Cliente FSM Naval Battle")
    clock = pygame.time.Clock()

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_socket.settimeout(2)  # evita bloqueo total si el servidor no responde
    except:
        print("No se pudo conectar al servidor.")
        pygame.quit()
        return

    while True:
        main_menu(screen, clock, client_socket)

        archivo_log = crear_logger()
        
        client_socket.sendall("GET_SHIPS".encode())

        barcos_server = client_socket.recv(1024).decode()
        
        escribir_log(archivo_log, "Posiciones de barcos del servidor: " + barcos_server)

        disparos = {}
        juego_activo = True
        exit_btn = pygame.Rect(SCREEN_SIZE - 110, SCREEN_SIZE + 10, 100, 30)
        font_btn = pygame.font.SysFont(None, 28)

        while juego_activo:
            screen.fill((20, 20, 20))
            draw_grid(screen, disparos)

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

                                    try:
                                        client_socket.sendall(f"DISPARO:{coord}".encode())
                                        respuesta = client_socket.recv(1024).decode()
                                        disparos[coord] = respuesta
                                        escribir_log(archivo_log, f"Disparo en {coord}: {respuesta}")

                                        if respuesta.startswith("500"):
                                            escribir_log(archivo_log, "¡Jugador ganó la partida!")
                                            print("¡Ganaste!")
                                            pygame.time.delay(1000)
                                            juego_activo = False

                                    except socket.timeout:
                                        disparos[coord] = "404-fallido"
                                        escribir_log(archivo_log, f"Timeout al disparar en {coord}. Asumido como fallido.")
                                    except Exception as e:
                                        print(f"Error durante disparo en {coord}:", e)
                                        juego_activo = False

            pygame.display.flip()
            clock.tick(30)

if __name__ == "__main__":
    main()
