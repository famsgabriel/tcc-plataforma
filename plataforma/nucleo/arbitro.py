# por enquanto só o modo manual, com watchdog pela idade da entrada
import carla


def arbitrar(comando, idade, watchdog_s):  # (se tiver watchdog no comando)
    if idade > watchdog_s:  # desconectou ou perdeu
        return carla.VehicleControl(steer=comando.steer, brake=1.0), True
    return comando, False
