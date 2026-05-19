"""
Define la clase BioSignal que representa una señal biomédica 1D (ECG/EMG)
con su frecuencia de muestreo y metadatos básicos.
"""

import numpy as np


class BioSignal:
    """
    Representa una señal biomédica 1D (ECG o EMG) con su frecuencia de muestreo
    y metadatos básicos.
    Atributos privados/protegidos con validación (Encapsulación).
    """

    VALID_TYPES = ('ECG', 'EMG')

    def __init__(self, data, fs: float, signal_type: str, name: str = ''):
        """
        Parámetros
        ----------
        data        : array-like  Muestras de la señal (1D).
        fs          : float       Frecuencia de muestreo [Hz].
        signal_type : str         Tipo de señal ('ECG' o 'EMG').
        name        : str         Nombre descriptivo (opcional).
        """
        self._name = str(name)
        # Setters con validación
        self.data = data
        self.fs = fs
        self.signal_type = signal_type

    # ── Propiedades con validación ──────────────────────────────────────────

    @property
    def data(self) -> np.ndarray:
        """Array NumPy 1D con las muestras de la señal."""
        return self._data

    @data.setter
    def data(self, value):
        arr = np.asarray(value, dtype=float)
        if arr.ndim != 1:
            raise ValueError("Los datos de la señal deben ser un arreglo 1D.")
        if arr.size == 0:
            raise ValueError("El arreglo de datos no puede estar vacío.")
        self._data = arr
        """validacion de datos: convertir a NumPy, verificar 1D y no vacío."""
    @property
    def fs(self) -> float:
        """Frecuencia de muestreo [Hz]."""
        return self._fs

    @fs.setter
    def fs(self, value):
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError("La frecuencia de muestreo debe ser un número positivo.")
        self._fs = float(value)
        """validación de fs: debe ser un número positivo."""
    @property
    def signal_type(self) -> str:
        """Tipo de señal biomédica ('ECG' o 'EMG')."""
        return self._signal_type

    @signal_type.setter
    def signal_type(self, value: str):
        if value not in self.VALID_TYPES:
            raise ValueError(f"signal_type debe ser uno de {self.VALID_TYPES}.")
        self._signal_type = value
        """validación de signal_type: debe ser 'ECG' o 'EMG'."""
    @property
    def name(self) -> str:
        return self._name

    # ── Propiedades derivadas ───────────────────────────────────────────────

    @property
    def duration(self) -> float:
        """Duración de la señal en segundos."""
        return len(self._data) / self._fs

    @property
    def time(self) -> np.ndarray:
        """Eje temporal de la señal (segundos)."""
        return np.linspace(0, self.duration, len(self._data), endpoint=False)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return (
            f"BioSignal(name='{self._name}', type={self._signal_type}, "
            f"fs={self._fs} Hz, duration={self.duration:.2f} s, "
            f"samples={len(self._data)})"
        )

    def copy(self) -> 'BioSignal':
        """Devuelve una copia independiente de la señal."""
        return BioSignal(self._data.copy(), self._fs, self._signal_type, self._name)
