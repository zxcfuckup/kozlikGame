import pygame
import random


class Platform:
    def __init__(self, x, y, w, h, images, fake=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.fake = fake
        self.scored = False
        self.img = images["fake"] if fake else random.choice([images["cloudB"], images["cloudM"], images["grass"]])
        self.draw_offset_y = 40

        # --- НОВОЕ ДЛЯ СЛОЖНОСТИ ---
        self.is_moving = random.random() < 0.2  # 20% платформ будут двигаться
        self.speed = random.choice([-2, 2])  # Случайное направление
        # ---------------------------

    def update(self, design_w, speed_mult):
        if self.is_moving:
            # Платформы двигаются быстрее со временем
            self.rect.x += self.speed * speed_mult
            # Отскок от краев
            if self.rect.right > design_w or self.rect.left < 0:
                self.speed *= -1

    def get_visual_top(self):
        return self.rect.y - self.draw_offset_y

    def draw(self, screen, shake_y=0):
        screen.blit(self.img, (self.rect.x - 25, self.rect.y - self.draw_offset_y + shake_y))
