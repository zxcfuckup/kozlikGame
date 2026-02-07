# layout_editor.py
import pygame, sys, os
from menu import Menu, DESIGN_W, DESIGN_H

pygame.init()
BASE = os.path.dirname(__file__)

# окно
info = pygame.display.Info()
WIN_W, WIN_H = info.current_w, info.current_h
screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
pygame.display.set_caption("Layout Editor")
clock = pygame.time.Clock()

# поверхность дизайна
design_surface = pygame.Surface((DESIGN_W, DESIGN_H)).convert_alpha()

def compute_scale_and_offset(window_w, window_h):
    scale = min(window_w / DESIGN_W, window_h / DESIGN_H)
    sw = int(DESIGN_W * scale)
    sh = int(DESIGN_H * scale)
    ox = (window_w - sw) // 2
    oy = (window_h - sh) // 2
    return scale, ox, oy, sw, sh

scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(WIN_W, WIN_H)

def real_to_design(mx, my):
    return (mx - offset_x) / scale, (my - offset_y) / scale

def design_to_real(dx, dy):
    return int(dx*scale + offset_x), int(dy*scale + offset_y)

# меню
menu = Menu()

# добавляем новые кнопки в редактор
buttons = [
    menu.play_button,
    menu.settings_button,
    menu.exit_button,
    menu.shop_button,
    menu.debug_button,
    menu.logo,      # новая кнопка Logo
    menu.kozlik     # новая кнопка KOZLIKt
]

dragging = None
preview_horizontal = False

print("Editor running. Controls: SHIFT-image move | CTRL-hitbox move | Shift/CTRL + arrows resize | Ctrl+S save")

# загрузка существующего макета
menu.load_layout_if_exists()

while True:
    dt = clock.tick(60)
    events = pygame.event.get()
    mx_real, my_real = pygame.mouse.get_pos()
    mx, my = real_to_design(mx_real, my_real)

    for ev in events:
        if ev.type == pygame.QUIT:
            menu.save_layout()
            pygame.quit(); sys.exit()

        if ev.type == pygame.VIDEORESIZE:
            WIN_W, WIN_H = ev.w, ev.h
            screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
            scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(WIN_W, WIN_H)

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_h:
                preview_horizontal = not preview_horizontal
            if ev.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                menu.save_layout()
                print("Saved layout.json")

        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mods = pygame.key.get_mods()
            shift = mods & pygame.KMOD_SHIFT
            ctrl = mods & pygame.KMOD_CTRL

            for btn in buttons[::-1]:
                if shift and btn.is_image_hit((mx,my)):
                    dragging = (btn, "image", mx, my, btn.rect.x, btn.rect.y)
                    break
                if ctrl and btn.is_hitbox_hit((mx,my)):
                    dragging = (btn, "hitbox", mx, my, btn.hitbox_rect.x, btn.hitbox_rect.y)
                    break

        if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
            dragging = None

    # перетаскивание изображения или хитбокса
    if dragging:
        btn, mode, start_mx, start_my, start_x, start_y = dragging
        dx = mx - start_mx
        dy = my - start_my
        if mode == "image":
            btn.rect.x = int(start_x + dx)
            btn.rect.y = int(start_y + dy)
            btn._update_hitbox_from_padding()
        else:
            btn.hitbox_rect.x = int(start_x + dx)
            btn.hitbox_rect.y = int(start_y + dy)
        dragging = (btn, mode, mx, my, start_x + dx, start_y + dy)

    # изменение размера
    keys = pygame.key.get_pressed()
    mods = pygame.key.get_mods()
    if mods & pygame.KMOD_SHIFT:
        # image resize
        step = 6
        if keys[pygame.K_UP]:
            for btn in buttons:
                if btn.is_image_hit((mx,my)):
                    btn.resize_image(0, -step)
        if keys[pygame.K_DOWN]:
            for btn in buttons:
                if btn.is_image_hit((mx,my)):
                    btn.resize_image(0, step)
        if keys[pygame.K_RIGHT]:
            for btn in buttons:
                if btn.is_image_hit((mx,my)):
                    btn.resize_image(step, 0)
        if keys[pygame.K_LEFT]:
            for btn in buttons:
                if btn.is_image_hit((mx,my)):
                    btn.resize_image(-step, 0)
    if mods & pygame.KMOD_CTRL:
        # изменение размера хитбокса
        step = 6
        if keys[pygame.K_UP]:
            for btn in buttons:
                if btn.is_hitbox_hit((mx,my)):
                    btn.resize_hitbox(0, -step)
        if keys[pygame.K_DOWN]:
            for btn in buttons:
                if btn.is_hitbox_hit((mx,my)):
                    btn.resize_hitbox(0, step)
        if keys[pygame.K_RIGHT]:
            for btn in buttons:
                if btn.is_hitbox_hit((mx,my)):
                    btn.resize_hitbox(step, 0)
        if keys[pygame.K_LEFT]:
            for btn in buttons:
                if btn.is_hitbox_hit((mx,my)):
                    btn.resize_hitbox(-step, 0)

    # рисование на поверхности дизайна
    design_surface.fill((30,30,30))
    # фон
    bg_path = os.path.join(BASE, "contents/backgroundsF/menu.jpg")
    if os.path.exists(bg_path):
        try:
            bg = pygame.image.load(bg_path).convert_alpha()
            bg = pygame.transform.smoothscale(bg, (DESIGN_W, DESIGN_H))
            design_surface.blit(bg, (0,0))
        except:
            pass

    # отрисовка кнопок и хитбоксов
    for btn in buttons:
        # проверка что изображение подгружено в нужный размер
        if (btn.rect.width, btn.rect.height) != (btn.image.get_width(), btn.image.get_height()):
            btn.load_image((btn.rect.width, btn.rect.height))
        design_surface.blit(btn.image, btn.rect)
        pygame.draw.rect(design_surface, (255,0,0), btn.hitbox_rect, 2)

    # масштабирование для окна и отрисовка
    scaled = pygame.transform.smoothscale(design_surface, (scaled_w, scaled_h))
    screen.fill((0,0,0))
    if preview_horizontal:
        rotated = pygame.transform.rotate(scaled, -90)
        rx, ry = rotated.get_size()
        sx = (WIN_W - rx) // 2
        sy = (WIN_H - ry) // 2
        screen.blit(rotated, (sx, sy))
    else:
        screen.blit(scaled, (offset_x, offset_y))

    # подсказки сверху (HUD)
    font = pygame.font.Font(None, 20)
    hud = "SHIFT: image move | CTRL: hitbox move | Shift/CTRL + arrows resize | Ctrl+S save | H toggle preview"
    screen.blit(font.render(hud, True, (255,255,0)), (10,10))

    pygame.display.flip()