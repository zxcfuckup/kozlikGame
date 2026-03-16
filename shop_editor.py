#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pygame
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

try:
    from menu import Menu, DESIGN_W, DESIGN_H
    from buttons import Button
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

SHOP_LAYOUT_FILE = "shop_layout.json"


class DragMode:
    IMAGE = 1
    HITBOX = 2


class ShopEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((DESIGN_W, DESIGN_H))
        pygame.display.set_caption("Shop Editor | 1:Image 2:Hitbox | LMB:drag | Arrows:resize | Ctrl+S:save")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 36)

        self.menu = Menu()
        self.menu.shop_open = True
        self.menu.inventory_open = False

        self.panel_rect = self.menu._shop_panel_rect.copy()

        self.buttons = []
        self._build_button_list()

        # Режим перетаскивания
        self.drag_mode = DragMode.IMAGE
        self.dragging = None  # (btn, mode, offset_x, offset_y)

        self.show_grid = True
        self.grid_size = 10

        self.load_layout()
        print(f"Загружено {len(self.buttons)} элементов")

    def _build_button_list(self):
        self.buttons = []

        self.buttons.append({
            'id': 'shop_panel',
            'name': 'Panel',
            'type': 'panel',
            'rect': self.panel_rect.copy(),
            'hitbox_rect': self.panel_rect.copy(),
            'obj': None
        })

        # Добавляем кнопки из меню
        items = [
            ('close_button', 'Close', getattr(self.menu, 'close_button', None)),
            ('shop_tab', 'Shop Tab', getattr(self.menu, 'shop_tab_button', None)),
            ('inventory_tab', 'Inv Tab', getattr(self.menu, 'inventory_tab_button', None)),
            ('arrow_left', 'Arrow L', getattr(self.menu, 'arrow_left', None)),
            ('arrow_right', 'Arrow R', getattr(self.menu, 'arrow_right', None)),
        ]

        for btn_id, name, obj in items:
            if obj and hasattr(obj, 'rect') and hasattr(obj, 'hitbox_rect'):
                self.buttons.append({
                    'id': btn_id,
                    'name': name,
                    'obj': obj,
                    'rect': obj.rect.copy(),
                    'hitbox_rect': obj.hitbox_rect.copy(),
                })

        if hasattr(self.menu, 'character_buttons'):
            for i, btn in enumerate(self.menu.character_buttons):
                if hasattr(btn, 'rect') and hasattr(btn, 'hitbox_rect'):
                    self.buttons.append({
                        'id': f'character_{i}',
                        'name': f'Char {i + 1}',
                        'obj': btn,
                        'rect': btn.rect.copy(),
                        'hitbox_rect': btn.hitbox_rect.copy(),
                    })

    def snap(self, value):
        if not self.show_grid:
            return value
        return round(value / self.grid_size) * self.grid_size

    def save_layout(self):
        """Сохраняет в формат JSON как у пользователя"""
        data = {"elements": []}

        for btn in self.buttons:
            element = {
                "id": btn['id'],
                "image": {
                    "x": btn['rect'].x,
                    "y": btn['rect'].y,
                    "width": btn['rect'].width,
                    "height": btn['rect'].height
                },
                "hitbox": {
                    "x": btn['hitbox_rect'].x,
                    "y": btn['hitbox_rect'].y,
                    "width": btn['hitbox_rect'].width,
                    "height": btn['hitbox_rect'].height
                }
            }
            data["elements"].append(element)

        try:
            with open(SHOP_LAYOUT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ Сохранено {len(data['elements'])} элементов в {SHOP_LAYOUT_FILE}")
        except Exception as e:
            print(f"✗ Ошибка сохранения: {e}")

    def load_layout(self):
        """Загружает из формата JSON пользователя"""
        if not os.path.exists(SHOP_LAYOUT_FILE):
            print("Файл layout не найден, используются значения по умолчанию")
            return

        try:
            with open(SHOP_LAYOUT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            elements = {elem['id']: elem for elem in data.get('elements', [])}
            count = 0

            for btn in self.buttons:
                if btn['id'] not in elements:
                    continue

                elem = elements[btn['id']]
                img = elem.get('image', {})
                hit = elem.get('hitbox', {})

                # Обновляем изображение
                if img:
                    btn['rect'].x = img.get('x', btn['rect'].x)
                    btn['rect'].y = img.get('y', btn['rect'].y)
                    btn['rect'].width = max(10, img.get('width', btn['rect'].width))
                    btn['rect'].height = max(10, img.get('height', btn['rect'].height))

                # Обновляем хитбокс
                if hit:
                    btn['hitbox_rect'].x = hit.get('x', btn['hitbox_rect'].x)
                    btn['hitbox_rect'].y = hit.get('y', btn['hitbox_rect'].y)
                    btn['hitbox_rect'].width = max(5, hit.get('width', btn['hitbox_rect'].width))
                    btn['hitbox_rect'].height = max(5, hit.get('height', btn['hitbox_rect'].height))

                # Синхронизируем с объектом меню
                self._sync_button(btn)
                count += 1

            # Обновляем панель отдельно
            if 'shop_panel' in elements:
                panel = elements['shop_panel']
                img = panel.get('image', {})
                self.panel_rect.x = img.get('x', self.panel_rect.x)
                self.panel_rect.y = img.get('y', self.panel_rect.y)
                self.panel_rect.width = max(50, img.get('width', self.panel_rect.width))
                self.panel_rect.height = max(50, img.get('height', self.panel_rect.height))

                self.menu._shop_panel_rect = self.panel_rect.copy()
                self.menu.shop_x = self.panel_rect.x
                self.menu.shop_y = self.panel_rect.y
                self.menu.shop_w = self.panel_rect.width
                self.menu.shop_h = self.panel_rect.height
                if hasattr(self.menu, '_make_shop_bg'):
                    self.menu.shop_bg = self.menu._make_shop_bg(self.panel_rect.size)

            print(f"✓ Загружено {count} элементов")

        except Exception as e:
            print(f"✗ Ошибка загрузки: {e}")
            import traceback
            traceback.print_exc()

    def _sync_button(self, btn):
        """Синхронизирует кнопку с объектом меню"""
        if not btn['obj']:
            return

        if hasattr(btn['obj'], 'rect'):
            btn['obj'].rect = btn['rect'].copy()
        if hasattr(btn['obj'], 'hitbox_rect'):
            btn['obj'].hitbox_rect = btn['hitbox_rect'].copy()

        # Для кнопок с изображением пробуем масштабировать
        if hasattr(btn['obj'], 'image') and btn['obj'].image:
            try:
                import pygame
                orig_image = getattr(btn['obj'], '_original_image', None)
                if orig_image:
                    btn['obj'].image = pygame.transform.scale(orig_image, (btn['rect'].width, btn['rect'].height))
                else:
                    # Сохраняем оригинал при первом ресайзе
                    btn['obj']._original_image = btn['obj'].image.copy()
                    btn['obj'].image = pygame.transform.scale(btn['obj'].image, (btn['rect'].width, btn['rect'].height))
            except:
                pass  # Если не получилось масштабировать, просто меняем rect

    def get_target(self, pos):
        """Находит что тянуть под курсором"""
        # Идем сверху вниз (обратный порядок)
        for btn in reversed(self.buttons):
            if self.drag_mode == DragMode.IMAGE:
                if btn['rect'].collidepoint(pos):
                    return btn, 'image'
            else:
                if btn['hitbox_rect'].collidepoint(pos):
                    return btn, 'hitbox'
        return None, None

    def handle_events(self):
        mx, my = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return False

            if ev.type == pygame.KEYDOWN:
                # Сохранение
                if ev.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    self.save_layout()
                    continue

                # Сетка
                if ev.key == pygame.K_g:
                    self.show_grid = not self.show_grid
                    print(f"Сетка: {'ON' if self.show_grid else 'OFF'}")
                    continue

                # Режимы
                if ev.key == pygame.K_1:
                    self.drag_mode = DragMode.IMAGE
                    print("Режим: IMAGE (изображения)")
                elif ev.key == pygame.K_2:
                    self.drag_mode = DragMode.HITBOX
                    print("Режим: HITBOX (хитбоксы)")

                # Сброс хитбокса к изображению
                if ev.key == pygame.K_r:
                    for btn in self.buttons:
                        if btn['rect'].collidepoint((mx, my)) or btn['hitbox_rect'].collidepoint((mx, my)):
                            btn['hitbox_rect'].center = btn['rect'].center
                            self._sync_button(btn)
                            print(f"Хитбокс {btn['name']} выровнен по центру изображения")
                            break

            # Начало перетаскивания
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                btn, mode = self.get_target((mx, my))
                if btn:
                    if mode == 'image':
                        offset_x = mx - btn['rect'].x
                        offset_y = my - btn['rect'].y
                    else:
                        offset_x = mx - btn['hitbox_rect'].x
                        offset_y = my - btn['hitbox_rect'].y

                    self.dragging = (btn, mode, offset_x, offset_y)
                    print(f"Тащим: {btn['name']} ({mode})")

            # Конец перетаскивания
            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                if self.dragging:
                    # Синхронизируем при отпускании
                    btn = self.dragging[0]
                    self._sync_button(btn)
                    if btn['id'] == 'shop_panel':
                        self.menu._shop_panel_rect = self.panel_rect.copy()
                        if hasattr(self.menu, '_make_shop_bg'):
                            self.menu.shop_bg = self.menu._make_shop_bg(self.panel_rect.size)
                self.dragging = None

        # Обработка перетаскивания
        if self.dragging:
            btn, mode, off_x, off_y = self.dragging

            if mode == 'image':
                new_x = self.snap(mx - off_x)
                new_y = self.snap(my - off_y)
                btn['rect'].topleft = (new_x, new_y)

                if btn['id'] == 'shop_panel':
                    self.panel_rect = btn['rect'].copy()
            else:
                new_x = self.snap(mx - off_x)
                new_y = self.snap(my - off_y)
                btn['hitbox_rect'].topleft = (new_x, new_y)

        # Изменение размеров стрелками
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            # Находим элемент под курсором
            target_btn = None
            for btn in reversed(self.buttons):
                if btn['rect'].collidepoint((mx, my)) or btn['hitbox_rect'].collidepoint((mx, my)):
                    target_btn = btn
                    break

            if target_btn:
                mods = pygame.key.get_mods()
                step = 1 if (mods & pygame.KMOD_SHIFT) else 10  # SHIFT = точно

                # ALT + стрелки = размер изображения
                if mods & pygame.KMOD_ALT:
                    if keys[pygame.K_UP]:
                        target_btn['rect'].height = max(10, target_btn['rect'].height - step)
                    if keys[pygame.K_DOWN]:
                        target_btn['rect'].height += step
                    if keys[pygame.K_LEFT]:
                        target_btn['rect'].width = max(10, target_btn['rect'].width - step)
                    if keys[pygame.K_RIGHT]:
                        target_btn['rect'].width += step

                    if target_btn['id'] == 'shop_panel':
                        self.panel_rect = target_btn['rect'].copy()
                    self._sync_button(target_btn)

                # CTRL + стрелки = размер хитбокса
                elif mods & pygame.KMOD_CTRL:
                    if keys[pygame.K_UP]:
                        target_btn['hitbox_rect'].height = max(5, target_btn['hitbox_rect'].height - step)
                    if keys[pygame.K_DOWN]:
                        target_btn['hitbox_rect'].height += step
                    if keys[pygame.K_LEFT]:
                        target_btn['hitbox_rect'].width = max(5, target_btn['hitbox_rect'].width - step)
                    if keys[pygame.K_RIGHT]:
                        target_btn['hitbox_rect'].width += step

                    self._sync_button(target_btn)

        return True

    def draw(self):
        self.screen.fill((30, 30, 35))

        # Сетка
        if self.show_grid:
            for x in range(0, DESIGN_W, self.grid_size):
                pygame.draw.line(self.screen, (50, 50, 60), (x, 0), (x, DESIGN_H))
            for y in range(0, DESIGN_H, self.grid_size):
                pygame.draw.line(self.screen, (50, 50, 60), (0, y), (DESIGN_W, y))

        # Фон
        if self.menu.bg_image:
            self.screen.blit(self.menu.bg_image, (0, 0))

        # Затемнение
        overlay = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        # Панель
        panel_surf = pygame.Surface((self.panel_rect.width, self.panel_rect.height), pygame.SRCALPHA)
        panel_surf.fill((45, 45, 55, 200))
        self.screen.blit(panel_surf, self.panel_rect.topleft)
        pygame.draw.rect(self.screen, (80, 80, 90), self.panel_rect, 2)

        # Элементы меню
        if hasattr(self.menu, 'shop_tab_button'):
            self.menu.shop_tab_button.draw(self.screen)
        if hasattr(self.menu, 'inventory_tab_button'):
            self.menu.inventory_tab_button.draw(self.screen)
        if hasattr(self.menu, 'close_button'):
            self.menu.close_button.draw(self.screen)

        if self.menu.inventory_open:
            if hasattr(self.menu, 'arrow_left'):
                self.menu.arrow_left.draw(self.screen)
            if hasattr(self.menu, 'arrow_right'):
                self.menu.arrow_right.draw(self.screen)
            if hasattr(self.menu, 'character_buttons'):
                for btn in self.menu.character_buttons:
                    btn.draw(self.screen)

        mx, my = pygame.mouse.get_pos()

        # Отрисовка рамок
        for btn in self.buttons:
            is_hovered_img = btn['rect'].collidepoint((mx, my))
            is_hovered_hit = btn['hitbox_rect'].collidepoint((mx, my))
            is_dragging = self.dragging and self.dragging[0] == btn

            # Цвета
            if self.drag_mode == DragMode.IMAGE:
                img_color = (0, 255, 100) if is_hovered_img else (100, 200, 255)
                hit_color = (80, 80, 80)  # Тусклый хитбокс
            else:
                img_color = (80, 80, 80)  # Тусклое изображение
                hit_color = (255, 100, 255) if is_hovered_hit else (200, 100, 255)

            # Подсветка при перетаскивании
            if is_dragging:
                if self.dragging[1] == 'image':
                    img_color = (255, 255, 0)
                else:
                    hit_color = (255, 255, 0)

            # Рамка изображения (толще)
            pygame.draw.rect(self.screen, img_color, btn['rect'], 3 if is_hovered_img or is_dragging else 2)

            # Рамка хитбокса (тоньше, пунктирная)
            pygame.draw.rect(self.screen, hit_color, btn['hitbox_rect'], 2 if is_hovered_hit or is_dragging else 1)

            # Подпись
            label = self.font_small.render(btn['name'], True, img_color)
            self.screen.blit(label, (btn['rect'].x, btn['rect'].y - 18))

            # Размеры при наведении
            if is_hovered_img or is_hovered_hit:
                info = f"I:{btn['rect'].width}x{btn['rect'].height} H:{btn['hitbox_rect'].width}x{btn['hitbox_rect'].height}"
                info_surf = self.font_small.render(info, True, (255, 255, 255))
                self.screen.blit(info_surf, (btn['rect'].x, btn['rect'].bottom + 3))

        # HUD
        mode_str = "IMAGE" if self.drag_mode == DragMode.IMAGE else "HITBOX"
        status = f"Mode: {mode_str} | "
        if self.dragging:
            status += f"Dragging: {self.dragging[0]['name']} ({self.dragging[1]}) | "

        hud = status + "1:Img 2:Hit | LMB:drag | ALT+arrows:resize img | CTRL+arrows:resize hit | R:align | G:grid | Ctrl+S:save"
        hud_surf = self.font.render(hud, True, (255, 255, 0))
        self.screen.blit(hud_surf, (10, 10))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    editor = ShopEditor()
    editor.run()