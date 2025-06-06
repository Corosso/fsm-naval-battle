# 🚢 Batalla Naval con FSM

Un juego de Batalla Naval implementado en Python que utiliza Máquinas de Estados Finitos (FSM) para el control del flujo del juego. El proyecto incluye una arquitectura cliente-servidor, interfaz gráfica con Pygame y un sistema de logging para seguimiento de eventos.

## 🎮 Características

- Implementación de Máquinas de Estados Finitos para el control del juego
- Arquitectura cliente-servidor con comunicación en tiempo real
- Interfaz gráfica desarrollada con Pygame
- Sistema de logging para seguimiento de eventos
- Tablero de juego 5x5
- Sistema de disparos y seguimiento de impactos
- Detección automática de barcos hundidos
- Manejo de estados y transiciones de manera eficiente

## 🛠️ Tecnologías Utilizadas

- Python
- Pygame
- Sockets para comunicación en red
- Enums para manejo de estados
- JSON para logging

## 📋 Requisitos

- Python
- Pygame
- Conexión a internet (para modo multijugador)

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/batalla-naval-fsm.git
cd batalla-naval-fsm
```

2. Instalar pygame:
```bash
pip install pygame
```

## 🎯 Uso

### Iniciar el Servidor
```bash
python src/server/server.py
```

### Iniciar el Cliente
```bash
python src/client/client.py
```

## 🏗️ Estructura del Proyecto

```
batalla-naval-fsm/
├── src/
│   ├── client/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── gui.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── fsm_server.py
│   └── common/
│       ├── __init__.py
│       ├── constants.py
│       ├── game_logic.py
│       └── logger.py
├── assets/
│   └── images/
├── logs/
├── requirements.txt
└── README.md
```

## 🎮 Cómo Jugar

1. El servidor inicia el juego y espera conexiones
2. El cliente se conecta al servidor
3. El cliente puede realizar disparos en el tablero
4. El servidor procesa los disparos y envía los resultados
5. El juego continúa hasta que todos los barcos sean hundidos

## 📊 Estados del Juego

- `FLOTA_INTACTA`: Estado inicial del juego
- `BARCO_IMPACTADO`: Un barco ha sido impactado
- `BARCO_HUNDIDO`: Un barco ha sido hundido
- `DERROTA`: Todos los barcos han sido hundidos

## 🔍 Resultados de Disparo

- `OK`: Disparo válido
- `IMPACTADO`: Disparo impactó un barco
- `HUNDIDO`: Disparo hundió un barco
- `VICTORIA`: Todos los barcos han sido hundidos
- `FALLO`: Disparo fallido
- `NO_ENCONTRADO`: Coordenada inválida

## 📝 Logging

El sistema registra todos los eventos del juego en archivos JSON en el directorio `logs/`. Esto incluye:
- Conexiones de clientes
- Disparos realizados
- Resultados de disparos
- Estados del juego
- Eventos de error

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 🙏 Agradecimientos

- Pygame por la biblioteca de juegos
- La comunidad de Python por su apoyo
- Todos los contribuidores que han ayudado al proyecto

