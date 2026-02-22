# menu.py
import pygame
import os
import json
from buttons import Button

BASE = os.path.dirname(__file__)
DESIGN_W, DESIGN_H = 400, 800
LAYOUT_FILE = os.path.join(BASE, "layout.json")


def _full(p):
    return os.path.join(BASE, p)


class Menu:
    def __init__(self):
        # фоновый путь
        self.bg_path = "contents/backgroundsF/menu.jpg"

        # Загружает фон один раз при инициализации
        bg_full = os.path.join(BASE, self.bg_path)
        try:
            raw_bg = pygame.image.load(bg_full).convert_alpha()
            self.bg_image = pygame.transform.smoothscale(raw_bg, (DESIGN_W, DESIGN_H))
        except Exception:
            self.bg_image = None

        # центральные координаты
        cx, cy = DESIGN_W // 2, DESIGN_H // 2

        # кнопки главного меню
        self.play_button = Button("contents/buttons/PLAY.png", (cx, cy - 80), (300, 150),
                                  hitbox_padding=(10, 10, 10, 10))
        self.settings_button = Button("contents/buttons/SETTING.png", (cx, cy + 50), (220, 110),
                                      hitbox_padding=(8, 8, 8, 8))
        self.exit_button = Button("contents/buttons/EXIT.png", (DESIGN_W - 60, 60), (120, 60),
                                  hitbox_padding=(6, 6, 6, 6))
        self.shop_button = Button("contents/buttons/SHOP.png", (cx + 140, cy + 50), (160, 80),
                                  hitbox_padding=(6, 6, 6, 6))
        self.debug_button = Button("contents/buttons/debug.png", (40, 40), (70, 70), hitbox_padding=(0, 0, 0, 0))

        # --- КНОПКА ВЫХОДА ИЗ НАСТРОЕК ---
        self.settings_exit_button = Button("contents/buttons/exit.png", (DESIGN_W - 70, 70), (120, 120),
                                           hitbox_padding=(5, 5, 5, 5))

        # новые кнопки
        self.logo = Button("contents/buttons/logo.png", (50, 50), (80, 80))
        self.kozlik = Button("contents/buttons/KOZLIKt.png", (DESIGN_W // 2, DESIGN_H - 120), (120, 120))

        # =========================
        # СИСТЕМА УРОВНЕЙ (LEVEL SELECT)
        # =========================
        self.level_select_open = False
        self.selected_level = 1
        self.level_buttons = []

        tile_size = 80
        spacing = 100
        start_x = DESIGN_W // 2 - spacing
        start_y = DESIGN_H // 2 - 100

        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            bx = start_x + col * spacing
            by = start_y + row * spacing
            btn = Button("contents/buttons/debug.png", (bx, by), (tile_size, tile_size))
            # ТЕПЕРЬ 1 И 2 УРОВНИ АКТИВНЫ (i <= 2)
            self.level_buttons.append({"btn": btn, "num": i, "active": i <= 2})

        # флаги
        self.play_hovered = False
        self.settings_hovered = False
        self.exit_hovered = False
        self.shop_hovered = False
        self.settings_exit_hovered = False

        self.show_hitboxes = False
        self.hover_scale = 1.1
        self.start_game = False

        # =========================
        # МАГАЗИН
        # =========================
        self.shop_open = False
        self.inventory_open = False
        self.selected_character = None

        self.shop_w = int(DESIGN_W * 1.2)
        self.shop_h = int(DESIGN_H * 1.9)
        self.shop_x = (DESIGN_W - self.shop_w) // 2
        self.shop_y = (DESIGN_H - self.shop_h) // 2

        try:
            self.shop_bg = pygame.image.load("contents/backgroundsF/shopFon.png").convert_alpha()
            self.shop_bg = pygame.transform.smoothscale(self.shop_bg, (self.shop_w, self.shop_h))
        except Exception:
            self.shop_bg = pygame.Surface((self.shop_w, self.shop_h))
            self.shop_bg.fill((50, 50, 50))

        self.close_button = Button("contents/buttons/exit.png", (DESIGN_W - 70, 70), (100, 100))

        tab_width, tab_height = 220, 120
        center_x = DESIGN_W // 2
        center_y = DESIGN_H // 2 - 80
        offset = 110

        self.shop_tab_button = Button("contents/buttons/shopBut.png", (center_x - offset, center_y),
                                      (tab_width, tab_height))
        self.inventory_tab_button = Button("contents/buttons/invBut.png", (center_x + offset, center_y),
                                           (tab_width, tab_height))

        # ПЕРСОНАЖИ
        self.character_paths = ["contents/characters/player1.png", "contents/characters/svinL.png",
                                "contents/characters/horseL.png"]
        self.character_buttons = []
        char_size = 120
        spacing_char = 150
        start_x_char = DESIGN_W // 2 - spacing_char
        y_pos_char = DESIGN_H // 2 + 120
        for i, path in enumerate(self.character_paths):
            btn = Button(path, (start_x_char + i * spacing_char, y_pos_char), (char_size, char_size))
            self.character_buttons.append(btn)

        # ГРОМКОСТЬ
        self.music_volume = 1.0
        self.sfx_volume = 1.0
        self._slider_track_x = DESIGN_W // 2 - 100
        self._slider_track_w = 200
        self._music_slider_y = DESIGN_H // 2 + 40
        self._sfx_slider_y = DESIGN_H // 2 + 100
        self._dragging_slider = None
        self.settings_open = False
        self.load_layout_if_exists()

    def load_layout_if_exists(self, path=LAYOUT_FILE):
        if not os.path.exists(path): return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        mapping = [("PLAY", self.play_button), ("SETTING", self.settings_button), ("EXIT", self.exit_button),
                   ("SHOP", self.shop_button), ("DEBUG", self.debug_button), ("LOGO", self.logo),
                   ("KOZLIK", self.kozlik)]
        for key, btn in mapping:
            if key in data:
                try:
                    new = Button.from_dict(data[key])
                    btn.image_path, btn.image, btn.rect, btn.hitbox_rect = new.image_path, new.image, new.rect, new.hitbox_rect
                except Exception:
                    pass

    def handle_event(self, event, mouse_pos_design=None):
        mx, my = mouse_pos_design if mouse_pos_design else pygame.mouse.get_pos()
        pos = (mx, my)
        self.play_hovered = self.play_button.is_hitbox_hit(pos)
        self.settings_hovered = self.settings_button.is_hitbox_hit(pos)
        self.exit_hovered = self.exit_button.is_hitbox_hit(pos)
        self.shop_hovered = self.shop_button.is_hitbox_hit(pos)
        self.settings_exit_hovered = self.settings_exit_button.is_hitbox_hit(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.level_select_open:
                if self.close_button.is_hitbox_hit(pos):
                    self.level_select_open = False
                    return
                for item in self.level_buttons:
                    if item["active"] and item["btn"].is_hitbox_hit(pos):
                        self.selected_level = item["num"]
                        self.start_game = True
                        self.level_select_open = False
                        return
                return
            if self.settings_open:
                if self.settings_exit_button.is_hitbox_hit(pos): self.settings_open = False; return
                tx, tw = self._slider_track_x, self._slider_track_w
                if pygame.Rect(tx, self._music_slider_y - 8, tw, 16).collidepoint(pos):
                    self.music_volume = max(0.0, min(1.0, (pos[0] - tx) / tw));
                    self._dragging_slider = "music"
                elif pygame.Rect(tx, self._sfx_slider_y - 8, tw, 16).collidepoint(pos):
                    self.sfx_volume = max(0.0, min(1.0, (pos[0] - tx) / tw));
                    self._dragging_slider = "sfx"
                return
            if self.shop_open:
                if self.close_button.is_hitbox_hit(pos): self.shop_open = False; self.inventory_open = False; return
                if self.inventory_open:
                    for btn in self.character_buttons:
                        if btn.is_hitbox_hit(pos): self.selected_character = btn.image_path
                    return
                if self.shop_tab_button.is_hitbox_hit(pos): self.inventory_open = False
                if self.inventory_tab_button.is_hitbox_hit(pos): self.inventory_open = True
                return
            if self.play_button.is_hitbox_hit(pos):
                self.level_select_open = True
            elif self.settings_button.is_hitbox_hit(pos):
                self.settings_open = True
            elif self.exit_button.is_hitbox_hit(pos):
                pygame.quit(); raise SystemExit()
            elif self.shop_button.is_hitbox_hit(pos):
                self.shop_open = True
            elif self.debug_button.is_hitbox_hit(pos):
                self.show_hitboxes = not self.show_hitboxes
        elif event.type == pygame.MOUSEMOTION and self._dragging_slider:
            tx, tw = self._slider_track_x, self._slider_track_w
            rel = max(0.0, min(1.0, (mx - tx) / tw))
            if self._dragging_slider == "music":
                self.music_volume = rel
            elif self._dragging_slider == "sfx":
                self.sfx_volume = rel
        elif event.type == pygame.MOUSEBUTTONUP:
            self._dragging_slider = None

    def draw(self, surface, debug=False):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((30, 30, 30))

        if not self.shop_open and not self.settings_open and not self.level_select_open:
            for btn, hovered in [(self.play_button, self.play_hovered), (self.settings_button, self.settings_hovered),
                                 (self.exit_button, self.exit_hovered), (self.shop_button, self.shop_hovered)]:
                if hovered:
                    img = pygame.transform.scale(btn.image, (int(btn.rect.width * self.hover_scale),
                                                             int(btn.rect.height * self.hover_scale)))
                    surface.blit(img, img.get_rect(center=btn.rect.center))
                else:
                    btn.draw(surface)
            self.logo.draw(surface);
            self.kozlik.draw(surface);
            self.debug_button.draw(surface)

        if self.level_select_open:
            surface.blit(self.shop_bg, (self.shop_x, self.shop_y))
            self.close_button.draw(surface)
            f = pygame.font.Font(None, 60)
            shadow = f.render("ВЫБОР УРОВНЯ", True, (0, 0, 0))
            surface.blit(shadow, (DESIGN_W // 2 - 148, 152))
            title = f.render("ВЫБОР УРОВНЯ", True, (255, 255, 255))
            surface.blit(title, (DESIGN_W // 2 - 150, 150))

            for item in self.level_buttons:
                if not item["active"]:
                    item["btn"].image.set_alpha(80)
                else:
                    item["btn"].image.set_alpha(255)
                item["btn"].draw(surface)
                num_txt = f.render(str(item["num"]), True, (255, 255, 255) if item["active"] else (80, 80, 80))
                surface.blit(num_txt, num_txt.get_rect(center=item["btn"].rect.center))

        if self.shop_open:
            surface.blit(self.shop_bg, (self.shop_x, self.shop_y));
            self.close_button.draw(surface);
            self.shop_tab_button.draw(surface);
            self.inventory_tab_button.draw(surface)
            if self.inventory_open:
                for btn in self.character_buttons:
                    btn.draw(surface)
                    if btn.image_path == self.selected_character: pygame.draw.rect(surface, (255, 215, 0), btn.rect, 4)

        if self.settings_open:
            overlay = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA);
            overlay.fill((0, 0, 0, 160));
            surface.blit(overlay, (0, 0))
            tx, tw = self._slider_track_x, self._slider_track_w
            my, sy = self._music_slider_y, self._sfx_slider_y
            pygame.draw.rect(surface, (90, 90, 90), (tx, my - 6, tw, 12), border_radius=6)
            pygame.draw.rect(surface, (90, 90, 90), (tx, sy - 6, tw, 12), border_radius=6)
            pygame.draw.rect(surface, (60, 140, 220), (tx, my - 6, int(self.music_volume * tw), 12), border_radius=6)
            pygame.draw.rect(surface, (220, 160, 60), (tx, sy - 6, int(self.sfx_volume * tw), 12), border_radius=6)
            pygame.draw.circle(surface, (230, 230, 230), (int(tx + self.music_volume * tw), my), 12)
            pygame.draw.circle(surface, (230, 230, 230), (int(tx + self.sfx_volume * tw), sy), 12)
            self.settings_exit_button.draw(surface)

        if debug or self.show_hitboxes:
            for b in [self.play_button, self.settings_button, self.exit_button, self.shop_button, self.debug_button,
                      self.logo, self.kozlik, self.close_button, self.settings_exit_button] + self.character_buttons + [
                         l["btn"] for l in self.level_buttons]:
                b.draw_hitbox(surface)
