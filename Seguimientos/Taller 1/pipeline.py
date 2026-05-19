"""
Clase Pipeline que representa una cadena de procesamiento compuesta por
varios objetos Processor aplicados en orden sobre una BioSignal.
"""

from typing import List
from processor import Processor
from biosignal import BioSignal


class Pipeline:
    """
    Cadena/flujo de procesamiento compuesta por varios Processor aplicados
    secuencialmente sobre una BioSignal.

    Flujo recomendado:
        Señal original → Notch → Bandpass → EventDetector
    """

    def __init__(self, name: str = 'Pipeline'):
        self._name = str(name)
        self._processors: List[Processor] = []
        self._intermediate_signals: List[BioSignal] = []

    # ── Propiedades ────

    @property
    def name(self) -> str:
        return self._name

    @property
    def processors(self) -> List[Processor]:
        """Copia de la lista de procesadores en el pipeline."""
        return self._processors.copy()

    @property
    def intermediate_signals(self) -> List[BioSignal]:
        """
        Lista de señales intermedias (incluye original + resultado de cada paso).
        Disponible después de llamar a run().
        """
        return self._intermediate_signals.copy()

    # ── Métodos públicos ─────

    def add(self, processor: Processor) -> 'Pipeline':
        """
        Añade un Processor al final del pipeline.
        Devuelve self para permitir encadenamiento fluido.
        """
        if not isinstance(processor, Processor):
            raise TypeError(
                f"Se esperaba un objeto Processor, se recibió {type(processor).__name__}."
            )
        self._processors.append(processor)
        return self

    def run(self, signal: BioSignal) -> BioSignal:
        """
        Ejecuta el pipeline completo sobre la señal de entrada.

        Aplica cada Processor en orden y almacena las señales intermedias.

        Parámetros
        ----------
        signal : BioSignal  Señal de entrada.

        Devuelve
        --------
        BioSignal  Señal resultante tras todos los pasos de procesamiento.
        """
        if not self._processors:
            raise RuntimeError("El pipeline no contiene procesadores.")

        self._intermediate_signals = [signal]   # Guardar señal original
        current = signal

        for proc in self._processors:
            print(f"   Ejecutando: {proc}")
            current = proc.process(current)
            self._intermediate_signals.append(current)

        return current

    def summary(self) -> str:
        """Devuelve un resumen legible de los pasos del pipeline."""
        steps = " → ".join(str(p) for p in self._processors)
        return f"Pipeline '{self._name}': {steps}"

    def __len__(self) -> int:
        return len(self._processors)

    def __repr__(self) -> str:
        steps = " → ".join(p.name for p in self._processors)
        return f"Pipeline(name='{self._name}', steps=[{steps}])"
