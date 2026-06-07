# Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real

**Proyecto Final — Física 1**
Universidad Mariano Gálvez · Facultad de Ingeniería en Sistemas · Plan fin de semana

**Autor:** Juan José Monzón

---

## Descripción

Sistema computacional que captura, analiza y visualiza el movimiento de objetos físicos
a partir de video digital o datos simulados. El sistema aplica ecuaciones de cinemática
para calcular posición, velocidad y aceleración frame a frame, clasifica automáticamente
el tipo de movimiento (MRU, MRUV o Caída Libre) y valida los resultados experimentales
contra valores teóricos conocidos.

El dashboard corre completamente en el navegador — no requiere hardware especializado,
solo una cámara de video convencional y una computadora estándar.

---

## Funcionalidades

- **Análisis de video:** Carga archivos MP4, AVI o MOV y rastrea un objeto de color usando segmentación HSV con OpenCV.
- **Modo simulación:** Genera trayectorias sintéticas perfectas de MRU, MRUV y Caída Libre con parámetros configurables.
- **Cálculo cinemático:** Posición, velocidad instantánea, aceleración y distancia acumulada mediante diferencias finitas con suavizado.
- **Clasificación automática:** Determina el tipo de movimiento sin intervención del usuario mediante regresión lineal y cuadrática (R²).
- **Validación:** Compara resultados experimentales con teóricos y calcula el error absoluto y porcentual.
- **Gráficas interactivas:** Posición vs t, Velocidad vs t, Aceleración vs t y Trayectoria 2D con Plotly.
- **Exportación:** Descarga los datos calculados en formato CSV.
- **Calibración:** Convierte píxeles a metros usando un objeto de referencia con dimensiones conocidas.

---

## Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11+ | Lenguaje principal |
| Streamlit | ≥ 1.35 | Dashboard web interactivo |
| OpenCV | ≥ 4.9 | Procesamiento de video y detección por color HSV |
| NumPy | ≥ 1.26 | Cálculo numérico y diferencias finitas |
| Pandas | ≥ 2.2 | Manejo de datos y suavizado con media móvil |
| Plotly | ≥ 5.22 | Gráficas interactivas |
| SciPy | ≥ 1.13 | Funciones científicas auxiliares |
| pytest | ≥ 8.0 | 29 pruebas unitarias automatizadas |
| Ruff | ≥ 0.4 | Linting |
| Black | ≥ 24 | Formato de código |
| Pyright | ≥ 1.1 | Verificación estática de tipos |

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/JJ-Monzon/motion-physics-monitor.git
cd motion-physics-monitor

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Ejecutar la Aplicación

```bash
source .venv/bin/activate
streamlit run app.py
```

La aplicación se abre automáticamente en `http://localhost:8501`.

---

## Estructura del Proyecto

```
motion-physics-monitor/
│
├── app.py                        # Punto de entrada — dashboard Streamlit
├── requirements.txt              # Dependencias Python
├── pyproject.toml                # Configuración de pytest, ruff y black
├── pyrightconfig.json            # Configuración de Pyright (modo basic)
├── CLAUDE.md                     # Guía interna de desarrollo
├── README.md
│
├── src/                          # Lógica del sistema
│   ├── physics_calculations.py   # Posición, velocidad, aceleración, distancia
│   ├── motion_classification.py  # Clasificación MRU / MRUV / Caída Libre
│   ├── simulation.py             # Generador de datos sintéticos
│   ├── tracking.py               # Detección de objetos por color HSV (OpenCV)
│   ├── video_processing.py       # Lectura de video, metadata, iteración de frames
│   ├── validation.py             # Error absoluto y porcentual vs valores teóricos
│   ├── plotting.py               # Gráficas Plotly
│   └── utils.py                  # Calibración px→m, suavizado, utilidades
│
├── data/
│   ├── sample_videos/            # Videos de prueba (no versionados)
│   └── outputs/                  # CSV exportados por la app (no versionados)
│
└── tests/
    └── test_physics_calculations.py   # 29 pruebas unitarias
```

---

## Módulos — Descripción Detallada

### `src/physics_calculations.py`
Implementa las ecuaciones de la cinemática usando diferencias finitas sobre series de tiempo discretas:
- `build_time_array` — genera el arreglo de tiempos a partir de FPS.
- `compute_positions` — convierte coordenadas en píxeles a metros (si hay calibración).
- `compute_velocity` / `compute_velocity_2d` — velocidad instantánea vx, vy y rapidez resultante.
- `compute_acceleration` — aceleración por doble diferencia finita con suavizado.
- `compute_distance` — distancia acumulada como longitud de arco de la trayectoria.
- `compute_summary_stats` — estadísticas agregadas: promedio, máximo.
- `build_results_dataframe` — ensambla el DataFrame de exportación.

### `src/motion_classification.py`
Clasifica el movimiento mediante regresión:
1. **Caída Libre (calibrada):** compara la pendiente de vy vs t contra g = 9.8 m/s² (tolerancia ±35%).
2. **Caída Libre (sin calibrar):** ajuste parabólico sobre y_posición, R² > 0.75 y diferencia R²_cuad − R²_lin > 0.02.
3. **MRU:** coeficiente de variación de velocidad < 0.15 y posición lineal R² > 0.90.
4. **MRUV:** velocidad lineal R² > 0.75 y posición cuadrática R² > 0.75.

### `src/tracking.py`
Detecta el objeto rastreado en cada frame BGR:
- Convierte a HSV y aplica máscara de color configurable (6 presets + personalizado).
- Operaciones morfológicas (apertura/cierre) para eliminar ruido.
- Extrae el centroide del contorno más grande mediante momentos de imagen.
- Dibuja trayectoria y anotaciones sobre el frame.

