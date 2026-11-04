# dstravar o servidor se tiver cliente morto
import carla
import yaml

with open("config/plataforma.yaml") as f:
    s = yaml.safe_load(f)["servidor"]
world = carla.Client(s["host"], s["porta"]).get_world()
world.apply_settings(carla.WorldSettings(synchronous_mode=False))
print("mundo restaurado para modo assíncrono")
