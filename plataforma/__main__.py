# python -m plataforma [--entrada config/8bitdo.yaml] [--visual] [--duracao s]
import argparse

import carla
import yaml

from plataforma.nucleo.laco import rodar
from plataforma.sim.mundo import CarlaSyncMode, conectar, criar_camera, criar_ego
from plataforma.telemetria.registro import resumo, salvar_csv


class SemControle:  # sem --entrada so freia e para - melhorar isso pra testar de repente, caso de teste
    def ler(self):
        return carla.VehicleControl(brake=1.0), 0.0


def main():
    p = argparse.ArgumentParser(prog="plataforma")
    p.add_argument("--entrada", help="yaml do controle, ex.: config/8bitdo.yaml")
    p.add_argument("--visual", action="store_true", help="câmera do ego numa janela")
    p.add_argument("--duracao", type=float, help="segundos; 0 = até ctrl+c ou esc")
    a = p.parse_args()
    with open("config/plataforma.yaml") as f:
        cfg = yaml.safe_load(f)
    if a.duracao is not None:
        cfg["laco"]["duracao_s"] = a.duracao
    dt = cfg["mundo"]["dt"]
    assert 1 / 30 - 1e-9 <= dt <= 1 / 20 + 1e-9, "dt deve ficar entre 1/30 e 1/20 s"

    if a.entrada:
        from plataforma.entrada.leitura_evdev import Controle
        controle = Controle(a.entrada)
    else:
        controle = SemControle()
    world = conectar(cfg)
    atores, janela, registro = [], None, []
    try:
        ego = criar_ego(world, cfg)
        atores.append(ego)
        if a.visual:
            from plataforma.visualizacao.janela import Janela
            atores.append(criar_camera(world, ego, cfg))
            janela = Janela(cfg["camera"]["largura"], cfg["camera"]["altura"])
        with CarlaSyncMode(world, *atores[1:], fps=1 / dt) as sync:  # reseta config
            rodar(world, ego, sync, controle, cfg, registro, janela)
    except KeyboardInterrupt:
        print("\ninterrompido")
    finally:
        for ator in reversed(atores):  # camera antes do ego
            ator.destroy()
        if registro:
            print(resumo(registro, dt))
            print(f"registro em {salvar_csv(registro, cfg['registro']['pasta'])}")


if __name__ == "__main__":
    main()
