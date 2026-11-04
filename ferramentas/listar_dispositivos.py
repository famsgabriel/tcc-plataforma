# lista os dispositivos evdev que têm eixos, com vendor:product e a faixa de cada eixo
# python ferramentas/listar_dispositivos.py   (python -m evdev.evtest)
import evdev
from evdev import ecodes

for caminho in evdev.list_devices():
    dev = evdev.InputDevice(caminho)
    eixos = dev.capabilities(verbose=True).get(("EV_ABS", ecodes.EV_ABS), [])
    if eixos:
        print(f"{dev.path}  {dev.info.vendor:#06x}:{dev.info.product:#06x}  {dev.name}")
        for (nome, _), info in eixos:
            print(f"    {nome:12}  min {info.min:7}  max {info.max:7}  atual {info.value:7}")
if not evdev.list_devices():
    print("nada para ler checar input")
