import pygame
import socket
import sys
import os
from datetime import datetime

# --- CONSTANTES ---
TILE_SIZE = 80
GRID_SIZE = 5

# Espacio para los encabezados (números y letras)
HEADER_OFFSET = TILE_SIZE 

# Dimensiones de la ventana del juego
SCREEN_WIDTH_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET
# Alto del tablero + espacio para encabezados + espacio para mensajes/botones en la parte inferior
SCREEN_HEIGHT_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET + 50 

LOGS_DIR = "logs"

# --- Carga de imagen de fondo (opcional) ---
WATER_BACKGROUND = None
try:
    water_image_path = os.path.join('assets', 'water_texture.png') 
    if os.path.exists(water_image_path):
        WATER_BACKGROUND = pygame.image.load(water_image_path).convert()
        WATER_BACKGROUND = pygame.transform.scale(WATER_BACKGROUND, (SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
    else:
        print(f"Advertencia: No se encontró la imagen de agua en '{water_image_path}'. Se usará un color de fondo sólido.")
except pygame.error as e:
    print(f"Error cargando imagen de agua: {e}. Se usará un color de fondo sólido.")
    WATER_BACKGROUND = None

# --- FUENTES (Mejora de Tipografía) ---
pygame.font.init() # Inicializa el módulo de fuentes
FONT_DEFAULT_NAME = 'Arial' # Puedes probar con 'Helvetica', 'Calibri', etc.
# Si la fuente Arial no está disponible, Pygame usará una predeterminada.

FONT_TITLE = pygame.font.SysFont(FONT_DEFAULT_NAME, 45, bold=True)
FONT_MENU_BUTTON = pygame.font.SysFont(FONT_DEFAULT_NAME, 38, bold=True)
FONT_HEADER_GRID = pygame.font.SysFont(FONT_DEFAULT_NAME, 26, bold=True)
FONT_GRID_CELL = pygame.font.SysFont(FONT_DEFAULT_NAME, 30) # Para texto futuro en celdas
FONT_INPUT = pygame.font.SysFont(FONT_DEFAULT_NAME, 32)
FONT_SMALL_BUTTON = pygame.font.SysFont(FONT_DEFAULT_NAME, 28, bold=True)
FONT_RESULT_MESSAGE = pygame.font.SysFont(FONT_DEFAULT_NAME, 36)

# --- COLORES ---
COLOR_BACKGROUND_DARK = (10, 10, 50) # Fondo oscuro para menú
COLOR_BLUE_WATER = (0, 0, 150)       # Agua sólida
COLOR_GRID_EMPTY = (70, 70, 70)      # Celda sin disparar
COLOR_GRID_HIT = (255, 200, 0)       # Impacto (Naranja/Amarillo)
COLOR_GRID_SUNK = (255, 0, 0)        # Hundido (Rojo)
COLOR_GRID_MISS = (0, 0, 255)        # Agua (Azul oscuro)
COLOR_GRID_PENDING = (100, 100, 255) # Pendiente (Azul claro)
COLOR_GRID_FAILED = (120, 120, 120)  # Disparo fallido (Gris medio)
COLOR_WHITE = (255, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_BLACK = (0,0,0)

# Colores para botones con relieve
COLOR_BUTTON_PLAY = (0, 120, 250)
COLOR_BUTTON_PLAY_SHADOW = (0, 80, 180)

COLOR_BUTTON_TEST = (0, 180, 100) # Un verde un poco más suave
COLOR_BUTTON_TEST_SHADOW = (0, 130, 70)

COLOR_BUTTON_QUIT = (200, 50, 50)
COLOR_BUTTON_QUIT_SHADOW = (150, 30, 30)

# --- Funciones Auxiliares ---

def crear_logger():
    """Crea un archivo de log para la sesión del cliente."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(LOGS_DIR, f"client_log_{timestamp}.txt")
    with open(log_file, 'w') as f:
        f.write(f"--- Client Log {timestamp} ---\n")
    return log_file

def escribir_log(archivo, mensaje):
    """Escribe un mensaje en el archivo de log."""
    with open(archivo, 'a') as f:
        f.write(f"{datetime.now().strftime('%H:%M:%S')} - {mensaje}\n")

def draw_button(surface, rect, main_color, shadow_color, text, font, text_color, shadow_offset=3):
    """
    Dibuja un botón con un efecto de relieve/sombra.
    :param surface: La superficie de Pygame donde dibujar.
    :param rect: El objeto pygame.Rect del botón.
    :param main_color: Color principal del botón.
    :param shadow_color: Color de la sombra.
    :param text: Texto a mostrar en el botón.
    :param font: Objeto de fuente de Pygame para el texto.
    :param text_color: Color del texto.
    :param shadow_offset: Desplazamiento de la sombra (píxeles).
    """
    # Dibuja la sombra
    pygame.draw.rect(surface, shadow_color, 
                     (rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height))
    # Dibuja el botón principal
    pygame.draw.rect(surface, main_color, rect)
    
    # Renderiza y blitea el texto centrado
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)

def draw_multiline_text_centered(text, font, color, surface, rect, line_spacing=5):
    """
    Dibuja texto con múltiples líneas centrado dentro de un rectángulo.
    """
    lines = text.split('\n')
    total_height = 0
    rendered_lines = []
    for line in lines:
        rendered_line = font.render(line, True, color)
        rendered_lines.append(rendered_line)
        total_height += rendered_line.get_height() + line_spacing
    total_height -= line_spacing # Remove last line_spacing

    start_y = rect.centery - total_height // 2

    for i, rendered_line in enumerate(rendered_lines):
        x = rect.centerx - rendered_line.get_width() // 2
        y = start_y + i * (rendered_line.get_height() + line_spacing)
        surface.blit(rendered_line, (x, y))

def draw_grid(screen, disparos, resultado=None):
    """
    Dibuja el tablero de juego del cliente, incluyendo encabezados y celdas de disparo.
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
            coord = f"{chr(65 + fila)}{col + 1}"
            respuesta = disparos.get(coord)

            rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, HEADER_OFFSET + fila * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if respuesta:
                if respuesta.startswith("202"):
                    color = COLOR_GRID_HIT 
                elif respuesta.startswith("200") or respuesta.startswith("500"):
                    color = COLOR_GRID_SUNK
                elif respuesta == "PENDING":
                    color = COLOR_GRID_PENDING
                elif respuesta.startswith("404"):
                    color = COLOR_GRID_MISS
                else:
                    color = COLOR_GRID_FAILED # Para "404-fallido"
            else:
                color = COLOR_GRID_EMPTY

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, COLOR_WHITE, rect, 2) # Borde blanco de la celda

    # --- MENSAJE DE RESULTADO FINAL DE PARTIDA (si aplica) ---
    if resultado:
        text_res = FONT_RESULT_MESSAGE.render(resultado, True, COLOR_YELLOW)
        screen.blit(text_res, (20, SCREEN_HEIGHT_GAME - 40))

def pedir_direccion_servidor():
    """
    Muestra una ventana de diálogo para que el usuario ingrese la IP y el puerto del servidor.
    Esta es una ventana separada del juego principal.
    """
    pygame.init() 
    screen = pygame.display.set_mode((400, 250)) 
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
                    # Validación básica antes de retornar
                    try:
                        ip_final = ip_text.strip() if ip_text.strip() else 'localhost' # Usa localhost si se deja vacío
                        port_final = int(port_text.strip()) if port_text.strip() else 65432 # Usa 65432 si se deja vacío
                        pygame.display.quit() 
                        return ip_final, port_final
                    except ValueError:
                        print("Error: El puerto debe ser un número válido.")
                        pass # Continúa el bucle para que el usuario corrija

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
                            pygame.display.quit()
                            return ip_final, port_final
                        except ValueError:
                            print("Error: El puerto debe ser un número válido.")
                            pass # Continúa el bucle
                    elif event.unicode.isdigit(): # Solo permite dígitos para el puerto
                        port_text += event.unicode
        
        screen.fill((30, 30, 30)) # Fondo de la ventana de conexión
        
        # --- Dibujar campo de IP ---
        screen.blit(FONT_INPUT.render("IP del servidor:", True, COLOR_WHITE), (100, 20))
        # Dibuja el rectángulo del input box
        pygame.draw.rect(screen, color_active if active_ip else color_inactive, input_box_ip, 2)
        
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
            screen.blit(text_surface_ip, (text_x, text_display_rect_ip.y), text_display_rect_ip.copy())
        else:
            # Si el texto cabe, centrarlo horizontalmente dentro del área de display
            text_x = text_display_rect_ip.x + (text_display_rect_ip.width - text_surface_ip.get_width()) // 2
            screen.blit(text_surface_ip, (text_x, text_display_rect_ip.y))


        # --- Dibujar campo de Puerto ---
        screen.blit(FONT_INPUT.render("Puerto:", True, COLOR_WHITE), (100, 99))
        pygame.draw.rect(screen, color_active if active_port else color_inactive, input_box_port, 2)

        # Renderiza el texto del puerto
        text_surface_port = FONT_INPUT.render(port_text, True, COLOR_WHITE)

        # Define el área donde se bliteará el texto dentro del input box
        text_display_rect_port = pygame.Rect(input_box_port.x + text_padding, 
                                            input_box_port.y + text_padding, 
                                            input_box_port.width - 2 * text_padding, 
                                            input_box_port.height - 2 * text_padding)

        if text_surface_port.get_width() > text_display_rect_port.width:
            text_x = text_display_rect_port.x - (text_surface_port.get_width() - text_display_rect_port.width)
            screen.blit(text_surface_port, (text_x, text_display_rect_port.y), text_display_rect_port.copy())
        else:
            text_x = text_display_rect_port.x + (text_display_rect_port.width - text_surface_port.get_width()) // 2
            screen.blit(text_surface_port, (text_x, text_display_rect_port.y))


        # Dibuja el botón de Conectar con la nueva función
        draw_button(screen, connect_btn_rect, connect_btn_color, connect_btn_shadow_color, 
                    "Conectar", FONT_INPUT, COLOR_WHITE)

        pygame.display.flip()

def main_menu(screen, clock, client_socket):
    """
    Muestra el menú principal del juego.
    Recibe la pantalla ya inicializada del juego principal.
    """
    while True:
        screen.fill(COLOR_BACKGROUND_DARK) # Fondo del menú principal
        title = FONT_TITLE.render("Batalla naval (FSM)", True, COLOR_WHITE)
        screen.blit(title, (SCREEN_WIDTH_GAME // 2 - title.get_width() // 2, 40))

        # Ajustar las posiciones de los botones usando SCREEN_WIDTH_GAME
        play_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 120, 200, 50)
        test_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 190, 200, 100) # Más alto para texto multilinea
        quit_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME // 2 - 100, 310, 200, 50)

        # Dibuja los botones del menú con relieve
        draw_button(screen, play_btn_rect, COLOR_BUTTON_PLAY, COLOR_BUTTON_PLAY_SHADOW, 
                    "JUGAR", FONT_MENU_BUTTON, COLOR_WHITE)
        
        # Para el botón de "PROBAR CONEXIÓN", usamos la función para texto multilinea
        # Primero dibujamos el botón base (sombra y color principal)
        pygame.draw.rect(screen, COLOR_BUTTON_TEST_SHADOW, 
                         (test_btn_rect.x + 3, test_btn_rect.y + 3, test_btn_rect.width, test_btn_rect.height))
        pygame.draw.rect(screen, COLOR_BUTTON_TEST, test_btn_rect)
        # Luego el texto multilinea centrado
        draw_multiline_text_centered("PROBAR\nCONEXIÓN", FONT_MENU_BUTTON, COLOR_WHITE, screen, test_btn_rect)

        draw_button(screen, quit_btn_rect, COLOR_BUTTON_QUIT, COLOR_BUTTON_QUIT_SHADOW, 
                    "SALIR", FONT_MENU_BUTTON, COLOR_WHITE)
        
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
                    return # Salir del menú y empezar el juego
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
        clock.tick(30)

# --- Función Principal del Cliente ---
def main():
    """
    Función principal que ejecuta el cliente del juego Batalla Naval.
    Gestiona la conexión, el menú y el bucle principal del juego.
    """
    # 1. Pedir la dirección del servidor PRIMERO.
    HOST, PORT = pedir_direccion_servidor()
    
    # 2. Después de obtener la dirección, inicializar Pygame y la ventana principal del juego
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
    pygame.display.set_caption("Cliente FSM Naval Battle")
    clock = pygame.time.Clock()

    client_socket = None 
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        client_socket.settimeout(2) # Timeout para operaciones de socket
        print(f"Conectado a {HOST}:{PORT}")
    except Exception as e:
        print(f"No se pudo conectar al servidor en {HOST}:{PORT}: {e}")
        pygame.quit()
        sys.exit() 

    # Loop principal del juego (permite volver al menú y jugar de nuevo)
    while True:
        # Muestra el menú principal; el juego comenzará al regresar de esta función
        main_menu(screen, clock, client_socket)

        archivo_log = crear_logger()
        
        # Solicitar posiciones de barcos al servidor (esto es información del oponente)
        try:
            client_socket.sendall("GET_SHIPS".encode()) 
            barcos_server = client_socket.recv(1024).decode()
            escribir_log(archivo_log, "Posiciones de barcos del servidor (oponente): " + barcos_server)
        except Exception as e:
            print(f"Error al obtener barcos del servidor: {e}")
            escribir_log(archivo_log, f"Error al obtener barcos del servidor: {e}")
            continue 

        disparos = {} # Diccionario para almacenar los resultados de los disparos del cliente
        juego_activo = True 
        
        # Posición del botón "Salir" (ajustado a la nueva altura de la pantalla)
        exit_btn_rect = pygame.Rect(SCREEN_WIDTH_GAME - 110, SCREEN_HEIGHT_GAME - 40, 100, 30)

        # Bucle principal del juego (después de que el menú ha sido cerrado)
        while juego_activo:
            # Dibuja el tablero, que incluye el fondo y las celdas
            draw_grid(screen, disparos) 

            # Dibuja el botón de salir con relieve usando la función auxiliar
            draw_button(screen, exit_btn_rect, COLOR_BUTTON_QUIT, COLOR_BUTTON_QUIT_SHADOW, 
                        "Salir", FONT_SMALL_BUTTON, COLOR_WHITE, shadow_offset=2)

            # Manejo de eventos (clics del ratón, cerrar ventana)
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
                    if exit_btn_rect.collidepoint(event.pos):
                        escribir_log(archivo_log, "Jugador salió de la partida antes de terminar.")
                        juego_activo = False 
                    else:
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        # Ajustar las coordenadas del clic para el offset de los encabezados
                        # El clic debe estar DENTRO del área del tablero (después de los encabezados y antes del botón)
                        if mouse_x > HEADER_OFFSET and mouse_y > HEADER_OFFSET and \
                           mouse_x < SCREEN_WIDTH_GAME and mouse_y < (SCREEN_HEIGHT_GAME - 50): 
                            
                            # Calcular fila y columna LÓGICAS (0-indexed) restando el offset
                            fila = (mouse_y - HEADER_OFFSET) // TILE_SIZE
                            col = (mouse_x - HEADER_OFFSET) // TILE_SIZE

                            # Asegurarse de que las coordenadas calculadas estén dentro del rango válido de la cuadrícula
                            if 0 <= fila < GRID_SIZE and 0 <= col < GRID_SIZE:
                                coord = f"{chr(65 + fila)}{col + 1}"

                                # Solo permite disparar si no se ha disparado antes en esa celda
                                if coord not in disparos: 
                                    disparos[coord] = "PENDING" 
                                    draw_grid(screen, disparos) 
                                    pygame.display.flip() 

                                    try:
                                        client_socket.sendall(f"DISPARO:{coord}".encode())
                                        respuesta = client_socket.recv(1024).decode()
                                        disparos[coord] = respuesta 
                                        escribir_log(archivo_log, f"Disparo en {coord}: {respuesta}")

                                        # Condición de victoria (si el servidor envía 500 para victoria)
                                        if respuesta.startswith("500"):
                                            escribir_log(archivo_log, "¡Jugador ganó la partida!")
                                            print("¡Ganaste!")
                                            pygame.time.delay(2000) 
                                            juego_activo = False 

                                    except socket.timeout:
                                        disparos[coord] = "404-fallido" 
                                        escribir_log(archivo_log, f"Timeout al disparar en {coord}. Asumido como fallido.")
                                    except Exception as e:
                                        print(f"Error durante disparo en {coord}:", e)
                                        escribir_log(archivo_log, f"Error durante disparo en {coord}: {e}")
                                        juego_activo = False 
            
            pygame.display.flip() 
            clock.tick(30) 


if __name__ == "__main__":
    main()