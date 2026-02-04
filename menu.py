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
        # background path
        self.bg_path = "contents/backgroundsF/menu.jpg"

        # --- ОПТИМИЗАЦИЯ: Загружаем фон один раз при инициализации ---
        bg_full = os.path.join(BASE, self.bg_path)
        try:
            raw_bg = pygame.image.load(bg_full).convert_alpha()
            # Сразу подгоняем под размер виртуального холста
            self.bg_image = pygame.transform.smoothscale(raw_bg, (DESIGN_W, DESIGN_H))
        except Exception:
            self.bg_image = None

        # create buttons with default positions (in design coords)
        cx, cy = DESIGN_W // 2, DESIGN_H // 2
        self.play_button = Button("contents/buttons/PLAY.png", (cx, cy - 80), (300, 150),
                                  hitbox_padding=(10, 10, 10, 10))
        self.settings_button = Button("contents/buttons/SETTING.png", (cx, cy + 50), (220, 110),
                                      hitbox_padding=(8, 8, 8, 8))
        self.exit_button = Button("contents/buttons/EXIT.png", (DESIGN_W - 60, 60), (120, 60),
                                  hitbox_padding=(6, 6, 6, 6))
        self.shop_button = Button("contents/buttons/SHOP.png", (cx + 140, cy + 50), (160, 80),
                                  hitbox_padding=(6, 6, 6, 6))
        self.debug_button = Button("contents/buttons/debug.png", (40, 40), (70, 70), hitbox_padding=(0, 0, 0, 0))

        # hover flags
        self.play_hovered = False
        self.settings_hovered = False
        self.exit_hovered = False
        self.shop_hovered = False

        self.show_hitboxes = False
        self.hover_scale = 1.1
        self.start_game = False

        # try loading layout if file exists
        self.load_layout_if_exists()

    # --- layout load/save ---
    def load_layout_if_exists(self, path=LAYOUT_FILE):
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        mapping = [("PLAY", self.play_button),
                   ("SETTING", self.settings_button),
                   ("EXIT", self.exit_button),
                   ("SHOP", self.shop_button),
                   ("DEBUG", self.debug_button)]
        for key, btn in mapping:
            if key in data:
                try:
                    new = Button.from_dict(data[key])
                    # apply to existing button (preserve object references)
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
            "DEBUG": self.debug_button.to_dict()
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
            if self.play_button.is_hitbox_hit(pos):
                self.start_game = True
            elif self.settings_button.is_hitbox_hit(pos):
                print("Settings clicked")
            elif self.exit_button.is_hitbox_hit(pos):
                pygame.quit();
                raise SystemExit()
            elif self.shop_button.is_hitbox_hit(pos):
                print("Shop clicked")
            elif self.debug_button.is_hitbox_hit(pos):
                self.show_hitboxes = not self.show_hitboxes

        if event.type == pygame.QUIT:
            pygame.quit();
            raise SystemExit()

    # --- drawing: draw onto a surface in design coords ---
    def draw(self, surface, debug=False):
        # --- ИСПРАВЛЕНО: Рисуем заранее загруженный фон ---
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((30, 30, 30))

        # Отображение кнопок с масштабированием при наведении курсора
        for btn, hovered in [(self.play_button, self.play_hovered),
                             (self.settings_button, self.settings_hovered),
                             (self.exit_button, self.exit_hovered),
                             (self.shop_button, self.shop_hovered)]:
            if hovered:
                # Использует быстрый scale
                img = pygame.transform.scale(btn.image, (int(btn.rect.width * self.hover_scale),
                                                         int(btn.rect.height * self.hover_scale)))
                rect = img.get_rect(center=btn.rect.center)
                surface.blit(img, rect)
            else:
                btn.draw(surface)

        # debug кнопка
        self.debug_button.draw(surface)

        if debug or self.show_hitboxes:
            for b in [self.play_button, self.settings_button, self.exit_button, self.shop_button, self.debug_button]:
                b.draw_hitbox(surface)
