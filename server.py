#LOGICA DEL SERVIDOR PARA EL JUEGO

import pygame
import sys
import socket
from fsm_server import FSMServer

HOST = 'localhost'
PORT = 65432
TILE_SIZE = 80
GRID_SIZE = 5
SCREEN_SIZE = TILE_SIZE * GRID_SIZE

def coord_a_str(fila, col):
    return f"{chr(65 + fila)}{col + 1}"

def seleccionar_barcos():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + 60))
    pygame.display.set_caption("Selecciona 5 posiciones para los barcos")
    clock = pygame.time.Clock()

    barcos = set()
    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 28)

    def draw_grid():
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = coord_a_str(fila, col)
                rect = pygame.Rect(col * TILE_SIZE, fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                color = (0, 200, 0) if coord in barcos else (70, 70, 70)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)

    def draw_reset_button():
        btn_rect = pygame.Rect(10, SCREEN_SIZE + 10, 140, 40)
        pygame.draw.rect(screen, (200, 50, 50), btn_rect)
        text = small_font.render("Reiniciar", True, (255, 255, 255))
        screen.blit(text, (btn_rect.x + 30, btn_rect.y + 8))
        return btn_rect

    def draw_confirmation():
        overlay = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE + 60))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        msg = font.render("¿Confirmar selección?", True, (255, 255, 255))
        screen.blit(msg, (SCREEN_SIZE // 2 - msg.get_width() // 2, SCREEN_SIZE // 2 - 40))

        btn_yes = pygame.Rect(SCREEN_SIZE // 2 - 100, SCREEN_SIZE // 2, 80, 40)
        btn_no = pygame.Rect(SCREEN_SIZE // 2 + 20, SCREEN_SIZE // 2, 80, 40)

        pygame.draw.rect(screen, (0, 200, 0), btn_yes)
        pygame.draw.rect(screen, (200, 0, 0), btn_no)

        screen.blit(small_font.render("Sí", True, (255, 255, 255)), (btn_yes.x + 25, btn_yes.y + 8))
        screen.blit(small_font.render("No", True, (255, 255, 255)), (btn_no.x + 22, btn_no.y + 8))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if btn_yes.collidepoint(event.pos):
                        return True
                    if btn_no.collidepoint(event.pos):
                        return False

            clock.tick(30)

    running = True
    while running:
        screen.fill((30, 30, 30))
        draw_grid()
        reset_btn = draw_reset_button()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return list(barcos)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_btn.collidepoint(event.pos):
                    barcos.clear()
                elif len(barcos) < 5:
                    x, y = pygame.mouse.get_pos()
                    if y < SCREEN_SIZE:
                        fila = y // TILE_SIZE
                        col = x // TILE_SIZE
                        coord = coord_a_str(fila, col)
                        if coord not in barcos:
                            barcos.add(coord)
                            draw_grid()
                            draw_reset_button()
                            pygame.display.flip()

        if len(barcos) == 5:
            if draw_confirmation():
                pygame.quit()
                return list(barcos)
            else:
                barcos.clear()

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    return list(barcos)


def main():
    barcos = seleccionar_barcos()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Servidor FSM escuchando en {HOST}:{PORT}...")

        while True:
            conn, addr = server_socket.accept()
            print(f"\nNueva conexión desde {addr}")
            fsm = FSMServer(barcos)
            with conn:
                while True:
                    try:
                        data = conn.recv(1024)
                        if not data:
                            print("Cliente desconectado.")
                            break

                        mensaje = data.decode().strip()

                        if mensaje == "CLOSE_SERVER":
                            print("Cliente solicitó cerrar el servidor.")
                            conn.sendall("Servidor cerrado".encode())
                            conn.close()
                            server_socket.close()
                            pygame.quit()
                            return  # Salir de main()

                        respuesta = fsm.process_message(mensaje)
                        conn.sendall(respuesta.encode())
                    except Exception as e:
                        print(f"Error durante la conexión: {e}")
                        break

if __name__ == "__main__":
    main()
