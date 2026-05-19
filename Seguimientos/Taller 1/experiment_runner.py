"""
Clase ExperimentRunner: controla corridas del Pipeline, guarda métricas en CSV
y genera figuras de los resultados.
"""

import os
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Optional

from pipeline import Pipeline
from biosignal import BioSignal
from event_detector import EventDetector


class ExperimentRunner:
    """
    Orquestador de experimentos: ejecuta el Pipeline con distintas señales,
    guarda métricas (bitácora CSV) y genera figuras.
    """

    def __init__(self, output_dir: str = 'results'):
        self._output_dir = output_dir
        self._figures_dir = os.path.join(output_dir, 'figures')
        self._results: list = []
        self._run_count: int = 0

        os.makedirs(self._figures_dir, exist_ok=True)

    # ── Propiedades ─────────────────────────────────────────────────────────

    @property
    def output_dir(self) -> str:
        return self._output_dir

    @property
    def results(self) -> list:
        return self._results.copy()

    @property
    def run_count(self) -> int:
        return self._run_count

    # ── Método principal ────────────────────────────────────────────────────

    def run(self, pipeline: Pipeline, signal: BioSignal,
            event_detector: EventDetector) -> tuple:
        """
        Ejecuta el pipeline sobre la señal y almacena resultados.

        Parámetros
        ----------
        pipeline       : Pipeline        Pipeline de procesamiento a ejecutar.
        signal         : BioSignal       Señal de entrada.
        event_detector : EventDetector   Referencia al detector para leer métricas.

        Devuelve
        --------
        tupla (BioSignal procesada, dict de métricas)
        """
        self._run_count += 1
        run_id = f"run_{self._run_count:03d}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\n{'━'*60}")
        print(f"  Experimento : {run_id}")
        print(f"  Señal       : {signal.name}  |  Tipo: {signal.signal_type}")
        print(f"  Duración    : {signal.duration:.2f} s  |  fs: {signal.fs} Hz")
        print(f"{'━'*60}")

        # Ejecutar pipeline
        processed = pipeline.run(signal)

        # Leer métricas del detector
        metrics = event_detector.metrics
        events = event_detector.events

        # Guardar registro
        record = {
            'run_id':        run_id,
            'timestamp':     timestamp,
            'signal_name':   signal.name,
            'signal_type':   signal.signal_type,
            'fs_hz':         signal.fs,
            'duration_s':    round(signal.duration, 4),
            'num_processors': len(pipeline),
            **metrics,
        }
        self._results.append(record)

        # Imprimir métricas
        print(f"\n  Métricas:")
        for k, v in metrics.items():
            print(f"      {k}: {v}")

        # Generar y guardar figura
        fig_path = self._save_figure(
            pipeline.intermediate_signals, events, signal, run_id, metrics
        )
        print(f"\n  Figura guardada: {fig_path}")

        return processed, metrics

    # ── Métodos privados ────────────────────────────────────────────────────

    def _save_figure(self, signals: list, events: list,
                     original: BioSignal, run_id: str, metrics: dict) -> str:
        """Genera y guarda la figura de procesamiento por etapas."""

        stage_labels = [
            'Original (con ruido)',
            'Tras Filtro Notch (50 Hz)',
            'Tras Filtro Pasa-Banda',
            'Detección de Eventos',
        ]
        colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

        n = len(signals)
        fig, axes = plt.subplots(n, 1, figsize=(13, 3.2 * n), sharex=True)
        if n == 1:
            axes = [axes]

        for i, (sig, ax) in enumerate(zip(signals, axes)):
            t = sig.time
            label = stage_labels[i] if i < len(stage_labels) else f'Etapa {i}'
            color = colors[i % len(colors)]

            ax.plot(t, sig.data, color=color, linewidth=0.75, label=label, zorder=2)

            # Marcar eventos en la última etapa
            if i == n - 1 and events:
                ev_idx = [e for e in events if e < len(sig.data)]
                ev_t = np.array(ev_idx) / sig.fs
                ev_v = sig.data[ev_idx]
                ax.scatter(ev_t, ev_v, color='crimson', s=45, zorder=5,
                           label='Eventos detectados', marker='o')

            ax.set_ylabel('Amplitud (mV)', fontsize=9)
            ax.set_title(f'Etapa {i+1}: {label}', fontsize=9, loc='left',
                         fontweight='bold', color=colors[i % len(colors)])
            ax.legend(loc='upper right', fontsize=8, framealpha=0.8)
            ax.grid(True, alpha=0.25, linestyle='--')
            ax.spines[['top', 'right']].set_visible(False)

        axes[-1].set_xlabel('Tiempo (s)', fontsize=10)

        # Métricas en el título general
        metrics_str = '   |   '.join(
            f"{k}: {v}" for k, v in metrics.items()
            if k != 'signal_type' and v is not None
        )
        fig.suptitle(
            f"Pipeline — {original.signal_type}  ·  {run_id}\n{metrics_str}",
            fontsize=10, fontweight='bold', y=1.01
        )

        plt.tight_layout()
        fig_path = os.path.join(self._figures_dir, f'{run_id}_{original.signal_type}.png')
        plt.savefig(fig_path, dpi=150, bbox_inches='tight')
        plt.close()
        return fig_path

    # ── Guardar bitácora CSV ────────────────────────────────────────────────

    def save_metrics_csv(self, filename: str = 'metrics.csv') -> str:
        """Guarda todas las métricas recopiladas en un archivo CSV."""
        if not self._results:
            print("No hay resultados para guardar.")
            return ''

        filepath = os.path.join(self._output_dir, filename)

        # Unión de todas las claves posibles
        all_keys: list = []
        seen = set()
        for row in self._results:
            for k in row:
                if k not in seen:
                    all_keys.append(k)
                    seen.add(k)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=all_keys, extrasaction='ignore')
            writer.writeheader()
            for row in self._results:
                writer.writerow(row)

        print(f"\n  Bitácora CSV guardada: {filepath}")
        return filepath

    def __repr__(self) -> str:
        return (f"ExperimentRunner(output_dir='{self._output_dir}', "
                f"runs={self._run_count})")
