import pygame
import random

class Platform:
    def __init__(self, x, y, w, h, images, fake=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.fake = fake
        self.scored = False
        # выбирается изображение
        self.img = images["fake"] if fake else random.choice([images["cloudB"], images["cloudM"], images["grass"]])

        self.draw_offset_y = 40

    def get_visual_top(self):

        return self.rect.y - self.draw_offset_y

    def draw(self, screen, shake_y=0):

        screen.blit(self.img, (self.rect.x - 25, self.rect.y - self.draw_offset_y + shake_y))