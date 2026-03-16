import pygame
import os
import json
import math
from buttons import Button

BASE = os.path.dirname(__file__)

DESIGN_W, DESIGN_H = 400, 800

LAYOUT_FILE = os.path.join(BASE, "layout.json")
SHOP_LAYOUT_FILE = os.path.join(BASE, "shop_layout.json")


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
        self.play_button = Button(
            "contents/buttons/PLAY.png",
            (cx, cy - 80),
            (300, 150),
            hitbox_padding=(10, 10, 10, 10),
        )
        self.settings_button = Button(
            "contents/buttons/SETTING.png",
            (cx, cy + 50),
            (220, 110),
            hitbox_padding=(8, 8, 8, 8),
        )
        self.exit_button = Button(
            "contents/buttons/EXIT.png",
            (DESIGN_W - 60, 60),
            (120, 60),
            hitbox_padding=(6, 6, 6, 6),
        )
        self.shop_button = Button(
            "contents/buttons/SHOP.png",
            (cx + 140, cy + 50),
            (160, 80),
            hitbox_padding=(6, 6, 6, 6),
        )
        self.debug_button = Button(
            "contents/buttons/debug.png",
            (40, 40),
            (70, 70),
            hitbox_padding=(0, 0, 0, 0),
        )

        # --- КНОПКА ВЫХОДА ИЗ НАСТРОЕК ---
        self.settings_exit_button = Button(
            "contents/buttons/exit.png",
            (DESIGN_W - 70, 70),
            (140, 140),
            hitbox_padding=(0, 0, 0, 0),
        )

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
            self.level_buttons.append({"btn": btn, "num": i, "active": i <= 3})

        # флаги
        self.play_hovered = False
        self.settings_hovered = False
        self.exit_hovered = False
        self.shop_hovered = False
        self.settings_exit_hovered = False
        self.show_hitboxes = False
        self.hover_scale = 1.10
        self.start_game = False

        # =========================
        # МАГАЗИН
        # =========================
        self.shop_open = False
        self.inventory_open = False
        self.selected_character = None

        # Размеры панели магазина - ДЕФОЛТНЫЕ
        self.shop_w = int(DESIGN_W * 0.92)
        self.shop_h = int(DESIGN_H * 0.78)
        self.shop_x = (DESIGN_W - self.shop_w) // 2
        self.shop_y = (DESIGN_H - self.shop_h) // 2

        self._shop_panel_rect = pygame.Rect(self.shop_x, self.shop_y, self.shop_w, self.shop_h)

        # фон магазина
        self._shop_bg_raw = None
        try:
            self._shop_bg_raw = pygame.image.load(_full("contents/backgroundsF/shopFon.png")).convert_alpha()
        except Exception:
            self._shop_bg_raw = None
        self.shop_bg = self._make_shop_bg(self._shop_panel_rect.size)

        # Кнопка закрытия
        self.close_button = Button(
            "contents/buttons/exit.png",
            (self._shop_panel_rect.right - 40, self._shop_panel_rect.top + 40),
            (120, 120),
            hitbox_padding=(0, 0, 0, 0),
        )

        # Табы
        self._tab_gap = 10
        tab_width, tab_height = 200, 110

        self.shop_tab_button = Button(
            "contents/buttons/shopBut.png",
            (DESIGN_W // 2 - 60, DESIGN_H // 2 - 80),
            (tab_width, tab_height),
        )
        self.inventory_tab_button = Button(
            "contents/buttons/invBut.png",
            (DESIGN_W // 2 + 60, DESIGN_H // 2 - 80),
            (tab_width, tab_height),
        )

        # Персонажи
        self.character_paths = [
            "contents/characters/player1.png",
            "contents/characters/svinL.png",
            "contents/characters/horseL.png",
        ]
        self.character_buttons = []
        self._char_gap = 18
        self._char_size = 120
        for path in self.character_paths:
            btn = Button(path, (0, 0), (self._char_size, self._char_size))
            self.character_buttons.append(btn)

        # Навигация стрелками
        self._selected_char_index = 0
        self.arrow_left = Button("contents/buttons/debug.png", (0, 0), (50, 50))
        self.arrow_right = Button("contents/buttons/debug.png", (0, 0), (50, 50))
        self._arrow_left_hovered = False
        self._arrow_right_hovered = False
        self._arrow_hover_scale = 1.15

        # =========================
        # НАСТРОЙКИ / ГРОМКОСТЬ
        # =========================
        self.music_volume = 1.0
        self.sfx_volume = 1.0

        self._slider_track_x = DESIGN_W // 2 - 100
        self._slider_track_w = 200
        self._music_slider_y = DESIGN_H // 2 + 40
        self._sfx_slider_y = DESIGN_H // 2 + 100
        self._dragging_slider = None
        self.settings_open = False

        self._slider_track_h = 18
        self._slider_handle_r = 14
        self._slider_handle_hit_r = 22

        # Hover states
        self._shop_hover_close = False
        self._shop_hover_shop_tab = False
        self._shop_hover_inv_tab = False
        self._shop_hover_char_index = -1
        self._tab_hover_scale = 1.06
        self._close_hover_scale = 1.10
        self._char_hover_scale = 1.06
        self._settings_exit_hover_scale = 1.10

        # === ЗАГРУЖАЕМ LAYOUT МАГАЗИНА ===
        self._load_shop_layout()

        # Загружаем layout главного меню
        self.load_layout_if_exists()

    def _load_shop_layout(self):
        if not os.path.exists(SHOP_LAYOUT_FILE):
            return

        try:
            with open(SHOP_LAYOUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if 'shop_panel' in data:
                panel = data['shop_panel']
                self._shop_panel_rect.x = panel.get('x', self._shop_panel_rect.x)
                self._shop_panel_rect.y = panel.get('y', self._shop_panel_rect.y)
                self._shop_panel_rect.width = max(50, panel.get('width', self._shop_panel_rect.width))
                self._shop_panel_rect.height = max(50, panel.get('height', self._shop_panel_rect.height))

                self.shop_bg = self._make_shop_bg(self._shop_panel_rect.size)

                self.shop_x = self._shop_panel_rect.x
                self.shop_y = self._shop_panel_rect.y
                self.shop_w = self._shop_panel_rect.width
                self.shop_h = self._shop_panel_rect.height

            for key, item in data.items():
                if key == 'shop_panel':
                    continue

                target = None
                if key == "close_button":
                    target = self.close_button
                elif key == "shop_tab":
                    target = self.shop_tab_button
                elif key == "inventory_tab":
                    target = self.inventory_tab_button
                elif key == "arrow_left":
                    target = self.arrow_left
                elif key == "arrow_right":
                    target = self.arrow_right
                elif key.startswith("character_"):
                    idx = int(key.split("_")[1])
                    if idx < len(self.character_buttons):
                        target = self.character_buttons[idx]

                if target and item:
                    center = item.get('image_center')
                    size = item.get('image_size')
                    if center and size:
                        if hasattr(target, 'load_image'):
                            target.load_image((max(10, size[0]), max(10, size[1])))
                        target.rect.center = center

                    hitbox = item.get('hitbox_rect')
                    if hitbox and hasattr(target, 'hitbox_rect'):
                        target.hitbox_rect.x = hitbox[0]
                        target.hitbox_rect.y = hitbox[1]
                        target.hitbox_rect.width = max(5, hitbox[2])
                        target.hitbox_rect.height = max(5, hitbox[3])

            print(f"[Shop] Загружен layout: {len(data)} элементов")
        except Exception as e:
            print(f"[Shop] Ошибка загрузки: {e}")

    def _make_shop_bg(self, size):
        w, h = int(size[0]), int(size[1])
        if self._shop_bg_raw:
            try:
                return pygame.transform.smoothscale(self._shop_bg_raw, (w, h))
            except Exception:
                pass
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((35, 35, 35, 230))
        return surf

    def _shop_frame_rect(self):
        p = self._shop_panel_rect
        left = p.x + int(p.w * 0.18)
        top = p.y + int(p.h * 0.25)
        width = int(p.w * 0.64)
        height = int(p.h * 0.50)
        return pygame.Rect(left, top, width, height)

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
            ("LOGO", self.logo),
            ("KOZLIK", self.kozlik),
        ]
        for key, btn in mapping:
            if key in data:
                try:
                    new = Button.from_dict(data[key])
                    btn.image_path, btn.image, btn.rect, btn.hitbox_rect = (
                        new.image_path,
                        new.image,
                        new.rect,
                        new.hitbox_rect,
                    )
                except Exception:
                    pass

    def _update_main_hover_flags(self, pos):
        self.play_hovered = self.play_button.is_hitbox_hit(pos)
        self.settings_hovered = self.settings_button.is_hitbox_hit(pos)
        self.exit_hovered = self.exit_button.is_hitbox_hit(pos)
        self.shop_hovered = self.shop_button.is_hitbox_hit(pos)
        self.settings_exit_hovered = self.settings_exit_button.is_hitbox_hit(pos)

    def _update_shop_hover_flags(self, pos):
        self._shop_hover_close = self.close_button.is_hitbox_hit(pos)
        self._shop_hover_shop_tab = self.shop_tab_button.is_hitbox_hit(pos)
        self._shop_hover_inv_tab = self.inventory_tab_button.is_hitbox_hit(pos)
        self._shop_hover_char_index = -1

        if self.inventory_open:
            self._arrow_left_hovered = self.arrow_left.is_hitbox_hit(pos)
            self._arrow_right_hovered = self.arrow_right.is_hitbox_hit(pos)
        else:
            self._arrow_left_hovered = False
            self._arrow_right_hovered = False

    def _slider_handle_pos(self, volume, y):
        tx, tw = self._slider_track_x, self._slider_track_w
        return int(tx + volume * tw), int(y)

    def _is_over_slider(self, pos, y, volume):
        tx, tw = self._slider_track_x, self._slider_track_w
        track_rect = pygame.Rect(tx, int(y - self._slider_track_h // 2), tw, self._slider_track_h)
        if track_rect.collidepoint(pos):
            return True
        hx, hy = self._slider_handle_pos(volume, y)
        dx = pos[0] - hx
        dy = pos[1] - hy
        return (dx * dx + dy * dy) <= (self._slider_handle_hit_r * self._slider_handle_hit_r)

    def _set_slider_from_pos(self, mx):
        tx, tw = self._slider_track_x, self._slider_track_w
        return max(0.0, min(1.0, (mx - tx) / tw))

    def handle_event(self, event, mouse_pos_design=None):
        mx, my = mouse_pos_design if mouse_pos_design else pygame.mouse.get_pos()
        pos = (mx, my)

        self._update_main_hover_flags(pos)

        if self.shop_open or self.level_select_open:
            self._update_shop_hover_flags(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # --- LEVEL SELECT ---
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

            # --- SETTINGS ---
            if self.settings_open:
                if self.settings_exit_button.is_hitbox_hit(pos):
                    self.settings_open = False
                    return
                if self._is_over_slider(pos, self._music_slider_y, self.music_volume):
                    self.music_volume = self._set_slider_from_pos(mx)
                    self._dragging_slider = "music"
                    return
                if self._is_over_slider(pos, self._sfx_slider_y, self.sfx_volume):
                    self.sfx_volume = self._set_slider_from_pos(mx)
                    self._dragging_slider = "sfx"
                    return
                return

            # --- SHOP / INVENTORY ---
            if self.shop_open:
                if self.close_button.is_hitbox_hit(pos):
                    self.shop_open = False
                    self.inventory_open = False
                    return

                if self.shop_tab_button.is_hitbox_hit(pos):
                    self.inventory_open = False
                    return

                if self.inventory_tab_button.is_hitbox_hit(pos):
                    self.inventory_open = True
                    return

                if self.inventory_open:
                    if self.arrow_left.is_hitbox_hit(pos):
                        self._selected_char_index = (self._selected_char_index - 1) % len(self.character_buttons)
                        self.selected_character = self.character_buttons[self._selected_char_index].image_path
                        return

                    if self.arrow_right.is_hitbox_hit(pos):
                        self._selected_char_index = (self._selected_char_index + 1) % len(self.character_buttons)
                        self.selected_character = self.character_buttons[self._selected_char_index].image_path
                        return

                    for i, btn in enumerate(self.character_buttons):
                        if btn.is_hitbox_hit(pos):
                            self._selected_char_index = i
                            self.selected_character = btn.image_path
                            return

                return

            # --- MAIN MENU ---
            if self.play_button.is_hitbox_hit(pos):
                self.level_select_open = True
                return

            if self.settings_button.is_hitbox_hit(pos):
                self.settings_open = True
                return

            if self.exit_button.is_hitbox_hit(pos):
                pygame.quit()
                raise SystemExit()

            if self.shop_button.is_hitbox_hit(pos):
                self.shop_open = True
                self.inventory_open = False
                return

            if self.debug_button.is_hitbox_hit(pos):
                self.show_hitboxes = not self.show_hitboxes
                return

        if event.type == pygame.MOUSEMOTION and self._dragging_slider:
            rel = self._set_slider_from_pos(mx)
            if self._dragging_slider == "music":
                self.music_volume = rel
            elif self._dragging_slider == "sfx":
                self.sfx_volume = rel

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging_slider = None

    def _draw_scaled_button(self, surface, btn: Button, scale: float):
        img = pygame.transform.smoothscale(
            btn.image, (max(1, int(btn.rect.width * scale)), max(1, int(btn.rect.height * scale)))
        )
        surface.blit(img, img.get_rect(center=btn.rect.center))

    def _draw_dim_overlay(self, surface, alpha=170):
        overlay = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(alpha)))
        surface.blit(overlay, (0, 0))

    def draw(self, surface, debug=False):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((30, 30, 30))

        # --- MAIN MENU ---
        if not self.shop_open and not self.settings_open and not self.level_select_open:
            for btn, hovered in [
                (self.play_button, self.play_hovered),
                (self.settings_button, self.settings_hovered),
                (self.exit_button, self.exit_hovered),
                (self.shop_button, self.shop_hovered),
            ]:
                if hovered:
                    self._draw_scaled_button(surface, btn, self.hover_scale)
                else:
                    btn.draw(surface)

            self.logo.draw(surface)
            self.kozlik.draw(surface)
            self.debug_button.draw(surface)

        # --- LEVEL SELECT ---
        if self.level_select_open:
            self._draw_dim_overlay(surface, alpha=165)
            surface.blit(self.shop_bg, self._shop_panel_rect.topleft)

            if self._shop_hover_close:
                self._draw_scaled_button(surface, self.close_button, self._close_hover_scale)
            else:
                self.close_button.draw(surface)

            f = pygame.font.Font(None, 60)
            title = f.render("ВЫБОР УРОВНЯ", True, (255, 255, 255))
            shadow = f.render("ВЫБОР УРОВНЯ", True, (0, 0, 0))
            tx = self._shop_panel_rect.centerx - title.get_width() // 2
            ty = self._shop_panel_rect.y + 92
            surface.blit(shadow, (tx + 2, ty + 2))
            surface.blit(title, (tx, ty))

            for item in self.level_buttons:
                if not item["active"]:
                    item["btn"].image.set_alpha(80)
                else:
                    item["btn"].image.set_alpha(255)
                item["btn"].draw(surface)

                num_txt = f.render(
                    str(item["num"]),
                    True,
                    (255, 255, 255) if item["active"] else (80, 80, 80),
                )
                surface.blit(num_txt, num_txt.get_rect(center=item["btn"].rect.center))

        # --- SHOP / INVENTORY ---
        if self.shop_open:
            self._draw_dim_overlay(surface, alpha=175)
            surface.blit(self.shop_bg, self._shop_panel_rect.topleft)

            # close
            if self._shop_hover_close:
                self._draw_scaled_button(surface, self.close_button, self._close_hover_scale)
            else:
                self.close_button.draw(surface)

            # tabs
            if self._shop_hover_shop_tab:
                self._draw_scaled_button(surface, self.shop_tab_button, self._tab_hover_scale)
            else:
                self.shop_tab_button.draw(surface)

            if self._shop_hover_inv_tab:
                self._draw_scaled_button(surface, self.inventory_tab_button, self._tab_hover_scale)
            else:
                self.inventory_tab_button.draw(surface)

            # content
            if self.inventory_open:
                if self._arrow_left_hovered:
                    self._draw_scaled_button(surface, self.arrow_left, self._arrow_hover_scale)
                else:
                    self.arrow_left.draw(surface)

                if self._arrow_right_hovered:
                    self._draw_scaled_button(surface, self.arrow_right, self._arrow_hover_scale)
                else:
                    self.arrow_right.draw(surface)

                if self.character_buttons:
                    frame = self._shop_frame_rect()
                    selected_btn = self.character_buttons[self._selected_char_index]

                    char_rect = selected_btn.image.get_rect(center=(frame.centerx, frame.centery + 10))
                    surface.blit(selected_btn.image, char_rect)

                    pygame.draw.rect(surface, (255, 215, 0), char_rect, 2)

                    name_font = pygame.font.Font(None, 28)
                    filename = os.path.basename(selected_btn.image_path)
                    name = filename.replace('.png', '').replace('L', '').replace('player', 'Player ')
                    name_text = name_font.render(name, True, (255, 255, 255))
                    name_rect = name_text.get_rect(center=(frame.centerx, char_rect.bottom + 20))
                    surface.blit(name_text, name_rect)

                    page_font = pygame.font.Font(None, 22)
                    page_text = page_font.render(
                        f"{self._selected_char_index + 1} / {len(self.character_buttons)}",
                        True,
                        (200, 200, 200)
                    )
                    page_rect = page_text.get_rect(center=(frame.centerx, frame.bottom - 20))
                    surface.blit(page_text, page_rect)

        # --- SETTINGS ---
        if self.settings_open:
            overlay = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surface.blit(overlay, (0, 0))

            tx, tw = self._slider_track_x, self._slider_track_w
            my, sy = self._music_slider_y, self._sfx_slider_y

            pygame.draw.rect(surface, (90, 90, 90),
                             (tx, my - self._slider_track_h // 2, tw, self._slider_track_h), border_radius=10)
            pygame.draw.rect(surface, (90, 90, 90),
                             (tx, sy - self._slider_track_h // 2, tw, self._slider_track_h), border_radius=10)

            pygame.draw.rect(surface, (60, 140, 220),
                             (tx, my - self._slider_track_h // 2, int(self.music_volume * tw), self._slider_track_h),
                             border_radius=10)
            pygame.draw.rect(surface, (220, 160, 60),
                             (tx, sy - self._slider_track_h // 2, int(self.sfx_volume * tw), self._slider_track_h),
                             border_radius=10)

            hx, hy = self._slider_handle_pos(self.music_volume, my)
            sx, sy2 = self._slider_handle_pos(self.sfx_volume, sy)

            pygame.draw.circle(surface, (230, 230, 230), (hx, hy), self._slider_handle_r)
            pygame.draw.circle(surface, (230, 230, 230), (sx, sy2), self._slider_handle_r)

            if self.settings_exit_hovered:
                self._draw_scaled_button(surface, self.settings_exit_button, self._settings_exit_hover_scale)
            else:
                self.settings_exit_button.draw(surface)

        # Debug hitboxes
        if debug or self.show_hitboxes:
            debug_buttons = [
                self.play_button, self.settings_button, self.exit_button, self.shop_button,
                self.debug_button, self.logo, self.kozlik, self.close_button, self.settings_exit_button
            ]
            debug_buttons.extend(self.character_buttons)
            debug_buttons.extend([l["btn"] for l in self.level_buttons])
            if self.inventory_open:
                debug_buttons.extend([self.arrow_left, self.arrow_right])

            for b in debug_buttons:
                if hasattr(b, 'draw_hitbox'):
                    b.draw_hitbox(surface)