# FSM Naval Battle

Este es un juego simple de Batalla Naval basado en una Máquina de Estados Finitos (FSM), desarrollado en Python usando `sockets` para la comunicación cliente-servidor y `pygame` para la interfaz gráfica.

## Requisitos

- Python 3.8 o superior
- Pygame

### FSM - Estados del servidor

- `q1`: Todos los barcos intactos.
- `q2`: Al menos un impacto.
- `q3`: Al menos un barco hundido.
- `q4`: Todos los barcos hundidos (fin del juego).

## 📁 Estructura de Archivos

├── client_gui.py # Cliente con GUI en Pygame

├── server.py # Servidor que recibe disparos

├── fsm_server.py # Lógica FSM y clase Barco

├── logs/ # Carpeta con logs de partidas

└── README.md

## Instalación

1. Instalar Pygame.

```bash
pip install pygame
```
## Ejecucion

- Debes abrir 2 terminales
- Primeramente, en una terminal debes ejecutar el siguiente comando para eecutar el servidor
```bash
python server.py
```
- Con click elige la posición de los barcos, con R la orientación (horizontal o vertical) y el botón reiniciar es para volver a escoger la posición de los barcos 

  
- En la segunda terminal ejecutar el siguiente comando
```bash
python client_gui.py
```
- Empezar juego: Empieza el juego
- Probar conexión: Prueba la conexion al servidor (Mensaje 200 OK, significa que la conexión se hizo de manera correcta)
- Salir: Se sale del juego
