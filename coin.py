import pygame
import math


class Coin:
    def __init__(self, x, y):
        # Сохраняем начальные координаты
        self.x = x
        self.y = y
        # Загружаем оригинал один раз, чтобы не терять качество при масштабировании
        self.original_img = pygame.transform.smoothscale(
            pygame.image.load("contents/contentGame/coin.png").convert_alpha(), (32, 32)
        )
        self.collected = False

        # Переменные для анимации
        self.angle = 0.0  # Угол для вращения
        self.float_offset = 0.0  # Для эффекта парения

    def get_hitbox(self):
        # Хитбокс остается стабильным, даже если картинка сужается
        return pygame.Rect(self.x, self.y, 32, 32)

    def update(self, dt=1):
        """Обновляем фазу анимации"""
        # Скорость вращения
        self.angle += 0.05 * dt
        # Скорость парения
        self.float_offset = math.sin(self.angle * 0.5) * 5

    def draw(self, screen, offset_y=0):
        if not self.collected:
            # Магия вращения: вычисляем текущую ширину через косинус
            # Ширина будет меняться от 32 до 0 и обратно
            curr_w = abs(int(math.cos(self.angle) * 32))
            if curr_w < 1: curr_w = 1  # Чтобы не было ошибок с нулевой шириной

            # Масштабируем картинку по горизонтали
            rot_img = pygame.transform.scale(self.original_img, (curr_w, 32))

            # Центрируем суженную монетку, чтобы она не "прыгала" влево
            draw_x = self.x + (32 - curr_w) // 2
            draw_y = self.y + self.float_offset + offset_y

            screen.blit(rot_img, (draw_x, draw_y))
