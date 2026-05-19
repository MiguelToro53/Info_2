"""
Subclases de Processor para filtrado de señales biomédicas:
  - BandpassFilter : filtro pasa-banda (aisla rango de frecuencias relevante).
  - NotchFilter    : filtro notch (elimina interferencia de red eléctrica 50/60 Hz).
"""

import numpy as np
from scipy import signal as scipy_signal
from processor import Processor
from biosignal import BioSignal


class BandpassFilter(Processor):
    """
    Filtro pasa-banda Butterworth para aislar el rango de frecuencias
    relevante de la señal (ECG: 0.5-40 Hz | EMG: 20-450 Hz).

    Hereda de Processor e implementa process().
    """

    def __init__(self, lowcut: float, highcut: float, order: int = 4):
        """
        Parámetros
        ----------
        lowcut  : float  Frecuencia de corte inferior [Hz].
        highcut : float  Frecuencia de corte superior [Hz].
        order   : int    Orden del filtro Butterworth (default 4).
        """
        super().__init__(name='BandpassFilter')
        # Setters con validación
        self.lowcut = lowcut
        self.highcut = highcut
        self.order = order
        self._params = {'lowcut': self._lowcut, 'highcut': self._highcut,
                        'order': self._order}

    # ── Propiedades con validación ──

    @property
    def lowcut(self) -> float:
        return self._lowcut

    @lowcut.setter
    def lowcut(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("lowcut debe ser un número positivo.")
        self._lowcut = float(value)

    @property
    def highcut(self) -> float:
        return self._highcut

    @highcut.setter
    def highcut(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("highcut debe ser un número positivo.")
        self._highcut = float(value)

    @property
    def order(self) -> int:
        return self._order

    @order.setter
    def order(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("order debe ser un entero positivo.")
        self._order = value

    # ── Implementación de process() ──

    def process(self, signal: BioSignal) -> BioSignal:
        """Aplica el filtro pasa-banda a la señal de entrada."""
        nyq = signal.fs / 2.0
        low = np.clip(self._lowcut / nyq, 1e-4, 0.9999)
        high = np.clip(self._highcut / nyq, 1e-4, 0.9999)

        if low >= high:
            raise ValueError(
                "lowcut debe ser estrictamente menor que highcut tras la normalización."
            )

        b, a = scipy_signal.butter(self._order, [low, high], btype='band')
        filtered = scipy_signal.filtfilt(b, a, signal.data)

        return BioSignal(filtered, signal.fs, signal.signal_type,
                         f"{signal.name}_bp")

    def __repr__(self) -> str:
        return (f"BandpassFilter(lowcut={self._lowcut} Hz, "
                f"highcut={self._highcut} Hz, order={self._order})")


# ──────────────────────────────────────────────────────────────────────────────


class NotchFilter(Processor):
    """
    Filtro notch (rechaza-banda estrecha) para eliminar interferencia de red
    eléctrica a una frecuencia específica (típicamente 50 Hz o 60 Hz).

    Hereda de Processor e implementa process().
    """

    def __init__(self, freq: float = 50.0, quality: float = 30.0):
        """
        Parámetros
        ----------
        freq    : float  Frecuencia a eliminar [Hz] (default 50 Hz).
        quality : float  Factor de calidad Q del filtro (default 30).
        """
        super().__init__(name='NotchFilter')
        self.freq = freq
        self.quality = quality
        self._params = {'freq': self._freq, 'quality': self._quality}

    # ── Propiedades con validación ────

    @property
    def freq(self) -> float:
        return self._freq

    @freq.setter
    def freq(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("freq debe ser un número positivo.")
        self._freq = float(value)

    @property
    def quality(self) -> float:
        return self._quality

    @quality.setter
    def quality(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("quality debe ser un número positivo.")
        self._quality = float(value)

    # ── Implementación de process() ────

    def process(self, signal: BioSignal) -> BioSignal:
        """Aplica el filtro notch para eliminar la frecuencia de interferencia."""
        b, a = scipy_signal.iirnotch(self._freq, self._quality, signal.fs)
        filtered = scipy_signal.filtfilt(b, a, signal.data)

        return BioSignal(filtered, signal.fs, signal.signal_type,
                         f"{signal.name}_notch")

    def __repr__(self) -> str:
        return f"NotchFilter(freq={self._freq} Hz, Q={self._quality})"
