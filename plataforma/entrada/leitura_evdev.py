# usando thread, testar com processo separado para não travar o servidor se a thread morrer - pesquisar
# camada 1: eixo bruto -> grandeza física (graus, [0, 1]); camada 2: grandezas -> carla.VehicleControl
import math
import select
import threading
import time

import carla
import evdev
import yaml
from evdev import ecodes


def converter(bruto, eixo):  # camada 1, com a zona morta a partir do repouso
    u = min(1.0, max(0.0, (bruto - eixo["min"]) / (eixo["max"] - eixo["min"])))
    zm = eixo["zona_morta"]
    if eixo["repouso"] == "centro":
        c = 2 * u - 1
        c = 0.0 if abs(c) <= zm else math.copysign((abs(c) - zm) / (1 - zm), c)
        u = (c + 1) / 2
    else:
        u = 0.0 if u <= zm else (u - zm) / (1 - zm)
    lo, hi = eixo["saida"]
    return lo + u * (hi - lo)


def para_comando(g, cfg):  # camada 2
    steer = g["angulo_volante_graus"] / cfg["veiculo"]["angulo_volante_max_graus"]
    return carla.VehicleControl(throttle=g["pedal_acelerador"], brake=g["pedal_freio"],
                                steer=max(-1.0, min(1.0, steer)))  # o carla não satura


def achar_dispositivo(cfg):  #achar eixo da config
    d = cfg["dispositivo"]
    codigos = {ecodes.ecodes[e["codigo"]] for e in cfg["eixos"].values()}
    for caminho in evdev.list_devices():
        dev = evdev.InputDevice(caminho)
        eixos = {cod for cod, _ in dev.capabilities().get(ecodes.EV_ABS, [])}
        if (dev.info.vendor, dev.info.product) == (d["vendor"], d["product"]) and codigos <= eixos:
            return dev
        dev.close()
    raise RuntimeError(f"{d['nome']} desligado ou fora do input")


class Controle:
    def __init__(self, caminho_cfg):
        with open(caminho_cfg) as f:
            self.cfg = yaml.safe_load(f)
        self.dev = achar_dispositivo(self.cfg)
        self._eixos = {ecodes.ecodes[e["codigo"]]: (nome, e) for nome, e in self.cfg["eixos"].items()}
        self.grandezas = {nome: converter(self.dev.absinfo(cod).value, e)  # posição atual de cada eixo
                          for cod, (nome, e) in self._eixos.items()}
        self.instante = time.perf_counter()
        self._lock = threading.Lock()
        threading.Thread(target=self._ler, daemon=True).start()

    def _ler(self):
        try:
            while True:
                if select.select([self.dev.fd], [], [], 0.01)[0]:  # heartbeat
                    for ev in self.dev.read():
                        if ev.type == ecodes.EV_ABS and ev.code in self._eixos:
                            nome, e = self._eixos[ev.code]
                            with self._lock:
                                self.grandezas[nome] = converter(ev.value, e)
                with self._lock:
                    self.instante = time.perf_counter()  # watchdog ve a thread viva
        except OSError:
            print("[entrada] controle desconectado")  # para de atualizar e o watchdog assume

    def ler(self):  # (comando, idade da última atualização em s ra retomar)
        with self._lock:
            g, instante = dict(self.grandezas), self.instante
        return para_comando(g, self.cfg), time.perf_counter() - instante
