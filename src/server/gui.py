import pygame
import sys
from typing import Tuple, List, Set, Callable
from common.constants import *

class ServerGUI:
    """
    Clase que maneja la interfaz gráfica del servidor.
    """
    def __init__(self):
        """
        Inicializa la interfaz gráfica del servidor.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH_GAME, SCREEN_HEIGHT_GAME))
        pygame.display.set_caption("Servidor FSM - Esperando conexión")
        self.clock = pygame.time.Clock()
        
        # Inicializar fuentes
        self.font = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_HEADER_GRID_SIZE)
        self.font_header = pygame.font.SysFont(FONT_DEFAULT_NAME, FONT_HEADER_GRID_SIZE)

    def draw_grid_server(self, impactos_recibidos: dict, ocupadas: Set[str], 
                        conectado: List, ultimo_disparo: str):
        """
        Dibuja el tablero del servidor con los barcos y los impactos recibidos.
        
        Args:
            impactos_recibidos (dict): Diccionario de coordenadas -> códigos de resultado
            ocupadas (Set[str]): Conjunto de coordenadas ocupadas por barcos
            conectado (List): Lista con estado de conexión
            ultimo_disparo (str): Texto del último disparo recibido
        """
        self.screen.fill(COLOR_BLUE_WATER)

        # --- DIBUJAR NÚMEROS (ENCABEZADOS DE COLUMNA) ---
        for col in range(GRID_SIZE):
            text_surface = self.font_header.render(str(col + 1), True, COLOR_WHITE)
            self.screen.blit(text_surface, (HEADER_OFFSET + col * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_width() // 2,
                                          HEADER_OFFSET // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR LETRAS (ENCABEZADOS DE FILA) ---
        for fila in range(GRID_SIZE):
            text_surface = self.font_header.render(chr(65 + fila), True, COLOR_WHITE)
            self.screen.blit(text_surface, (HEADER_OFFSET // 2 - text_surface.get_width() // 2,
                                          HEADER_OFFSET + fila * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR EL TABLERO PROPIAMENTE DICHO ---
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = f"{chr(65 + fila)}{col + 1}"
                rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, 
                                 HEADER_OFFSET + fila * TILE_SIZE, 
                                 TILE_SIZE, TILE_SIZE)

                if coord in impactos_recibidos:
                    resultado = impactos_recibidos[coord]
                    if resultado.startswith("500") or resultado.startswith("200"):
                        color = COLOR_GRID_SUNK  # Barco hundido
                    elif resultado.startswith("202"):
                        color = COLOR_GRID_HIT   # Impacto
                    else:
                        color = COLOR_GRID_MISS  # Agua
                elif coord in ocupadas:
                    color = COLOR_SHIP_PLACED  # Barco sin tocar
                else:
                    color = COLOR_GRID_EMPTY  # Celda vacía

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)

        # --- MENSAJES DE ESTADO (ABAJO DEL TABLERO) ---
        if conectado[0]:
            conn, addr = conectado[0]
            texto = self.font.render(f"Cliente conectado: {addr[0]}:{addr[1]}", True, COLOR_WHITE)
        else:
            texto = self.font.render(f"Esperando conexión en {HOST}:{PORT}...", True, COLOR_WHITE)
        self.screen.blit(texto, (10, SCREEN_HEIGHT_GAME - 50))

        if ultimo_disparo:
            texto_disparo = self.font.render(ultimo_disparo, True, COLOR_YELLOW)
            self.screen.blit(texto_disparo, (10, SCREEN_HEIGHT_GAME - 25))

    def draw_grid_placement(self, todos_ocupados: Set[str], preview_coords: List[str], 
                          index_barco: int, barcos_def: List[Tuple[str, int]], 
                          orientacion: str):
        """
        Dibuja el tablero durante la fase de colocación de barcos.
        
        Args:
            todos_ocupados (Set[str]): Conjunto de coordenadas ocupadas
            preview_coords (List[str]): Lista de coordenadas para previsualización
            index_barco (int): Índice del barco actual
            barcos_def (List[Tuple[str, int]]): Lista de definiciones de barcos
            orientacion (str): Orientación actual del barco ('H' o 'V')
        """
        self.screen.fill(COLOR_BLUE_WATER)

        # --- DIBUJAR NÚMEROS Y LETRAS ---
        for col in range(GRID_SIZE):
            text_surface = self.font_header.render(str(col + 1), True, COLOR_WHITE)
            self.screen.blit(text_surface, (HEADER_OFFSET + col * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_width() // 2,
                                          HEADER_OFFSET // 2 - text_surface.get_height() // 2))

        for fila in range(GRID_SIZE):
            text_surface = self.font_header.render(chr(65 + fila), True, COLOR_WHITE)
            self.screen.blit(text_surface, (HEADER_OFFSET // 2 - text_surface.get_width() // 2,
                                          HEADER_OFFSET + fila * TILE_SIZE + TILE_SIZE // 2 - text_surface.get_height() // 2))

        # --- DIBUJAR EL TABLERO ---
        for fila in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                coord = f"{chr(65 + fila)}{col + 1}"
                rect = pygame.Rect(HEADER_OFFSET + col * TILE_SIZE, 
                                 HEADER_OFFSET + fila * TILE_SIZE, 
                                 TILE_SIZE, TILE_SIZE)

                if coord in todos_ocupados:
                    color = COLOR_SHIP_PLACED  # Barco colocado
                elif preview_coords and coord in preview_coords:
                    color = COLOR_GRID_PENDING  # Previsualización
                else:
                    color = COLOR_GRID_EMPTY  # Celda vacía

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)

        # Mensaje con nombre del barco y orientación
        if index_barco < len(barcos_def):
            nombre, tamaño = barcos_def[index_barco]
            texto = self.font.render(f"{nombre} ({tamaño}): orientacion {orientacion}", True, COLOR_WHITE)
            self.screen.blit(texto, (10, SCREEN_HEIGHT_GAME - 50))

    def update_display(self):
        """
        Actualiza la pantalla y controla el FPS.
        """
        pygame.display.flip()
        self.clock.tick(30)
