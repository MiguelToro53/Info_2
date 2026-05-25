# Seguimiento_3

# Taller 3 – Procesamiento de Archivos DICOM
**Informática 2: Unidad 3 – Introducción a la Informática Médica**
Universidad de Antioquia – Facultad de Ingeniería

**Integrantes:**
- Miguel Angel Toro
- Stefania Concha Caceres

---

## 1. Descripción del proyecto

Aplicación en Python que automatiza la lectura, extracción y almacenamiento de metadatos de archivos DICOM, y realiza procesamiento básico de imágenes médicas usando OpenCV. El sistema carga archivos `.dcm` desde una carpeta local, extrae sus metadatos clínicos, calcula la intensidad promedio de píxeles con NumPy, y genera imágenes procesadas (ecualización de histograma y detección de bordes) guardadas en formato `.png`.

El proyecto sigue el paradigma de Programación Orientada a Objetos mediante la clase `ProcesadorDICOM` definida en `procesador.py`.

---

## 2. DICOM y HL7: interoperabilidad en salud

**DICOM** (Digital Imaging and Communications in Medicine) es el estándar para el manejo de imágenes médicas. Define cómo se almacenan, transmiten y visualizan imágenes provenientes de equipos como tomógrafos, resonadores o rayos X. Cada archivo DICOM contiene tanto la imagen como los metadatos del paciente y del estudio en un único archivo.

**HL7** (Health Level 7) es un estándar orientado al intercambio de información clínica en texto: historias clínicas, órdenes médicas, resultados de laboratorio, citas, entre otros. No maneja imágenes directamente.

La diferencia conceptual es clara: DICOM resuelve la comunicación de imágenes entre dispositivos médicos, mientras que HL7 resuelve la comunicación de datos clínicos entre sistemas de información hospitalaria. Ambos son complementarios y necesarios para la interoperabilidad completa en salud: un sistema PACS usa DICOM para recibir imágenes del tomógrafo y HL7 para asociarlas al historial del paciente en el sistema hospitalario.

---

## 3. Ecualización de histograma y detección de bordes con Canny en imágenes médicas

### Ecualización de histograma

**Ventajas:**
- Mejora el contraste en imágenes con rango dinámico reducido, haciendo visibles estructuras que de otro modo quedarían oscuras o sobreexpuestas.
- Es útil como paso de preprocesamiento antes de aplicar algoritmos de segmentación o detección.

**Limitaciones:**
- Puede amplificar el ruido de fondo junto con las estructuras de interés.
- En tomografías, donde los valores de intensidad tienen significado clínico preciso (unidades Hounsfield), la ecualización altera esa escala y puede distorsionar la interpretación diagnóstica.
- No es adecuada cuando el médico necesita comparar intensidades absolutas entre imágenes.

**Escenarios útiles:** preprocesamiento para algoritmos de machine learning, visualización exploratoria, imágenes con bajo contraste como radiografías de tórax.

**Escenarios donde puede ser perjudicial:** diagnóstico directo en tomografías o resonancias donde la intensidad original tiene valor clínico.

### Detección de bordes con Canny

**Ventajas:**
- Resalta contornos de estructuras anatómicas como huesos, órganos o tumores, lo que facilita la segmentación posterior.
- Es robusto frente al ruido cuando se ajustan bien los umbrales.

**Limitaciones:**
- Si los umbrales no son adecuados, puede detectar bordes irrelevantes (artefactos, ruido) o perder bordes importantes con bajo contraste.
- No distingue entre bordes clínicamente relevantes y los que no lo son.

**Escenarios útiles:** detección de fracturas en radiografías, delimitación de tumores, preprocesamiento para redes neuronales de segmentación médica.

**Escenarios donde puede ser perjudicial:** imágenes con mucho ruido donde los falsos bordes pueden inducir errores en diagnóstico automático.

En este proyecto se usaron umbrales de 50 (bajo) y 150 (alto) para Canny, valores que equilibran la sensibilidad ante bordes suaves con la supresión de ruido, apropiados para imágenes de prueba de tipo CT y MR.

---

## 4. Dificultades y herramientas de Python

**Dificultades encontradas:**
- La versión 3.0.2 de pydicom cambió el nombre de la función para acceder a archivos de prueba (`get_testfiles_name` fue reemplazada por `get_testdata_file`), lo que generó errores al intentar copiar los archivos de muestra.
- Algunos archivos DICOM no contienen datos de píxeles (modalidades SR, PR), por lo que fue necesario manejar estos casos con bloques `try/except` para que el programa no interrumpiera su ejecución.
- Las imágenes DICOM tienen profundidad de 12 o 16 bits, incompatible directamente con OpenCV, por lo que fue necesario normalizar a 8 bits antes de cualquier procesamiento.

**Importancia de las herramientas de Python:**
- `pydicom` permite acceder a cualquier tag del estándar DICOM de forma sencilla, sin necesidad de parsear archivos binarios manualmente.
- `pandas` facilita organizar los metadatos de múltiples archivos en una estructura tabular consultable y exportable.
- `numpy` permite operaciones matriciales sobre los píxeles de forma eficiente, tratando cada imagen como un arreglo numérico.
- `opencv-python` ofrece algoritmos de procesamiento de imagen listos para usar, ampliamente validados en contextos de visión por computadora e imágenes médicas.

---

## 5. Estructura del proyecto

```
Taller_3_MiguelT_StefaniaC/
├── datos_dicom/        ← archivos .dcm de entrada
├── salida/             ← imágenes procesadas generadas (.png)
├── procesador.py       ← clase ProcesadorDICOM
├── main.py             ← punto de entrada
├── requirements.txt    ← librerías necesarias
└── README.md           ← este archivo
```

---

## 6. Instalación y ejecución

```bash
# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python3 main.py
```

Las imágenes procesadas quedarán en la carpeta `salida/`.