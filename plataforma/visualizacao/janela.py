# synchronous_mode.py do carla 0.9.16: draw_image e should_quit usando pygame
import numpy as np
import pygame


def draw_image(surface, image, blend=False):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    array = array[:, :, :3]
    array = array[:, :, ::-1]
    image_surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
    if blend:
        image_surface.set_alpha(100)
    surface.blit(image_surface, (0, 0))


def should_quit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                return True
    return False


class Janela:
    def __init__(self, largura, altura):
        pygame.init()
        self.tela = pygame.display.set_mode((largura, altura), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.fonte = pygame.font.Font(None, 28)

    def mostrar(self, imagem, linhas):  # true se pediram para fechar
        draw_image(self.tela, imagem)
        for i, linha in enumerate(linhas):
            self.tela.blit(self.fonte.render(linha, True, (255, 255, 255), (0, 0, 0)), (10, 10 + 26 * i))
        pygame.display.flip()
        return should_quit()
