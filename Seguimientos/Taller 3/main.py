"""
Integrantes:
    - Miguel Angel Toro
    - Stefania Concha Caceres
"""

from procesador import ProcesadorDICOM


def main():
    print("=" * 50)
    print("  SISTEMA DE PROCESAMIENTO DICOM")
    print("=" * 50)

    # Carpeta donde están los archivos .dcm
    carpeta = "datos_dicom"

    # Crear el procesador
    p = ProcesadorDICOM(carpeta)

    # Paso 1: Cargar archivos
    print("\n[1] Cargando archivos DICOM...")
    p.cargar_archivos()

    # Paso 2: Extraer metadatos
    print("[2] Extrayendo metadatos...")
    p.extraer_metadatos()

    # Paso 3: Analizar intensidad de píxeles
    print("[3] Calculando intensidad promedio...")
    p.analizar_intensidad()

    # Paso 4: Procesar imágenes con OpenCV
    print("[4] Procesando imágenes con OpenCV...")
    p.procesar_imagenes(carpeta_salida="salida")

    print("=" * 50)
    print("  Proceso completado.")
    print("  Imágenes guardadas en: salida/")
    print("=" * 50)


if __name__ == "__main__":
    main()