import pygame
import random


class Platform:
    def __init__(self, x, y, w, h, images, fake=False):
        # Выбираем изображение сразу
        self.img = images["fake"] if fake else random.choice([images["cloudB"], images["cloudM"], images["grass"]])

        # Создаем маску для столкновений по прозрачности
        self.mask = pygame.mask.from_surface(self.img)

        # Физический rect теперь подгоняем под размер картинки для точности маски
        self.rect = self.img.get_rect(topleft=(x, y))

        self.fake = fake
        self.scored = False
        self.is_moving = random.random() < 0.2
        self.speed = random.choice([-2, 2])

    def update(self, design_w, speed_mult):
        if self.is_moving:
            self.rect.x += self.speed * speed_mult
            if self.rect.right > design_w or self.rect.left < 0:
                self.speed *= -1

    def get_visual_top(self):
        return self.rect.top

    def draw(self, screen, shake_y=0):
        # Рисуем ровно там, где находится rect
        screen.blit(self.img, (self.rect.x, self.rect.y + shake_y))