### `src/simulation.py`
Genera DataFrames con columnas idénticas a los datos de video para los tres tipos de movimiento:
- `simulate_mru` — posición lineal, velocidad constante.
- `simulate_mruv` — posición cuadrática, velocidad lineal.
- `simulate_free_fall` — caída con g configurable, almacena altura en `y_m`.

### `src/validation.py`
Calcula el error de medición:
- `validate_single` — error absoluto y porcentual para cualquier variable.
- `validate_mru`, `validate_mruv`, `validate_free_fall` — atajos con unidades predefinidas.
- `results_to_dataframe` — convierte resultados a tabla para display.

### `src/plotting.py`
Genera las 5 gráficas Plotly del dashboard:
- Posición vs Tiempo, Velocidad vs Tiempo, Aceleración vs Tiempo, Rapidez vs Tiempo y Trayectoria 2D.

### `src/video_processing.py`
Capa de I/O de video sobre OpenCV:
- `get_video_info` — metadata (FPS, frames, resolución) sin decodificar todos los frames.
- `iter_frames` — generador que entrega (índice, frame BGR), con soporte de skip y límite.

### `src/utils.py`
Funciones auxiliares:
- `smooth_series` — media móvil centrada para reducir ruido antes de derivar.
- `compute_meters_per_pixel` — factor de calibración.
- `invert_y_axis` — convierte de coordenadas de imagen (Y↓) a física (Y↑).
- `dataframe_to_csv_bytes` — serializa DataFrame para descarga en Streamlit.

---

## Física Implementada

| Variable | Fórmula |
|---|---|
| Tiempo | t = frame / fps |
| Velocidad instantánea | v = Δx / Δt |
| Velocidad 2D | v = √(vx² + vy²) |
| Aceleración | a = Δv / Δt |
| Distancia acumulada | d = Σ √(Δx² + Δy²) |
| MRU | x = x₀ + v · t |
| MRUV | x = x₀ + v₀·t + ½·a·t² |
| Caída Libre | y = y₀ + v₀·t − ½·g·t² , g = 9.8 m/s² |

**Convención de coordenadas:** OpenCV usa origen en la esquina superior izquierda con Y creciente hacia abajo.
El sistema invierte el eje Y cuando hay calibración para que Y positivo apunte hacia arriba (convención física estándar).

---

## Cómo Usar la Aplicación

### Modo Video

1. Ve a **Cargar Video** y sube un archivo MP4, AVI o MOV.
2. Selecciona el **color del objeto** a rastrear (Rojo, Azul, Verde, Amarillo, Naranja o personalizado).
3. Opcionalmente activa la **calibración** ingresando la distancia real y su equivalente en píxeles.
4. Ve a **Procesar Video** y haz clic en **Analizar Video**.
5. Revisa los resultados en **Análisis Físico** y **Gráficas**.
6. Compara contra valores teóricos en **Validación**.
7. Descarga los datos en **Exportar**.

### Modo Simulación

1. Ve a **Simulación**.
2. Selecciona el tipo: **MRU**, **MRUV** o **Caída Libre**.
3. Ajusta los parámetros (v₀, aceleración, tiempo total, altura inicial).
4. Haz clic en **Generar simulación**.
5. Los datos se transfieren automáticamente a Análisis Físico y Gráficas.

---

## Calibración Píxeles → Metros

1. Coloca un objeto de tamaño conocido visible en el video (ej. regla de 30 cm).
2. En **Cargar Video**, activa la calibración.
3. Ingresa la distancia real en metros y la distancia equivalente en píxeles.
4. El sistema calcula: `m/px = distancia_real_m / distancia_px`

Sin calibración, todos los resultados se expresan en píxeles y no son comparables con el Sistema Internacional de Unidades.

---

## Pruebas y Calidad de Código

```bash
# Pruebas unitarias (29 tests)
pytest

# Linting
ruff check .

# Verificar formato
black --check .

# Aplicar formato
black .

# Verificación de tipos
pyright
```

Estado actual: **29/29 tests passing · 0 errores Pyright · ruff clean · black clean**

---

## Consejos para Grabación de Video

Para obtener mejores resultados en el rastreo:

- Usar una pelota de **color sólido y muy saturado** (rojo, azul o verde brillante).
- Grabar con **fondo claro y uniforme**, sin objetos del mismo color que la pelota.
- **Cámara fija** en trípode, perpendicular al plano de movimiento.
- Colocar una **referencia de escala** visible en el encuadre (regla, metro) para calibrar.
- Asegurar buena iluminación constante, sin sombras fuertes.
- Para caída libre, soltar desde al menos 1.5 m de altura para capturar suficientes frames.

---

## Limitaciones

- La precisión depende directamente de la calidad del video y la iluminación.
- La detección falla si el objeto tiene color similar al fondo.
- La aceleración numérica amplifica el ruido (segunda derivada de posición ruidosa).
- El análisis es en 2D; movimiento con componente de profundidad no se captura.
- Sin calibración, los resultados están en píxeles y no en unidades físicas reales.
- La cámara debe permanecer estática durante toda la grabación.

---

## Posibles Mejoras Futuras

- Detección con YOLO o MediaPipe para mayor robustez ante oclusiones y cambios de iluminación.
- Análisis en 3D usando múltiples cámaras sincronizadas.
- Soporte para sensores físicos (Arduino/MPU6050) como fuente de datos alternativa.
- Exportación automática del informe técnico en PDF.
- Versión móvil con procesamiento de cámara en tiempo real.

---

## Licencia

Proyecto académico — Universidad Mariano Gálvez de Guatemala, 2026.
Desarrollado por **Juan José Monzón** para el curso de Física 1.
