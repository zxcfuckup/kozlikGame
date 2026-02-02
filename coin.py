import pygame

class Coin:
    def __init__(self, x, y):
        # x, y здесь — координаты верхнего левого угла
        self.x = x
        self.y = y
        self.img = pygame.transform.smoothscale(
            pygame.image.load("contents/contentGame/coin.png").convert_alpha(), (32, 32)
        )
        self.collected = False

    def get_hitbox(self):
        # хитбокс строится по реальным размерам изображения
        return pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())

    def draw(self, screen, shake_y=0):
        if not self.collected:
            screen.blit(self.img, (self.x, self.y + shake_y))