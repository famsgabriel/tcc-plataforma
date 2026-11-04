# mostrar as grandezas (camada 1), o comando (camada 2) e a idade da entrada
# python ferramentas/monitorar_entrada.py [config/8bitdo.yaml]
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from plataforma.entrada.leitura_evdev import Controle  # noqa: E402

controle = Controle(sys.argv[1] if len(sys.argv) > 1 else "config/8bitdo.yaml")
print("ctrl+c para sair")
try:
    while True:
        comando, idade = controle.ler()
        g = controle.grandezas
        print(f"\rvolante {g['angulo_volante_graus']:+7.1f}°  acel {g['pedal_acelerador']:.2f}  "
              f"freio {g['pedal_freio']:.2f}  | steer {comando.steer:+.3f}  | idade {idade * 1e3:5.1f} ms",
              end="", flush=True)
        time.sleep(0.1)
except KeyboardInterrupt:
    print()
