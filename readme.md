# FSM Naval Battle

Este es un juego simple de Batalla Naval basado en una Máquina de Estados Finitos (FSM), desarrollado en Python usando `sockets` para la comunicación cliente-servidor y `pygame` para la interfaz gráfica.

## Requisitos

- Python 3.8 o superior
- Pygame

## Instalación

1. Instalar Pygame.

```bash
pip install pygame
```
## Ejecucion

- Debes abrir 2 terminales
- Primeramente, en una terminal debes ejecutar el siguiente comando
```bash
python server.py
```
- Y escoger la posicion de los barcos, el boton reiniciar es para reiniciar la selección de la posición de los barcos
- En la segunda terminal ejecutar el siguiente comando
```bash
python client_gui.py
```
- Empezar juego: Empieza el juego
- Probar conexión: Prueba la conexion al servidor (Mensaje 200 OK, significa que la conexión se hizo de manera correcta)
- Salir: Se sale del juego