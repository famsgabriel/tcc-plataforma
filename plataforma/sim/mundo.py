# synchronous_mode.py do carla 0.9.16 (CarlaSyncMode), tick foi pro laco, aqui ficam os frame, que pega da fila o dado daquele frame
import queue

import carla


def conectar(cfg):
    client = carla.Client(cfg["servidor"]["host"], cfg["servidor"]["porta"])
    client.set_timeout(cfg["servidor"]["timeout_s"])
    world = client.get_world()
    if not world.get_map().name.endswith(cfg["mundo"]["mapa"]):
        world = client.load_world(cfg["mundo"]["mapa"])
    return world


def criar_ego(world, cfg):
    bp = world.get_blueprint_library().find(cfg["ego"]["blueprint"])
    ponto = world.get_map().get_spawn_points()[cfg["ego"]["ponto_spawn"]]
    return world.spawn_actor(bp, ponto)


def criar_camera(world, ego, cfg):
    c = cfg["camera"]
    bp = world.get_blueprint_library().find("sensor.camera.rgb")
    bp.set_attribute("image_size_x", str(c["largura"]))
    bp.set_attribute("image_size_y", str(c["altura"]))
    v = c["vistas"][c["vista"]]  
    posicao = carla.Transform(carla.Location(x=v["x"], y=v["y"], z=v["z"]), carla.Rotation(pitch=v["pitch"]))
    fixacao = getattr(carla.AttachmentType, v["fixacao"])  # "SpringArmGhost" -> carla.AttachmentType.SpringArmGhost
    return world.spawn_actor(bp, posicao, attach_to=ego, attachment_type=fixacao)



class CarlaSyncMode(object):
    def __init__(self, world, *sensors, **kwargs):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self.delta_seconds = 1.0 / kwargs.get('fps', 20)
        self._queues = []
        self._settings = None

    def __enter__(self):
        self._settings = self.world.get_settings()
        self.frame = self.world.apply_settings(carla.WorldSettings(
            no_rendering_mode=False,
            synchronous_mode=True,
            fixed_delta_seconds=self.delta_seconds))

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def dados(self, frame, timeout):  # world tick no laco pra controlar o pacing, aqui pega da fila o dado daquele frame
        self.frame = frame
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data
