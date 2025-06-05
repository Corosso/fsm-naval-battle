# constantes.py
"""
Módulo que contiene todas las constantes utilizadas en el juego de Batalla Naval.
Este módulo centraliza la configuración del juego, incluyendo dimensiones, colores,
fuentes y rutas de archivos para mantener la consistencia en toda la aplicación.
"""

import os
import pygame

# Obtener el directorio raíz del proyecto
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- CONSTANTES DE CONEXIÓN ---
HOST = '0.0.0.0'  # Dirección IP del servidor por defecto (escucha en todas las interfaces)
PORT = 65432       # Puerto por defecto para la conexión

# --- CONSTANTES DEL JUEGO ---
GRID_SIZE = 5      # Tamaño del tablero (5x5)
TILE_SIZE = 80     # Tamaño en píxeles de cada celda del tablero

# --- CONSTANTES DE PANTALLA ---
HEADER_OFFSET = TILE_SIZE  # Espacio reservado para números y letras del tablero
SCREEN_WIDTH_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET  # Ancho total de la ventana
SCREEN_HEIGHT_GAME = (GRID_SIZE * TILE_SIZE) + HEADER_OFFSET + 60  # Alto total de la ventana

# --- COLORES ---
# Colores principales del juego
COLOR_BACKGROUND_DARK = (10, 10, 50)    # Fondo oscuro para menú
COLOR_BLUE_WATER = (0, 0, 150)          # Color del agua
COLOR_GRID_EMPTY = (70, 70, 70)         # Celda sin disparar
COLOR_GRID_HIT = (255, 200, 0)          # Impacto en barco
COLOR_GRID_SUNK = (255, 0, 0)           # Barco hundido
COLOR_GRID_MISS = (0, 0, 255)           # Disparo al agua
COLOR_GRID_PENDING = (100, 100, 255)    # Celda pendiente de disparo
COLOR_GRID_FAILED = (120, 120, 120)     # Disparo fallido
COLOR_WHITE = (255, 255, 255)           # Color blanco
COLOR_YELLOW = (255, 255, 0)            # Color amarillo
COLOR_BLACK = (0, 0, 0)                 # Color negro

# Colores para botones con efecto de relieve
COLOR_BUTTON_PLAY = (0, 120, 250)       # Color principal botón jugar
COLOR_BUTTON_PLAY_SHADOW = (0, 80, 180) # Sombra botón jugar
COLOR_BUTTON_TEST = (0, 180, 100)       # Color principal botón probar
COLOR_BUTTON_TEST_SHADOW = (0, 130, 70) # Sombra botón probar
COLOR_BUTTON_QUIT = (200, 50, 50)       # Color principal botón salir
COLOR_BUTTON_QUIT_SHADOW = (150, 30, 30)# Sombra botón salir

# --- FUENTES ---
FONT_DEFAULT_NAME = 'Arial'              # Fuente predeterminada
FONT_TITLE_SIZE = 45                     # Tamaño para títulos
FONT_MENU_BUTTON_SIZE = 38              # Tamaño para botones del menú
FONT_HEADER_GRID_SIZE = 26              # Tamaño para encabezados del tablero
FONT_GRID_CELL_SIZE = 30                # Tamaño para celdas del tablero
FONT_INPUT_SIZE = 32                    # Tamaño para campos de entrada
FONT_SMALL_BUTTON_SIZE = 28             # Tamaño para botones pequeños
FONT_RESULT_MESSAGE_SIZE = 36           # Tamaño para mensajes de resultado

# --- DIRECTORIOS ---
LOGS_DIR = os.path.join(ROOT_DIR, "logs")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# --- NOMBRES DE ARCHIVOS ---
WATER_TEXTURE_FILE = "water_texture.png" # Textura de agua para el fondo

# --- COLORES ADICIONALES PARA BARCOS ---
COLOR_SHIP_PLACED = (0, 200, 0)         # Color para barcos colocados
COLOR_SHIP_PREVIEW = (100, 100, 255)    # Color para previsualización de barcos
