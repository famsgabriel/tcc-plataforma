# o laço devolve uma lista de dicionários pra virar csv e resumo, com o tempo de cada etapa do ciclo, idade da entrada e watchdog
import csv
import time
from pathlib import Path

import numpy as np


def salvar_csv(registro, pasta):
    caminho = Path(pasta) / time.strftime("laco_%Y%m%d_%H%M%S.csv")
    caminho.parent.mkdir(exist_ok=True)
    with open(caminho, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=registro[0].keys())
        w.writeheader()
        w.writerows(registro)
    return caminho


def resumo(registro, dt):
    col = {c: np.array([r[c] for r in registro]) for c in registro[0]}
    periodo = np.diff(col["t"])  # tempo de parede entre o início de ciclos seguidos
    rtf = col["dt_sim"][1:].sum() / periodo.sum()  # tempo simulado / tempo de parede
    return "\n".join([
        f"ciclos {len(registro)}  dt {dt * 1e3:.1f} ms",
        f"tick     média {col['dur_tick'].mean() * 1e3:6.2f}  máx {col['dur_tick'].max() * 1e3:6.2f} ms",
        f"dados    média {col['dur_dados'].mean() * 1e3:6.2f}  máx {col['dur_dados'].max() * 1e3:6.2f} ms",
        f"período  média {periodo.mean() * 1e3:6.2f}  jitter (desvio) {periodo.std() * 1e3:.2f} ms",
        f"perdas de deadline {(col['folga'] < 0).sum()}  watchdog {col['watchdog'].sum()} ciclos  RTF {rtf:.4f}",
    ])
