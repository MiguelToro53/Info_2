"""
Subclase de Processor que detecta eventos fisiológicos en señales biomédicas:
  - ECG : detecta picos R y calcula ritmo cardíaco medio [bpm].
  - EMG : calcula RMS y detecta inicios de activación muscular.
"""

import numpy as np
from scipy import signal as scipy_signal
from processor import Processor
from biosignal import BioSignal


class EventDetector(Processor):
    """
    Detector de eventos fisiológicos (latidos cardíacos o activaciones musculares).

    El comportamiento de process() varía según el tipo de señal (polimorfismo), conservando la misma firma del método heredado.

    Hereda de Processor e implementa process().
    """

    def __init__(self, threshold_factor: float = 0.5, min_distance_s: float = 0.3):
        """
        threshold_factor : float  Fracción del máximo de la señal para umbral
                                  de detección (0 < factor ≤ 1, base 0.5).
        min_distance_s   : float  Distancia mínima entre eventos detectados
                                  en segundos (base 0.3 s ≈ 200 bpm máx).
        """
        super().__init__(name='EventDetector')
        self.threshold_factor = threshold_factor
        self.min_distance_s = min_distance_s

        self._events: list = []          # Índices de los eventos detectados
        self._metrics: dict = {}         # Métricas calculadas

        self._params = {
            'threshold_factor': self._threshold_factor,
            'min_distance_s': self._min_distance_s,
        }

    # ── Propiedades con validación ──────────────────────────────────────────

    @property
    def threshold_factor(self) -> float:
        return self._threshold_factor

    @threshold_factor.setter
    def threshold_factor(self, value):
        if not isinstance(value, (int, float)) or not (0 < value <= 1):
            raise ValueError("threshold_factor debe estar en el intervalo (0, 1].")
        self._threshold_factor = float(value)

    @property
    def min_distance_s(self) -> float:
        return self._min_distance_s

    @min_distance_s.setter
    def min_distance_s(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("min_distance_s debe ser un número positivo.")
        self._min_distance_s = float(value)

    @property
    def events(self) -> list:
        """Lista de índices de los eventos detectados."""
        return self._events.copy()

    @property
    def metrics(self) -> dict:
        """Diccionario con las métricas calculadas tras la última llamada a process()."""
        return self._metrics.copy()

    # ── Implementación de process() ─────────────────────────────────────────

    def process(self, signal: BioSignal) -> BioSignal:
        """
        Detecta eventos fisiológicos y calcula métricas según el tipo de señal.

        - ECG → Detecta picos R y calcula ritmo cardíaco medio [bpm].
        - EMG → Calcula RMS y detecta inicios de activación muscular.

        Devuelve la señal sin modificar (paso de registro/análisis).
        """
        if signal.signal_type == 'ECG':
            self._process_ecg(signal)
        elif signal.signal_type == 'EMG':
            self._process_emg(signal)

        return BioSignal(signal.data.copy(), signal.fs, signal.signal_type,
                         f"{signal.name}_events")

    # ── Métodos privados de detección ───────────────────────────────────────

    def _process_ecg(self, signal: BioSignal) -> None:
        """Detecta picos R en señal ECG y calcula ritmo cardíaco medio."""
        data = signal.data
        fs = signal.fs
        min_dist = max(1, int(self._min_distance_s * fs))
        threshold = self._threshold_factor * np.max(data)

        peaks, _ = scipy_signal.find_peaks(
            data, height=threshold, distance=min_dist
        )
        self._events = peaks.tolist()

        if len(peaks) >= 2:
            rr_s = np.diff(peaks) / fs          # Intervalos R-R en segundos
            mean_rr = float(np.mean(rr_s))
            # Ritmo cardíaco medio = 60 / distancia media entre picos
            hr_bpm = round(60.0 / mean_rr, 2)
            self._metrics = {
                'signal_type':          'ECG',
                'num_beats':            len(peaks),
                'mean_rr_interval_s':   round(mean_rr, 4),
                'mean_heart_rate_bpm':  hr_bpm,
            }
        else:
            self._metrics = {
                'signal_type':         'ECG',
                'num_beats':           len(peaks),
                'mean_rr_interval_s':  None,
                'mean_heart_rate_bpm': None,
            }

    def _process_emg(self, signal: BioSignal) -> None:
        """Calcula RMS de la señal EMG y detecta inicios de activación muscular."""
        data = signal.data
        fs = signal.fs

        # Métrica principal: RMS (Raíz cuadrática media)
        rms = float(np.sqrt(np.mean(data ** 2)))

        # Detección de activaciones: muestras sobre el umbral
        threshold = self._threshold_factor * float(np.max(np.abs(data)))
        above = np.abs(data) > threshold

        # Inicios de activación (flancos de subida)
        onsets = np.where(np.diff(above.astype(int)) == 1)[0]
        self._events = onsets.tolist()

        self._metrics = {
            'signal_type':     'EMG',
            'rms':             round(rms, 6),
            'num_activations': int(len(onsets)),
            'threshold_used':  round(threshold, 6),
        }

    def __repr__(self) -> str:
        return (f"EventDetector(threshold_factor={self._threshold_factor}, "
                f"min_distance_s={self._min_distance_s})")
