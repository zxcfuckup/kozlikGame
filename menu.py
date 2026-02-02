import pygame
from buttons import Button

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.start_game = False

        w = self.screen.get_width()
        h = self.screen.get_height()

        # Фон меню
        self.bg = pygame.image.load("contents/backgroundsF/menu.jpg").convert_alpha()
        self.bg = pygame.transform.smoothscale(self.bg, (w, h))

        # ---- РАЗМЕРЫ КНОПОК ----
        play_size = (500, 300)
        small_size = (300, 150)
        exit_size = (500, 250)
        hover_scale = 1.1  # коэффициент увеличения при наведении
        padding = 15

        center_x = w // 2
        center_y = h // 2

        # PLAY (большая по центру)
        self.play_button = Button(
            image_path="contents/buttons/PLAY.png",
            center_pos=(center_x, center_y - 40),
            size=play_size,
            hitbox_padding=(60,200,165,45)
        )
        self.play_hovered = False

        # SETTING (меньше, под PLAY)
        self.settings_button = Button(
            image_path="contents/buttons/SETTING.png",
            center_pos=(center_x - 100, center_y + 60),
            size=(500, 250),
            hitbox_padding=(45,90,160,25)
        )
        self.settings_hovered = False

        # EXIT (правый верхний угол)
        self.exit_button = Button(
            image_path="contents/buttons/EXIT.png",
            center_pos=(
                w - exit_size[0] // 2 - padding,
                exit_size[1] // 2 + padding
            ),
            size=exit_size,
            hitbox_padding=(30,50,40,20)
        )
        self.exit_hovered = False

        # коэффициент увеличения при наведении
        self.hover_scale = hover_scale

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()

        # Проверка наведения мыши
        self.play_hovered = self.play_button.hitbox.collidepoint((mx, my))
        self.settings_hovered = self.settings_button.hitbox.collidepoint((mx, my))
        self.exit_hovered = self.exit_button.hitbox.collidepoint((mx, my))

        for event in events:
            if self.play_button.is_clicked(event):
                self.start_game = True

            if self.settings_button.is_clicked(event):
                print("Settings button clicked!")  # сюда потом можно добавить настройки

            if self.exit_button.is_clicked(event):
                pygame.quit()
                exit()

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        # Рисуем кнопки с hover-анимацией
        self.draw_button(self.play_button, self.play_hovered)
        self.draw_button(self.settings_button, self.settings_hovered)
        self.draw_button(self.exit_button, self.exit_hovered)

    def draw_button(self, button, hovered):
        if hovered:
            # увеличивает кнопку при наведении
            scaled_img = pygame.transform.smoothscale(
                button.image,
                (int(button.rect.width * self.hover_scale),
                 int(button.rect.height * self.hover_scale))

            )
            scaled_rect = scaled_img.get_rect(center=button.rect.center)
            self.screen.blit(scaled_img, scaled_rect)
        else:
            self.screen.blit(button.image, button.rect)
