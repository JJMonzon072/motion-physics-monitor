# Plantilla de Informe Técnico
## Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real

---

# PORTADA

**Universidad Mariano Gálvez de Guatemala**
Facultad de Ingeniería en Sistemas
Escuela de Ingeniería en Sistemas — Plan fin de semana

**Curso:** Física 1
**Proyecto Final**

**Título del Proyecto:**
Sistema de Monitoreo de Movimiento y Análisis Físico en Tiempo Real

**Integrante(s):**
- Nombre: _____________________________ Carné: ____________

**Catedrático:** ______________________________

**Fecha de entrega:** ____________________

---

## 1. INTRODUCCIÓN

_Describir brevemente en qué consiste el proyecto, qué problema resuelve y por qué es relevante aplicar principios de cinemática mediante software._

---

## 2. PLANTEAMIENTO DEL PROBLEMA

_Exponer la necesidad o problemática que motiva el desarrollo del sistema. Ejemplo: la dificultad de medir con precisión variables cinemáticas en un laboratorio sin equipo especializado._

---

## 3. OBJETIVO GENERAL

Desarrollar un sistema computacional que permita el monitoreo en tiempo real de un movimiento físico, aplicando modelos de cinemática para el análisis y visualización de variables dinámicas.

---

## 4. OBJETIVOS ESPECÍFICOS

- Capturar datos de movimiento mediante video o simulación.
- Implementar algoritmos para calcular posición, velocidad y aceleración.
- Clasificar el tipo de movimiento (MRU, MRUV, Caída Libre).
- Generar gráficas interactivas de posición, velocidad y aceleración vs tiempo.
- Validar los resultados experimentales contra valores teóricos.
- Desarrollar una interfaz amigable para la visualización de resultados.

---

## 5. JUSTIFICACIÓN

_¿Por qué es útil este sistema? ¿Qué ventajas tiene respecto a métodos manuales? ¿Cómo contribuye al aprendizaje de la física?_

---

## 6. MARCO TEÓRICO

### 6.1 Cinemática

La cinemática es la rama de la mecánica que estudia el movimiento de los cuerpos sin considerar las fuerzas que lo producen. Las variables fundamentales son:

- **Posición** x(t): ubicación del objeto en el espacio en función del tiempo.
- **Velocidad** v(t): tasa de cambio de la posición.
- **Aceleración** a(t): tasa de cambio de la velocidad.

### 6.2 Tipos de Movimiento

#### Movimiento Rectilíneo Uniforme (MRU)
El objeto se desplaza en línea recta con velocidad constante.

- x = x₀ + v · t
- v = constante
- a = 0

#### Movimiento Rectilíneo Uniformemente Variado (MRUV)
El objeto se desplaza con aceleración constante.

- x = x₀ + v₀·t + ½·a·t²
- v = v₀ + a·t
- a = constante

#### Caída Libre
Caso especial de MRUV con a = −g = −9.8 m/s².

- y = y₀ + v₀·t − ½·g·t²
- v = v₀ − g·t
- g ≈ 9.8 m/s²

### 6.3 Derivadas Numéricas

En el sistema se utilizan diferencias finitas para calcular velocidad y aceleración:

- v ≈ Δx / Δt
- a ≈ Δv / Δt

Donde Δt = 1 / FPS (o 1 / (FPS / skip) si se procesan frames salteados).

### 6.4 Visión por Computadora

_Describir brevemente qué es OpenCV, qué es la segmentación por color HSV y cómo se obtiene el centroide del objeto._

---

## 7. METODOLOGÍA

1. **Captura de datos**: video del objeto en movimiento o datos simulados.
2. **Preprocesamiento**: lectura de frames, conversión de color BGR → HSV.
3. **Detección**: creación de máscara de color y extracción del centroide.
4. **Cálculo físico**: conversión de píxeles a metros (si hay calibración), cálculo de velocidad y aceleración por diferencias finitas, suavizado con media móvil.
5. **Clasificación**: regresión lineal/cuadrática sobre las series temporales.
6. **Validación**: comparación contra valor teórico, cálculo de error porcentual.
7. **Visualización**: gráficas interactivas con Plotly en un dashboard Streamlit.

