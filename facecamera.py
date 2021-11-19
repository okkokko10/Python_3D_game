from screenIO import *
import pygame
import pygame.camera as cam
from render3D import *

cam.init()
l = cam.list_cameras()

c = cam.Camera(l[0])

photos = []


c.start()


def GetPhotos():
    img = pygame.transform.flip(c.get_image().convert(), True, False)
    photos.append(img)
    if len(photos) > 2:
        photos.pop(0)
    avg = pygame.transform.average_surfaces(photos)

    edges = pygame.transform.laplacian(avg)
    avg.blit(edges, (0, 0), special_flags=pygame.BLEND_ADD)
    return avg


if __name__ == '__main__':
    def update(updater: 'Updater'):
        updater.canvas.surface.blit(GetPhotos(), (0, 0))

    upd = Updater().Setup(func=update, framerate=30)
    upd.Play()
