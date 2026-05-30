# CLAUDE.md — motion-physics-monitor

## Objetivo del Proyecto
Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real.
Proyecto Final de Física 1 — Universidad Mariano Gálvez.
Captura, analiza y visualiza cinemática (posición, velocidad, aceleración)
a partir de video o datos simulados.

## Comandos Esenciales

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
streamlit run app.py

# Pruebas
pytest

# Linting
ruff check .

# Formato
black --check .
black .          # aplicar formato

# Tipos
pyright
```

## Estructura del Repositorio

```
motion-physics-monitor/
├── app.py                     # Dashboard Streamlit (punto de entrada)
├── requirements.txt
├── pyrightconfig.json
├── pyproject.toml
├── CLAUDE.md
├── README.md
├── src/
│   ├── physics_calculations.py  # Velocidad, aceleración, distancia
│   ├── motion_classification.py # Clasificar MRU / MRUV / Caída libre
│   ├── validation.py            # Error absoluto y porcentual
│   ├── simulation.py            # Datos sintéticos
│   ├── plotting.py              # Gráficas Plotly
│   ├── tracking.py              # Detección HSV con OpenCV
│   ├── video_processing.py      # I/O de video
│   └── utils.py                 # Auxiliares: calibración, suavizado
├── data/
│   ├── sample_videos/           # Videos de prueba (no versionados)
│   └── outputs/                 # CSV generados (no versionados)
├── docs/
│   ├── technical_report_template.md
│   └── demo_video_instructions.md
└── tests/
    └── test_physics_calculations.py
```

## Convenciones de Código

- Python 3.11+, type hints en funciones públicas.
- Docstrings en módulos y funciones importantes (una línea máximo para funciones simples).
- Nombres de variables descriptivos en inglés; strings de UI en español.
- Línea máxima: 100 caracteres.
- Formato: Black. Linting: Ruff. Tipos: Pyright (modo basic).

## Plugins Instalados (scope: project)

- **pyright-lsp**: revisión de tipos Python durante desarrollo.
- **frontend-design**: mejoras visuales de la interfaz Streamlit.
- **claude-md-management**: gestión de este CLAUDE.md.
- **code-review**: revisión de código al finalizar cada fase.

> El código debe funcionar sin depender de los plugins.
> Los plugins son apoyo de desarrollo, no dependencias de ejecución.

## Convención de Coordenadas

- OpenCV: origen top-left, Y crece hacia abajo.
- Física: origen bottom-left, Y crece hacia arriba.
- Inversión aplicada en `app.py` antes de los cálculos cuando hay calibración.

## Física Implementada

| Variable | Fórmula |
|---|---|
| Tiempo | t = frame / fps |
| Velocidad | v = Δx / Δt |
| Aceleración | a = Δv / Δt |
| Distancia | d = Σ √(Δx² + Δy²) |
| MRU | x = x₀ + v·t |
| MRUV | x = x₀ + v₀·t + ½·a·t² |
| Caída libre | y = y₀ + v₀·t − ½·g·t²; g = 9.8 m/s² |

## Prioridades de Desarrollo

1. Física correcta (fórmulas, unidades, clasificación).
2. Modo simulación siempre funcional.
3. Interfaz presentable y sin errores.
4. Documentación completa.
5. Manejo de errores robusto.
