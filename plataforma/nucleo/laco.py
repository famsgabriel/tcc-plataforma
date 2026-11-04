# núcleo cíclico, tickar o mundo
# pacing, entrada, arbitrador, controle, tick, estado e janela
import time

from plataforma.nucleo.arbitro import arbitrar


def proximo_alvo(t0, k, dt, agora):  # deadline absoluto t0 + k*dt; se atrasou reancora 
    alvo = t0 + k * dt
    folga = alvo - agora
    if folga < 0:
        t0, alvo = t0 - folga, agora
    return t0, alvo, folga


def esperar_ate(alvo, margem_s):
    if alvo - time.perf_counter() > margem_s:
        time.sleep(alvo - time.perf_counter() - margem_s)  # sleep grosso
    while time.perf_counter() < alvo:  # espera ativa no fim
        pass


def rodar(world, ego, sync, controle, cfg, registro, janela=None):  #lista preenchida ciclo a ciclo
    dt, laco = cfg["mundo"]["dt"], cfg["laco"]
    n = round(laco["duracao_s"] / dt)  # 0 = sem fim
    t0 = time.perf_counter() + dt  # um dt à frente pra nao nascer atrasado
    k = 0
    while n == 0 or k < n:
        t0, alvo, folga = proximo_alvo(t0, k, dt, time.perf_counter())
        esperar_ate(alvo, laco["margem_s"])
        t1 = time.perf_counter()
        comando, idade = controle.ler()
        comando, watchdog = arbitrar(comando, idade, laco["watchdog_s"])
        ego.apply_control(comando)
        t2 = time.perf_counter()
        frame = world.tick(cfg["servidor"]["timeout_s"])
        t3 = time.perf_counter()
        snapshot, *imagens = sync.dados(frame, cfg["servidor"]["timeout_s"])  # mesmo frame do tick
        t4 = time.perf_counter()
        velocidade = snapshot.find(ego.id).get_velocity().length()
        if janela and janela.mostrar(imagens[0], [f"{velocidade * 3.6:5.1f} km/h",
                                                  f"acel {comando.throttle:.2f}  freio {comando.brake:.2f}  "
                                                  f"direção {comando.steer:+.2f}"]
                                     + (["WATCHDOG"] if watchdog else [])):
            break  # janela fechada ou esc
        registro.append({"k": k, "t": t1, "folga": folga, "dur_entrada": t2 - t1, "dur_tick": t3 - t2,
                         "dur_dados": t4 - t3, "dur_janela": time.perf_counter() - t4,
                         "dt_sim": snapshot.timestamp.delta_seconds, "idade_entrada": idade,
                         "watchdog": watchdog, "throttle": comando.throttle, "brake": comando.brake,
                         "steer": comando.steer, "velocidade": velocidade})
        k += 1
