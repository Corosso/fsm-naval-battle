import pygame
import sys
from typing import Tuple
from common.constants import *
from .client import Client

class GUI:
    """
    Clase que maneja la interfaz gráfica del cliente.
    """
    def __init__(self):
        """
        Inicializa la interfaz gráfica y sus componentes.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
        pygame.display.set_caption("Cliente FSM Naval Battle")
        self.clock = pygame.time.Clock()
        
        # Inicializar fuentes
        self.font_title = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_TITLE_SIZE)
        self.font_menu = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_MENU_BUTTON_SIZE)
        self.font_header = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_HEADER_GRID_SIZE)
        self.font_input = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_INPUT_SIZE)
        self.font_result = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_RESULT_MESSAGE_SIZE)

    def pedir_direccion_servidor(self):
        """
        Muestra una ventana de diálogo para que el usuario ingrese la IP y puerto del servidor.
        
        Returns:
            tuple: (ip, port) donde:
                - ip (str): Dirección IP del servidor
                - port (int): Puerto del servidor
        """
        # Guardar la ventana principal actual
        old_screen = self.screen
        
        # Crear una nueva ventana para la conexión
        connection_screen = pygame.display.set_mode((400, 250)) 
        pygame.display.set_caption("Conectar al servidor FSM")
        
        input_box_ip = pygame.Rect(100, 60, 250, 42)
        input_box_port = pygame.Rect(100, 135, 250, 42)
        
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        
        active_ip = False 
        active_port = False

        # Valores predeterminados y banderas para saber si son los valores iniciales
        ip_text = 'localhost' 
        port_text = '65432'
        is_ip_default = True
        is_port_default = True
        
        done = False

        # Ajustado el tamaño y posición del botón "Conectar" para el texto
        connect_btn_rect = pygame.Rect(125, 190, 150, 40) # Ancho aumentado
        connect_btn_color = COLOR_BUTTON_TEST 
        connect_btn_shadow_color = COLOR_BUTTON_TEST_SHADOW 

        # Pequeño padding dentro de los cuadros de texto
        text_padding = 5 

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if input_box_ip.collidepoint(event.pos):
                        active_ip = True
                        active_port = False
                        if is_ip_default: # Si es el valor predeterminado, se borra al hacer clic
                            ip_text = ''
                            is_ip_default = False
                    elif input_box_port.collidepoint(event.pos):
                        active_port = True
                        active_ip = False
                        if is_port_default: # Si es el valor predeterminado, se borra al hacer clic
                            port_text = ''
                            is_port_default = False
                    else: # Si se hace clic fuera de los cuadros de entrada
                        active_ip = False
                        active_port = False
                        # Si el campo queda vacío y no se modificó, se puede volver a poner el valor por defecto
                        if not ip_text and not is_ip_default:
                            ip_text = 'localhost'
                            is_ip_default = True
                        if not port_text and not is_port_default:
                            port_text = '65432'
                            is_port_default = True


                    if connect_btn_rect.collidepoint(event.pos):
                        try:
                            ip_final = ip_text.strip() if ip_text.strip() else 'localhost'
                            port_final = int(port_text.strip()) if port_text.strip() else 65432
                            # Restaurar la ventana principal antes de retornar
                            self.screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
                            pygame.display.set_caption("Cliente FSM Naval Battle")
                            return ip_final, port_final
                        except ValueError:
                            print("Error: El puerto debe ser un número válido.")
                            pass

                if event.type == pygame.KEYDOWN:
                    if active_ip:
                        if event.key == pygame.K_BACKSPACE:
                            ip_text = ip_text[:-1]
                        elif event.key == pygame.K_RETURN: # Permite confirmar con Enter
                            active_ip = False
                            active_port = True # Pasa al siguiente campo
                            if is_port_default:
                                port_text = ''
                                is_port_default = False
                        else:
                            ip_text += event.unicode
                    elif active_port:
                        if event.key == pygame.K_BACKSPACE:
                            port_text = port_text[:-1]
                        elif event.key == pygame.K_RETURN: 
                            # Validación y retorno al presionar Enter en el campo de puerto
                            try:
                                ip_final = ip_text.strip() if ip_text.strip() else 'localhost'
                                port_final = int(port_text.strip()) if port_text.strip() else 65432
                                # Restaurar la ventana principal antes de retornar
                                self.screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
                                pygame.display.set_caption("Cliente FSM Naval Battle")
                                return ip_final, port_final
                            except ValueError:
                                print("Error: El puerto debe ser un número válido.")
                                pass
                        elif event.unicode.isdigit(): # Solo permite dígitos para el puerto
                            port_text += event.unicode
            
            connection_screen.fill((30, 30, 30)) # Fondo de la ventana de conexión
            
            # --- Dibujar campo de IP ---
            connection_screen.blit(FONT_INPUT.render("IP del servidor:", True, COLOR_WHITE), (100, 20))
            # Dibuja el rectángulo del input box
            pygame.draw.rect(connection_screen, color_active if active_ip else color_inactive, input_box_ip, 2)
            
            # Renderiza el texto
            text_surface_ip = FONT_INPUT.render(ip_text, True, COLOR_WHITE)
            
            # Define el área donde se bliteará el texto dentro del input box
            text_display_rect_ip = pygame.Rect(input_box_ip.x + text_padding, 
                                              input_box_ip.y + text_padding, 
                                              input_box_ip.width - 2 * text_padding, 
                                              input_box_ip.height - 2 * text_padding)

            # Si el texto es más largo que el área de display, ajusta la posición de inicio para "scrollear"
            if text_surface_ip.get_width() > text_display_rect_ip.width:
                # Calcular el desplazamiento X para mostrar la parte final del texto
                text_x = text_display_rect_ip.x - (text_surface_ip.get_width() - text_display_rect_ip.width)
                # Blitear el texto, usando el rectángulo de display como área de recorte
                # Esto asegura que el texto no se salga del rectángulo visual
                connection_screen.blit(text_surface_ip, (text_x, text_display_rect_ip.y), text_display_rect_ip.copy())
            else:
                # Si el texto cabe, centrarlo horizontalmente dentro del área de display
                text_x = text_display_rect_ip.x + (text_display_rect_ip.width - text_surface_ip.get_width()) // 2
                connection_screen.blit(text_surface_ip, (text_x, text_display_rect_ip.y))


            # --- Dibujar campo de Puerto ---
            connection_screen.blit(FONT_INPUT.render("Puerto:", True, COLOR_WHITE), (100, 99))
            pygame.draw.rect(connection_screen, color_active if active_port else color_inactive, input_box_port, 2)

            # Renderiza el texto del puerto
            text_surface_port = FONT_INPUT.render(port_text, True, COLOR_WHITE)

            # Define el área donde se bliteará el texto dentro del input box
            text_display_rect_port = pygame.Rect(input_box_port.x + text_padding, 
                                                input_box_port.y + text_padding, 
                                                input_box_port.width - 2 * text_padding, 
                                                input_box_port.height - 2 * text_padding)

            if text_surface_port.get_width() > text_display_rect_port.width:
                text_x = text_display_rect_port.x - (text_surface_port.get_width() - text_display_rect_port.width)
                connection_screen.blit(text_surface_port, (text_x, text_display_rect_port.y), text_display_rect_port.copy())
            else:
                text_x = text_display_rect_port.x + (text_display_rect_port.width - text_surface_port.get_width()) // 2
                connection_screen.blit(text_surface_port, (text_x, text_display_rect_port.y))


            # Dibuja el botón de Conectar con la nueva función
            draw_button(connection_screen, connect_btn_rect, connect_btn_color, connect_btn_shadow_color, 
                        "Conectar", FONT_INPUT, COLOR_WHITE)

            pygame.display.flip()

    def main_menu(self, client_socket):
        """
        Muestra y maneja el menú principal del juego.
        
        Args:
            client_socket (socket.socket): Socket de conexión con el servidor
        """
        while True:
            self.screen.fill(COLOR_BACKGROUND_DARK) # Fondo del menú principal
            title = self.font_title.render("Batalla naval (FSM)", True, COLOR_WHITE)
            self.screen.blit(title, (SCREEN_WIDTH_GAME // 2 - title.get_width() // 2, 40))

            # Ajustar las posiciones de los botones usando SCREEN_WIDTH_GAME
            play_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 120, 200, 50)
            test_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 190, 200, 100) # Más alto para texto multilinea
            quit_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 310, 200, 50)

            # Dibuja los botones del menú con relieve
            self.draw_button(self.screen, play_btn_rect, COLOR_BUTTON_PLAY, COLOR_BUTTON_PLAY_SHADOW, 
                        "JUGAR", self.font_menu, COLOR_WHITE)
            
            # Para el botón de "PROBAR CONEXIÓN", usamos la función para texto multilinea
            # Primero dibujamos el botón base (sombra y color principal)
            pygame.draw.rect(self.screen, COLOR_BUTTON_TEST_SHADOW, 
                             (test_btn_rect.x + 3, test_btn_rect.y + 3, test_btn_rect.width, test_btn_rect.height))
            pygame.draw.rect(self.screen, COLOR_BUTTON_TEST, test_btn_rect)
            # Luego el texto multilinea centrado
            self.draw_multiline_text_centered("PROBAR\nCONEXIÓN", self.font_menu, COLOR_WHITE, 
                                             self.screen, test_btn_rect)

            self.draw_button(self.screen, quit_btn_rect, COLOR_BUTTON_QUIT, COLOR_BUTTON_QUIT_SHADOW, 
                        "SALIR", self.font_menu, COLOR_WHITE)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    try:
                        client_socket.sendall("CLOSE_SERVER".encode())
                    except:
                        pass
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_btn_rect.collidepoint(event.pos):
                        return True # Salir del menú y empezar el juego
                    if test_btn_rect.collidepoint(event.pos):
                        try:
                            client_socket.settimeout(2)
                            client_socket.sendall("A0".encode()) # Mensaje de prueba de conexión
                            respuesta = client_socket.recv(1024).decode()
                            print("Respuesta de prueba:", respuesta)
                        except socket.timeout:
                            print("Timeout: El servidor no respondió a la prueba de conexión.")
                        except Exception as e:
                            print("Error durante la prueba de conexión:", e)
                        finally:
                            client_socket.settimeout(2)  # Aseguramos que el timeout siga en 2s

                    if quit_btn_rect.collidepoint(event.pos):
                        try:
                            client_socket.sendall("CLOSE_SERVER".encode())
                        except:
                            pass
                        pygame.quit()
                        sys.exit()

            pygame.display.flip()
            self.clock.tick(30)

    def draw_grid(screen, juego: JuegoCliente):
        """
        Dibuja el tablero de juego del cliente, incluyendo encabezados y celdas.
        
        Args:
            screen (pygame.Surface): Superficie donde se dibujará el tablero
            juego (JuegoCliente): Instancia del juego que contiene el estado actual
        """
        # --- Fondo de la pantalla ---
        if WATER_BACKGROUND:
            screen.blit(WATER_BACKGROUND, (0, 0))
        else:
            screen.fill(COLOR_BLUE_WATER) 

        # --- DIBUJAR NÚMEROS (ENCABEZADOS DE COLUMNA) ---
        for col in range(GRID_SIZE):
            text_surface = FONT_HEADER_GRID.render(str(col + 1), True, COLOR_WHITE)
            screen.blit(text_surface, (HEADER_OFFSET + col * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_width() // 2,
                                    HEADER_OFFSET // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR LETRAS (ENCABEZADOS DE FILA) ---
        for fila in range(GRID_SIZE):
            text_surface = FONT_HEADER_GRID.render(chr(65 + fila), True, COLOR_WHITE)
            screen.blit(text_surface, (HEADER_OFFSET // 2 - text_surface.get_width() // 2,
                                    HEADER_OFFSET + fila * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR EL TABLERO PROPIAMENTE DICHO ---
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = juego.coord_a_str(fila, col)
                rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, HEADER_OFFSET + fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                
                color = juego.obtener_color_celda(coord)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, COLOR_WHITE, rect, 2) # Borde blanco de la celda

        # --- MENSAJE DE RESULTADO FINAL DE PARTIDA (si aplica) ---
        if juego.juego_activo:
            text_res = FONT_RESULT_MESSAGE.render("Juego en curso...", True, COLOR_YELLOW)
            screen.blit(text_res, (20, SCREEN_HEIGHT_GAME - 40))
        else:
            text_res = FONT_RESULT_MESSAGE.render("¡Jugador ganó la partida!", True, COLOR_YELLOW)
            screen.blit(text_res, (20, SCREEN_HEIGHT_GAME - 40))


def main():
    """
    Función principal que ejecuta el cliente del juego.
    """
    gui = GUI()
    host, port = gui.pedir_direccion_servidor()
    
    client = Cliente(host, port)
    if not client.conectar():
        print(f"No se pudo conectar al servidor en {host}:{port}")
        pygame.quit()
        sys.exit()

    # Asegurarnos de que la ventana principal esté activa
    gui.screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
    pygame.display.set_caption("Cliente FSM Naval Battle")

    while True:
        if not gui.main_menu(client):
            break

        # Obtener posiciones de barcos
        barcos = client.obtener_barcos()
        if not barcos:
            continue

        # Bucle principal del juego
        while client.juego.juego_activo:
            gui.draw_grid(client.juego)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    client.cerrar_conexion()
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if (mouse_x > HEADER_OFFSET and mouse_y > HEADER_OFFSET and 
                        mouse_x < SCREEN_WIDTH_GAME and mouse_y < (SCREEN_HEIGHT_GAME - 50)):
                        
                        fila = (mouse_y - HEADER_OFFSET) // TILE_SIZE
                        col = (mouse_x - HEADER_OFFSET) // TILE_SIZE
                        
                        if 0 <= fila < GRID_SIZE and 0 <= col < GRID_SIZE:
                            coord = client.juego.coord_a_str(fila, col)
                            if client.juego.puede_disparar(coord):
                                client.enviar_disparo(coord)

            pygame.display.flip()
            gui.clock.tick(30)

if __name__ == "__main__":
    main()
