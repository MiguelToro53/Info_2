"""
Script principal ejecutable del sistema de procesamiento de señales biomédicas.

Genera señales sintéticas de ECG y EMG, las procesa con pipelines específicos
y guarda métricas (CSV) y figuras en la carpeta 'results/'.

Uso:
    python main.py
"""

import numpy as np
import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from biosignal import BioSignal
from filters import BandpassFilter, NotchFilter
from event_detector import EventDetector
from pipeline import Pipeline
from experiment_runner import ExperimentRunner


# ── Generadores de señales sintéticas ────────────────────────────────────────

def generate_ecg(duration: float = 10.0, fs: float = 500.0,
                 noise_level: float = 0.05, heart_rate: float = 72.0,
                 add_powerline: bool = True) -> BioSignal:
    """
    Genera una señal ECG sintética PQRST, con ruido gaussiano
    e interferencia de red eléctrica (50 Hz).

    Parámetros
    ----------
    duration      : float  Duración [s].
    fs            : float  Frecuencia de muestreo [Hz].
    noise_level   : float  Amplitud del ruido gaussiano.
    heart_rate    : float  Ritmo cardíaco simulado [bpm].
    add_powerline : bool   Añadir interferencia de 50 Hz.
    """
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    ecg = np.zeros_like(t)

    rr = 60.0 / heart_rate          # Intervalo R-R [s]
    beat_times = np.arange(0.5, duration - 0.2, rr)

    def gauss(center, width, amp):
        return amp * np.exp(-((t - center) ** 2) / (2 * width ** 2))

    for bt in beat_times:
        ecg += gauss(bt - 0.20, 0.025, 0.12)   # Onda P
        ecg += gauss(bt - 0.05, 0.010, 0.12)   # Onda Q (negativa menor)
        ecg += gauss(bt,        0.008, 1.00)   # Pico R
        ecg -= gauss(bt + 0.04, 0.012, 0.22)   # Onda S
        ecg += gauss(bt + 0.20, 0.040, 0.30)   # Onda T

    ecg += noise_level * np.random.randn(len(t))

    if add_powerline:
        ecg += 0.10 * np.sin(2 * np.pi * 50.0 * t)

    return BioSignal(ecg, fs, 'ECG', name='ECG_sintetica')


def generate_emg(duration: float = 5.0, fs: float = 1000.0,
                 noise_level: float = 0.02, n_bursts: int = 3,
                 add_powerline: bool = True) -> BioSignal:
    """
    Genera una señal EMG sintética con ráfagas de activación muscular,
    ruido de línea base e interferencia de red eléctrica (50 Hz).

    Parámetros
    ----------
    duration      : float  Duración [s].
    fs            : float  Frecuencia de muestreo [Hz].
    noise_level   : float  Amplitud del ruido de línea de base.
    n_bursts      : int    Número de ráfagas de activación muscular.
    add_powerline : bool   Añadir interferencia de 50 Hz.
    """
    t = np.linspace(0, duration, int(duration * fs), endpoint=False)
    emg = noise_level * np.random.randn(len(t))     # Línea de base

    burst_dur = 0.5         # Duración de cada ráfaga [s]
    starts = np.linspace(0.5, duration - 1.0, n_bursts)

    for bs in starts:
        be = bs + burst_dur
        mask = (t >= bs) & (t <= be)
        env = np.sin(np.pi * (t[mask] - bs) / burst_dur)   # Envolvente
        emg[mask] += 0.8 * env * np.random.randn(np.sum(mask))

    if add_powerline:
        emg += 0.05 * np.sin(2 * np.pi * 50.0 * t)

    return BioSignal(emg, fs, 'EMG', name='EMG_sintetica')


# ── Constructores de pipelines ────────────────────────────────────────────────

def build_ecg_pipeline() -> tuple:
    """
    Construye el pipeline de procesamiento para señales ECG:
        Notch (50 Hz) → Pasa-banda (0.5–40 Hz) → Detector de eventos (R-peaks)
    """
    detector = EventDetector(threshold_factor=0.5, min_distance_s=0.3)

    pipe = Pipeline(name='ECG_Pipeline')
    pipe.add(NotchFilter(freq=50.0, quality=30.0))
    pipe.add(BandpassFilter(lowcut=0.5, highcut=40.0, order=4))
    pipe.add(detector)

    return pipe, detector


def build_emg_pipeline() -> tuple:
    """
    Construye el pipeline de procesamiento para señales EMG:
        Notch (50 Hz) → Pasa-banda (20–450 Hz) → Detector de eventos (RMS + activaciones)
    """
    detector = EventDetector(threshold_factor=0.5, min_distance_s=0.05)

    pipe = Pipeline(name='EMG_Pipeline')
    pipe.add(NotchFilter(freq=50.0, quality=30.0))
    pipe.add(BandpassFilter(lowcut=20.0, highcut=450.0, order=4))
    pipe.add(detector)

    return pipe, detector


# ── Función principal ─────────────────────────────────────────────────────────

def main():
    print("\n" + "═" * 50)
    print("   Sistema de Procesamiento de Señales Biomédicas")
    print("   ECG & EMG — Pipeline con Filtrado + Detección de Eventos")
    print("═" * 50)

    np.random.seed(42)      # Reproducibilidad

    runner = ExperimentRunner(output_dir='resultados')

    # ── Experimento 1: ECG ────────────────────────────────────────────────
    print("\n Generando señal ECG...")
    ecg = generate_ecg(duration=10.0, fs=500.0, noise_level=0.05,
                       heart_rate=72.0, add_powerline=True)
    print(f"   {ecg}")

    ecg_pipe, ecg_det = build_ecg_pipeline()
    print(f"\n   {ecg_pipe.summary()}")

    runner.run(ecg_pipe, ecg, ecg_det)

    # ── Experimento 2: ECG ritmo diferente ───────────────────────────────
    print("\n Generando señal ECG (ritmo 55 bpm)...")
    ecg2 = generate_ecg(duration=12.0, fs=500.0, noise_level=0.07,
                        heart_rate=55.0, add_powerline=True)
    ecg2._name = 'ECG_sintetica_55bpm'
    print(f"   {ecg2}")

    ecg_pipe2, ecg_det2 = build_ecg_pipeline()
    runner.run(ecg_pipe2, ecg2, ecg_det2)

    # ── Experimento 3: EMG ────────────────────────────────────────────────
    print("\n Generando señal EMG...")
    emg = generate_emg(duration=5.0, fs=1000.0, noise_level=0.02,
                       n_bursts=3, add_powerline=True)
    print(f"   {emg}")

    emg_pipe, emg_det = build_emg_pipeline()
    print(f"\n   {emg_pipe.summary()}")

    runner.run(emg_pipe, emg, emg_det)

    # ── Guardar bitácora ──────────────────────────────────────────────────
    runner.save_metrics_csv('metrics.csv')

    print("\n" + "═" * 50)
    print("  Todos los experimentos completados.")
    print("  Revisa la carpeta 'resultados/' para figuras y métricas.")
    print("═" * 50 + "\n")


if __name__ == '__main__':
    main()
