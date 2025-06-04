import json
from datetime import datetime
from typing import Dict, Any
import os

class Logger:
    def __init__(self, logs_dir: str = "logs"):
        """
        Inicializa el logger.
        
        Args:
            logs_dir: Directorio donde se guardarán los logs
        """
        self.logs_dir = logs_dir
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(logs_dir, f"game_log_{self.timestamp}.json")
        self.log_data = {
            "timestamp_inicio": self.timestamp,
            "eventos": [],
            "estado_final": None
        }
        
        # Guardar el archivo inicial
        self._guardar_log()

    def _guardar_log(self) -> None:
        """Guarda el log actual en el archivo JSON."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=4, ensure_ascii=False)

    def registrar_evento(self, tipo: str, datos: Dict[str, Any]) -> None:
        """
        Registra un evento en el log.
        
        Args:
            tipo: Tipo de evento (ej: "disparo", "conexion", "error")
            datos: Datos del evento
        """
        evento = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "tipo": tipo,
            "datos": datos
        }
        self.log_data["eventos"].append(evento)
        self._guardar_log()

    def registrar_estado_final(self, estado: str) -> None:
        """
        Registra el estado final del juego.
        
        Args:
            estado: Estado final del juego
        """
        self.log_data["estado_final"] = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "estado": estado
        }
        self._guardar_log()

    def obtener_ruta_log(self) -> str:
        """Retorna la ruta del archivo de log."""
        return self.log_file
