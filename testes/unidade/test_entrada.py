import yaml

from plataforma.entrada.leitura_evdev import converter, para_comando

with open("config/8bitdo.yaml") as f:
    CFG = yaml.safe_load(f)
VOLANTE, ACEL = CFG["eixos"]["angulo_volante_graus"], CFG["eixos"]["pedal_acelerador"]


def test_volante_em_graus():
    # camada 1 do volante, se batentes viram ±450 e o centro (com zona morta) vira 0
    assert converter(-32768, VOLANTE) == -450.0
    assert converter(32767, VOLANTE) == 450.0
    assert converter(500, VOLANTE) == 0.0


def test_pedal_em_zero_a_um():
    # camada 1 do pedal: solto vale 0, até o fim vale 1
    assert converter(0, ACEL) == 0.0
    assert converter(255, ACEL) == 1.0


def test_volante_de_270_e_900_graus():
    # camada 2: o mesmo ângulo físico dá steer diferente conforme o batente do volante
    g = {"angulo_volante_graus": 90.0, "pedal_acelerador": 0.0, "pedal_freio": 0.0}
    assert round(para_comando(g, CFG).steer, 3) == 0.2  # 900° (batente em 450°)
    cfg_270 = {"veiculo": {"angulo_volante_max_graus": 135.0}}
    assert round(para_comando(g, cfg_270).steer, 3) == 0.667
