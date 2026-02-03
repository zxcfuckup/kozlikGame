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

        # ---- РАЗМЕРЫ ----
        play_size = (500, 300)
        settings_size = (500, 250)
        exit_size = (500, 250)

        center_x = w // 2
        center_y = h // 2

        # ---- PLAY ----
        self.play_button = Button(
            "contents/buttons/PLAY.png",
            (center_x, center_y - 40),
            play_size,
            hitbox_padding=(60, 243, 165, 70)
        )

        # ---- SETTINGS ----
        self.settings_button = Button(
            "contents/buttons/SETTING.png",
            (center_x, center_y + 30),
            settings_size,
            hitbox_padding=(125, 235, 93, 165)
        )

        # ---- EXIT ----
        self.exit_button = Button(
            "contents/buttons/EXIT.png",
            (w - exit_size[0] // 2 - 15, exit_size[1] // 2 + 15),
            exit_size,
            hitbox_padding=(20, 65, 170, 365)
        )

        # ---- DEBUG BUTTON ----
        self.debug_button = Button(
            "contents/buttons/debug.png",
            (40, 40),
            (70, 70),
            hitbox_padding=(0, 0, 0, 0)
        )

        self.show_hitboxes = False

        # hover
        self.hover_scale = 1.1

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()

        self.play_hovered = self.play_button.hitbox.collidepoint((mx, my))
        self.settings_hovered = self.settings_button.hitbox.collidepoint((mx, my))
        self.exit_hovered = self.exit_button.hitbox.collidepoint((mx, my))

        for event in events:
            if self.play_button.is_clicked(event):
                self.start_game = True

            if self.settings_button.is_clicked(event):
                print("Settings clicked")

            if self.exit_button.is_clicked(event):
                pygame.quit()
                exit()

            if self.debug_button.is_clicked(event):
                self.show_hitboxes = not self.show_hitboxes

            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

    def draw(self):
        self.screen.blit(self.bg, (0, 0))

        self.draw_button(self.play_button, self.play_hovered)
        self.draw_button(self.settings_button, self.settings_hovered)
        self.draw_button(self.exit_button, self.exit_hovered)

        self.debug_button.draw(self.screen)

        # ---- DEBUG HITBOXES ----
        if self.show_hitboxes:
            self.play_button.draw_hitbox(self.screen)
            self.settings_button.draw_hitbox(self.screen)
            self.exit_button.draw_hitbox(self.screen)
            self.debug_button.draw_hitbox(self.screen)

            font = pygame.font.Font(None, 20)
            txt = font.render("# HITBOX MODE", True, (255, 0, 0))
            self.screen.blit(txt, (10, 85))

    def draw_button(self, button, hovered):
        if hovered:
            img = pygame.transform.smoothscale(
                button.image,
                (int(button.rect.width * self.hover_scale),
                 int(button.rect.height * self.hover_scale))
            )
            rect = img.get_rect(center=button.rect.center)
            self.screen.blit(img, rect)
        else:
            button.draw(self.screen)