---

## 8. DESARROLLO DEL SISTEMA

### 8.1 Arquitectura

_Incluir diagrama de módulos o describir la estructura de carpetas._

### 8.2 Módulos Principales

| Módulo | Función |
|---|---|
| `physics_calculations.py` | Velocidad, aceleración, distancia |
| `motion_classification.py` | Clasificación MRU/MRUV/Caída Libre |
| `tracking.py` | Detección del objeto con OpenCV |
| `simulation.py` | Generación de datos sintéticos |
| `validation.py` | Comparación con valores teóricos |
| `plotting.py` | Gráficas Plotly |
| `app.py` | Dashboard Streamlit |

### 8.3 Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.11 | Lenguaje principal |
| Streamlit | ≥1.35 | Interfaz web |
| OpenCV | ≥4.9 | Procesamiento de video |
| NumPy | ≥1.26 | Cálculo numérico |
| Pandas | ≥2.2 | Manejo de datos |
| Plotly | ≥5.22 | Gráficas interactivas |
| SciPy | ≥1.13 | Funciones científicas auxiliares |

---

## 9. RESULTADOS OBTENIDOS

### 9.1 Caso de Prueba: [Describir el video usado]

_Incluir captura de pantalla de la interfaz con el video procesado._

### 9.2 Datos Calculados

| Variable | Valor Experimental | Unidad |
|---|---|---|
| Distancia total | | m |
| Velocidad promedio | | m/s |
| Velocidad máxima | | m/s |
| Aceleración promedio | | m/s² |
| Tipo de movimiento | | — |

### 9.3 Gráficas

_Insertar capturas de las gráficas generadas por la aplicación._

- Posición vs Tiempo
- Velocidad vs Tiempo
- Aceleración vs Tiempo
- Trayectoria 2D (si aplica)

---

## 10. VALIDACIÓN

### 10.1 Comparación Experimental vs Teórico

| Variable | Valor Teórico | Valor Experimental | Error Absoluto | Error % |
|---|---|---|---|---|
| _Velocidad / Aceleración / g_ | | | | |

### 10.2 Interpretación del Margen de Error

_Explicar por qué existe el error: ruido en la detección, resolución del video, calidad del rastreo, suavizado aplicado, etc._

---

## 11. LIMITACIONES

- La precisión depende de la calidad del video y condiciones de iluminación.
- Sin calibración, los resultados se expresan en píxeles.
- La aceleración numérica puede presentar ruido.
- El sistema asume movimiento en 2D plano perpendicular a la cámara.
- No reemplaza instrumentos de laboratorio calibrados.

---

## 12. CONCLUSIONES

_Al menos 3 conclusiones específicas sobre:_
- _Los resultados físicos obtenidos._
- _La precisión del sistema._
- _El cumplimiento de los objetivos._

---

## 13. RECOMENDACIONES

_Al menos 2 recomendaciones para mejorar el sistema o la metodología de grabación._

---

## 14. BIBLIOGRAFÍA

- Serway, R. A., & Jewett, J. W. (2019). *Physics for Scientists and Engineers* (10th ed.). Cengage Learning.
- OpenCV Documentation. (2024). https://docs.opencv.org
- Streamlit Documentation. (2024). https://docs.streamlit.io
- _[Agregar otras referencias usadas]_

---

## 15. ANEXOS

### Anexo A: Capturas de Pantalla de la Aplicación

_[Insertar capturas]_

### Anexo B: Fragmentos de Código Relevantes

_[Mostrar funciones clave con su explicación]_

### Anexo C: Video Demostrativo

_[Indicar enlace o adjuntar archivo]_
