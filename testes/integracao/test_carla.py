import carla
import pytest
import yaml

from plataforma.nucleo.laco import rodar
from plataforma.sim.mundo import CarlaSyncMode, conectar, criar_ego

pytestmark = pytest.mark.carla


class Acelerador:  # testar comando de aceleracao
    def ler(self):
        return carla.VehicleControl(throttle=1.0), 0.0


def test_dirige_um_segundo_e_restaura():
    # prova que o laço dá 20 ticks seguidos com dt fixo, o ego anda e o servidor volta ao assíncrono
    with open("config/plataforma.yaml") as f:
        cfg = yaml.safe_load(f)
    cfg["laco"]["duracao_s"] = 1.0
    world = conectar(cfg)
    ego = criar_ego(world, cfg)
    registro = []
    try:
        with CarlaSyncMode(world, fps=1 / cfg["mundo"]["dt"]) as sync:
            rodar(world, ego, sync, Acelerador(), cfg, registro)
    finally:
        ego.destroy()
    assert len(registro) == 20
    assert all(r["dt_sim"] == pytest.approx(0.05) for r in registro)
    assert registro[-1]["velocidade"] > 0.5
    assert not world.get_settings().synchronous_mode
