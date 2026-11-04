import carla
import pytest

from plataforma.nucleo.arbitro import arbitrar
from plataforma.nucleo.laco import proximo_alvo


def test_deadline_absoluto_sem_deriva():
    # ver se nao tem acumulação vendo t0 + kdt
    t0, alvo, folga = proximo_alvo(100.0, 2000, 0.05, agora=199.0)
    assert alvo == pytest.approx(200.0) and folga > 0


def test_atraso_reancora():
    # ciclo atrasado roda na hora e que o atraso vira folga negativa (perda de deadline)
    t0, alvo, folga = proximo_alvo(100.0, 1, 0.05, agora=100.08)
    assert alvo == 100.08 and folga == pytest.approx(-0.03)


def test_watchdog():
    # entrada recente passa direto e entrada velha zera o acelerador e freia
    comando = carla.VehicleControl(throttle=0.7, steer=-0.3)
    assert arbitrar(comando, 0.05, 0.1) == (comando, False)
    seguro, disparou = arbitrar(comando, 0.2, 0.1)
    assert disparou and seguro.throttle == 0.0 and seguro.brake == 1.0
