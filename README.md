# Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real

**Proyecto Final — Física 1**
Universidad Mariano Gálvez · Ingeniería en Sistemas

Dashboard interactivo para capturar, analizar y visualizar la cinemática de
objetos en movimiento a partir de video o datos simulados.

---

## Descripción General

El sistema detecta un objeto en movimiento en un video, registra su posición
frame a frame, y calcula velocidad, aceleración y distancia usando ecuaciones
de cinemática básica. Los resultados se muestran en gráficas interactivas y
se validan contra valores teóricos.

---

## Objetivos

- Capturar posiciones de un objeto mediante análisis de video.
- Calcular posición, velocidad, aceleración y distancia recorrida.
- Clasificar el movimiento como MRU, MRUV o Caída Libre.
- Validar resultados contra valores teóricos.
- Presentar los resultados en un dashboard moderno.

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.11 | Lenguaje principal |
| Streamlit | Dashboard interactivo |
| OpenCV | Detección del objeto en video |
| NumPy | Cálculos numéricos |
| Pandas | Manejo y suavizado de datos |
| Plotly | Gráficas interactivas |
| SciPy | Funciones auxiliares |
| Pytest | Pruebas unitarias |
| Ruff | Linting |
| Black | Formato de código |
| Pyright | Verificación de tipos |

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd motion-physics-monitor

# 2. Crear y activar entorno virtual (recomendado)
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecutar la Aplicación

```bash
streamlit run app.py
```

Se abrirá automáticamente en `http://localhost:8501`.

---

## Estructura del Proyecto

```
motion-physics-monitor/
├── app.py                        # Punto de entrada — dashboard Streamlit
├── requirements.txt
├── pyrightconfig.json
├── pyproject.toml
├── CLAUDE.md                     # Guía interna para desarrollo
├── README.md
├── src/
│   ├── physics_calculations.py   # Cinemática: velocidad, aceleración, distancia
│   ├── motion_classification.py  # Clasificar MRU / MRUV / Caída Libre
│   ├── validation.py             # Error absoluto y porcentual
│   ├── simulation.py             # Generación de datos sintéticos
│   ├── plotting.py               # Gráficas Plotly
│   ├── tracking.py               # Detección de objeto con OpenCV (HSV)
│   ├── video_processing.py       # Lectura y metadata de video
│   └── utils.py                  # Calibración, suavizado, auxiliares
├── data/
│   ├── sample_videos/            # Videos de prueba (no incluidos en git)
│   └── outputs/                  # CSV generados por la app
├── docs/
│   ├── technical_report_template.md
│   └── demo_video_instructions.md
└── tests/
    └── test_physics_calculations.py
```

---

## Cómo Usar la Aplicación

### Modo Video

1. Ve a **Cargar Video** y sube un archivo MP4, AVI o MOV.
2. Selecciona el **color del objeto** a rastrear.
3. (Opcional) Activa la **calibración** ingresando una distancia de referencia conocida.
4. Ve a **Procesar Video** y haz clic en **Analizar Video**.
5. Revisa los resultados en **Análisis Físico** y **Gráficas**.
6. Compara contra valores teóricos en **Validación**.
7. Descarga los datos en **Exportar**.

### Modo Simulación (sin video)

1. Ve a **Simulación**.
2. Elige el tipo de movimiento: MRU, MRUV o Caída Libre.
3. Ajusta los parámetros (velocidad inicial, aceleración, tiempo, etc.).
4. Haz clic en **Generar simulación**.
5. Los datos pasan automáticamente a Análisis Físico y Gráficas.

---

## Calibración Píxeles a Metros

Para obtener resultados en unidades físicas reales:

1. Coloca un objeto de tamaño conocido visible en el video (ej. regla de 30 cm).
2. En **Cargar Video**, activa la calibración.
3. Ingresa la distancia real (metros) y la distancia equivalente en píxeles.
4. El factor calculado es: `m/px = distancia_real_m / distancia_px`

Sin calibración, los resultados se muestran en píxeles.

---

## Física Implementada

| Variable | Fórmula |
|---|---|
| Tiempo | t = frame_idx / fps |
| Velocidad instantánea | v = delta_x / delta_t |
| Velocidad 2D | v = sqrt(vx^2 + vy^2) |
| Aceleración | a = delta_v / delta_t |
| Distancia acumulada | d = sum(sqrt(delta_x^2 + delta_y^2)) |
| MRU | x = x0 + v·t |
| MRUV | x = x0 + v0·t + (1/2)·a·t^2 |
| Caída Libre | y = y0 + v0·t - (1/2)·g·t^2 |

**Convención de coordenadas**: En video, Y crece hacia abajo.
El sistema invierte el eje Y cuando hay calibración para que Y positivo apunte hacia arriba.

---

## Clasificación del Movimiento

| Tipo | Criterio |
|---|---|
| MRU | Aceleración aprox. 0, posición lineal (R² > 0.90) |
| MRUV | Velocidad lineal (R² > 0.85), posición cuadrática (R² > 0.85) |
| Caída Libre | Aceleración vertical aprox. 9.8 m/s² (±25%) con calibración |

---

## Validación

Error porcentual: `|experimental - teorico| / |teorico| × 100`

- < 5%: Excelente
- 5-15%: Buena (aceptable para análisis por video)
- 15-30%: Moderada (revisar calibración o condiciones)
- > 30%: Alta (revisar video, iluminación, color)

---

## Pruebas y Revisiones

```bash
pytest              # Pruebas unitarias
ruff check .        # Linting
black --check .     # Verificar formato
black .             # Aplicar formato
pyright             # Verificación de tipos
```

---

## Limitaciones

- Precisión dependiente de la calidad del video.
- La aceleración numérica puede ser ruidosa (segunda derivada).
- Sin calibración, resultados en píxeles.
- Requiere objeto de color distinguible del fondo.
- Cámara debe mantenerse fija durante la grabación.
- Es una aproximación educativa, no un instrumento de laboratorio.

---

## Posibles Mejoras Futuras

- Detección con YOLO o MediaPipe (IA) para mayor robustez.
- Análisis en 3D con múltiples cámaras.
- Soporte para sensores físicos (Arduino).
- Exportación a PDF del informe técnico.
- Aplicación móvil con cámara en tiempo real.

---

## Video Demostrativo

Ver [docs/demo_video_instructions.md](docs/demo_video_instructions.md) para guía detallada.

Resumen:
- Pelota de color brillante y sólido.
- Fondo claro sin objetos del mismo color.
- Cámara fija, perpendicular al plano de movimiento.
- Referencia de escala visible (regla o metro).
- El alumno debe aparecer en el video.
- Caída libre desde ~1.5 m da excelentes resultados.

---

## Criterios de Evaluación

| Criterio | Peso | Módulos que lo cubren |
|---|---|---|
| Correcta aplicación de física | 30% | physics_calculations, simulation, validation |
| Funcionamiento del sistema | 20% | app.py, tracking, video_processing |
| Precisión de resultados | 10% | validation, calibración |
| Video demostrativo | 10% | docs/demo_video_instructions.md |
| Documentación | 30% | README.md, CLAUDE.md, docs/, docstrings |
