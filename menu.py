# menu.py
import pygame
import os
import json
from buttons import Button

BASE = os.path.dirname(__file__)
DESIGN_W, DESIGN_H = 400, 800
LAYOUT_FILE = os.path.join(BASE, "layout.json")


def _full(p): return os.path.join(BASE, p)


class Menu:
    def __init__(self):
        # фоновый путь
        self.bg_path = "contents/backgroundsF/menu.jpg"

        #  Загружает фон один раз при инициализации
        bg_full = os.path.join(BASE, self.bg_path)
        try:
            raw_bg = pygame.image.load(bg_full).convert_alpha()
            # Сразу подгоняем под размер виртуального холста
            self.bg_image = pygame.transform.smoothscale(raw_bg, (DESIGN_W, DESIGN_H))
        except Exception:
            self.bg_image = None

        # создание кнопки с расположением по умолчанию
        cx, cy = DESIGN_W // 2, DESIGN_H // 2
        self.play_button = Button("contents/buttons/PLAY.png", (cx, cy - 80), (300, 150),
                                  hitbox_padding=(10, 10, 10, 10))
        self.settings_button = Button("contents/buttons/SETTING.png", (cx, cy + 50), (220, 110),
                                      hitbox_padding=(8, 8, 8, 8))
        self.exit_button = Button("contents/buttons/EXIT.png", (DESIGN_W - 60, 60), (120, 60),
                                  hitbox_padding=(6, 6, 6, 6))
        self.shop_button = Button("contents/buttons/SHOP.png", (cx + 140, cy + 50), (160, 80),
                                  hitbox_padding=(6, 6, 6, 6))
        self.debug_button = Button("contents/buttons/debug.png", (40, 40), (70, 70),
                                   hitbox_padding=(0, 0, 0, 0))

        # новые кнопки
        self.logo = Button("contents/buttons/logo.png", (50, 50), (80, 80))
        self.kozlik = Button("contents/buttons/KOZLIKt.png", (DESIGN_W // 2, DESIGN_H - 120), (120, 120))

        # флаги
        self.play_hovered = False
        self.settings_hovered = False
        self.exit_hovered = False
        self.shop_hovered = False

        self.show_hitboxes = False
        self.hover_scale = 1.1
        self.start_game = False

        #  магазин
        self.shop_open = False
        self.shop_w = int(DESIGN_W * 1.2)  #  ширина магазина
        self.shop_h = int(DESIGN_H * 1.9)  #  высота магазина
        self.shop_x = (DESIGN_W - self.shop_w) // 2
        self.shop_y = (DESIGN_H - self.shop_h) // 2
        try:
            self.shop_bg = pygame.image.load("contents/backgroundsF/shopFon.png").convert_alpha()
            self.shop_bg = pygame.transform.smoothscale(self.shop_bg, (self.shop_w, self.shop_h))
        except Exception:
            self.shop_bg = pygame.Surface((self.shop_w, self.shop_h))
            self.shop_bg.fill((50, 50, 50))

        # крестик для закрытия магазина
        cross_size = 200
        padding = 10
        self.close_button = Button("contents/buttons/exit.png",
                                   (DESIGN_W - padding - cross_size // 2, padding + cross_size // 2),
                                   (cross_size, cross_size))

        # кнопки внутри магазина (shop / inventory)
        tab_width, tab_height = 180, 100  # увеличенные размеры кнопок
        # размещаем их по горизонтали ниже верхней границы окна
        self.shop_tab_button = Button("contents/buttons/shopBut.png",
                                      (self.shop_x + self.shop_w // 2 - 120, self.shop_y + 200),
                                      (tab_width, tab_height))
        self.inventory_tab_button = Button("contents/buttons/invBut.png",
                                           (self.shop_x + self.shop_w // 2 + 120, self.shop_y + 200),
                                           (tab_width, tab_height))

        # try loading layout if file exists
        self.load_layout_if_exists()


    def load_layout_if_exists(self, path=LAYOUT_FILE):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return

        mapping = [
            ("PLAY", self.play_button),
            ("SETTING", self.settings_button),
            ("EXIT", self.exit_button),
            ("SHOP", self.shop_button),
            ("DEBUG", self.debug_button),
            ("LOGO", self.logo),  # добавлено
            ("KOZLIK", self.kozlik)  # добавлено
        ]
        for key, btn in mapping:
            if key in data:
                try:
                    new = Button.from_dict(data[key])

                    btn.image_path = new.image_path
                    btn.image = new.image
                    btn.rect = new.rect
                    btn.hitbox_rect = new.hitbox_rect
                except Exception:
                    pass

    def save_layout(self, path=LAYOUT_FILE):
        data = {
            "PLAY": self.play_button.to_dict(),
            "SETTING": self.settings_button.to_dict(),
            "EXIT": self.exit_button.to_dict(),
            "SHOP": self.shop_button.to_dict(),
            "DEBUG": self.debug_button.to_dict(),
            "LOGO": self.logo.to_dict(),  # добавлено
            "KOZLIK": self.kozlik.to_dict()  # добавлено
        }
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    # --- events (mouse_pos_design in design coords) ---
    def handle_event(self, event, mouse_pos_design=None):
        if mouse_pos_design is not None:
            mx, my = mouse_pos_design
        else:
            mx, my = pygame.mouse.get_pos()

        # update hover flags using hitboxes
        self.play_hovered = self.play_button.is_hitbox_hit((mx, my))
        self.settings_hovered = self.settings_button.is_hitbox_hit((mx, my))
        self.exit_hovered = self.exit_button.is_hitbox_hit((mx, my))
        self.shop_hovered = self.shop_button.is_hitbox_hit((mx, my))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = (mx, my)

            if self.shop_open:
                # только крестик и внутренние кнопки активны
                if self.close_button.is_hitbox_hit(pos):
                    self.shop_open = False
                    return  # остальные кнопки не обрабатываем
                if self.shop_tab_button.is_hitbox_hit(pos):
                    print("Shop tab clicked")
                if self.inventory_tab_button.is_hitbox_hit(pos):
                    print("Inventory tab clicked")
                return  # остальные кнопки меню не активны

            # обычная обработка меню
            if self.play_button.is_hitbox_hit(pos):
                self.start_game = True
            elif self.settings_button.is_hitbox_hit(pos):
                print("Settings clicked")
            elif self.exit_button.is_hitbox_hit(pos):
                pygame.quit(); raise SystemExit()
            elif self.shop_button.is_hitbox_hit(pos):
                self.shop_open = True
            elif self.debug_button.is_hitbox_hit(pos):
                self.show_hitboxes = not self.show_hitboxes

        if event.type == pygame.QUIT:
            pygame.quit(); raise SystemExit()

    #  рисует  на поверхности в соответствии с координатами.
    def draw(self, surface, debug=False):
        #  Рисует заранее загруженный фон
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((30, 30, 30))

        # Отображение кнопок с масштабированием при наведении курсора
        for btn, hovered in [
            (self.play_button, self.play_hovered),
            (self.settings_button, self.settings_hovered),
            (self.exit_button, self.exit_hovered),
            (self.shop_button, self.shop_hovered)
        ]:
            if self.shop_open:
                continue  # не отображаем интерактивность остальных кнопок, пока магазин открыт
            if hovered:
                img = pygame.transform.scale(btn.image, (int(btn.rect.width * self.hover_scale),
                                                         int(btn.rect.height * self.hover_scale)))
                rect = img.get_rect(center=btn.rect.center)
                surface.blit(img, rect)
            else:
                btn.draw(surface)

        # новые кнопки (logo и kozlik)
        self.logo.draw(surface)
        self.kozlik.draw(surface)

        # debug кнопка
        self.debug_button.draw(surface)

        # магазин
        if self.shop_open:
            surface.blit(self.shop_bg, (self.shop_x, self.shop_y))
            self.close_button.draw(surface)  # крестик в правом верхнем углу
            # внутренние кнопки магазина
            self.shop_tab_button.draw(surface)
            self.inventory_tab_button.draw(surface)

        if debug or self.show_hitboxes:
            for b in [self.play_button, self.settings_button, self.exit_button, self.shop_button,
                      self.debug_button, self.logo, self.kozlik, self.close_button,
                      self.shop_tab_button, self.inventory_tab_button]:
                b.draw_hitbox(surface)