import pygame

class Button:
    def __init__(self, image_path, center_pos, size, hitbox_padding=(50,50,50,50)):



        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, size)
        self.rect = self.image.get_rect(center=center_pos)

        # Создаём хитбокс с отступами
        top, right, bottom, left = hitbox_padding
        self.hitbox = pygame.Rect(
            self.rect.left + left,
            self.rect.top + top,
            self.rect.width - left - right,
            self.rect.height - top - bottom
        )

    def draw(self, screen):
        screen.blit(self.image, self.rect)

        # Для дебага: показать хитбокс
        # pygame.draw.rect(screen, (255,0,0), self.hitbox, 2)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hitbox.collidepoint(event.pos):
                return True
        return False
