from screenIO import *
import pygame
import pygame.camera as cam

cam.init()
l = cam.list_cameras()

c = cam.Camera(l[0])

photos = []


c.start()


def GetPhotos():
    for _ in range(2):
        img = pygame.transform.flip(c.get_image().convert(), True, False)
        photos.append(img)
    # img = pygame.transform.flip(c.get_image().convert(), True, False)
    # photos.append(img)
    while len(photos) > 2:
        photos.pop(0)
    avg = pygame.transform.average_surfaces(photos)
    # avg = img

    # edges = pygame.transform.laplacian(avg)
    # avg.blit(edges, (0, 0), special_flags=pygame.BLEND_ADD)
    return avg


# if __name__ == '__main__':
#     def update(updater: 'Updater'):
#         updater.canvas.surface.blit(GetPhotos(), (0, 0))

#     upd = Updater().Setup(func=update, framerate=30)
#     upd.Play()
