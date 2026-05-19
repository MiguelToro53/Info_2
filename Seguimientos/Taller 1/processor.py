"""
Clase base abstracta (interfaz) Processor.
Todas las subclases deben implementar el método process().
Esto garantiza Herencia y Polimorfismo.
"""

from abc import ABC, abstractmethod
from biosignal import BioSignal


class Processor(ABC):
    """
    Clase base abstracta que define la interfaz genérica de procesamiento.

    Cualquier paso del pipeline (filtro, detector, etc.) extiende esta clase
    e implementa el método process() — garantizando polimorfismo.
    """

    def __init__(self, name: str = 'Processor'):
        self._name = str(name)
        self._params: dict = {}

    # ── Propiedades ─────────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        """Nombre descriptivo del procesador."""
        return self._name

    @property
    def params(self) -> dict:
        """Copia de los parámetros de configuración."""
        return self._params.copy()

    # ── Método abstracto (interfaz) ──────────────────────────────────────────

    @abstractmethod
    def process(self, signal: BioSignal) -> BioSignal:
        """
        Procesa una BioSignal y devuelve una nueva BioSignal transformada.
        Debe ser implementado por todas las subclases.

        Parámetros
        ----------
        signal : BioSignal  Señal de entrada.

        Devuelve
        --------
        BioSignal  Señal procesada.
        """

    # ── Representación ──────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self._name}')"
