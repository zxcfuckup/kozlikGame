# main.py
import pygame
import random
import sys
import os
from player import Player
from game_platform import Platform
from coin import Coin
from sound import SoundManager
from menu import Menu, DESIGN_W, DESIGN_H

# -----------------------
# Инициализация
# -----------------------
pygame.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Warning: mixer init failed:", e)

display_info = pygame.display.Info()
WIN_W, WIN_H = max(800, display_info.current_w), max(600, display_info.current_h)
screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
pygame.display.set_caption("Приключение козлика")

game_surface = pygame.Surface((DESIGN_W, DESIGN_H)).convert_alpha()
clock = pygame.time.Clock()


def compute_scale_and_offset(window_w, window_h, design_w=DESIGN_W, design_h=DESIGN_H):
    scale = min(window_w / design_w, window_h / design_h)
    sw = max(1, int(design_w * scale))
    sh = max(1, int(design_h * scale))
    offset_x = (window_w - sw) // 2
    offset_y = (window_h - sh) // 2
    return scale, offset_x, offset_y, sw, sh


def real_to_design(mx, my, scale, offset_x, offset_y):
    dx = (mx - offset_x) / scale
    dy = (my - offset_y) / scale
    return dx, dy


def design_to_real(dx, dy, scale, offset_x, offset_y):
    rx = int(dx * scale + offset_x)
    ry = int(dy * scale + offset_y)
    return rx, ry


# -----------------------
# Ресурсы и Шрифты
# -----------------------
sound = SoundManager()
try:
    if hasattr(sound, "menu_music") and sound.menu_music:
        sound.play_music(sound.menu_music)
except:
    pass

menu = Menu()
in_menu = True


def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.smoothscale(img, size)
        return img
    except:
        return pygame.Surface(size if size else (100, 100))


bg = safe_load_image(os.path.join("images", "bg.jpg"), (DESIGN_W, DESIGN_H))
images_dict = {
    "cloudB": safe_load_image(os.path.join("images", "cloudB.png"), (120, 100)),
    "cloudM": safe_load_image(os.path.join("images", "cloudM.png"), (120, 100)),
    "grass": safe_load_image(os.path.join("images", "grass.png"), (120, 100)),
    "fake": safe_load_image(os.path.join("contents", "slabs", "cloudFake.png"), (100, 80))
}


def load_game_font(size):
    path = os.path.join("fonts", "GravitasOne-Regular.ttf")
    if os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except:
            pass
    return pygame.font.SysFont("Arial", size, bold=True)


main_font = load_game_font(26)
small_font = load_game_font(18)
big_font = load_game_font(50)

cursor_img = safe_load_image(os.path.join("images", "cursor.png"), (32, 32))

# -----------------------
# Логика игры
# -----------------------
hitbox_w, hitbox_h = 70, 15
platforms, coins, floating_texts = [], [], []
score, best_score, coin_count, combo = 0, 0, 0, 0
game_speed, game_over = 1.0, False
player = None
camera_trigger = 350


def spawn_platform(y, last_x):
    is_fake = random.random() < 0.20
    side = random.choice([-1, 1])
    offset = side * random.randint(110, 230)
    new_x = last_x + offset

    if new_x < 20: new_x = random.randint(30, 150)
    if new_x > DESIGN_W - hitbox_w - 20: new_x = DESIGN_W - hitbox_w - random.randint(30, 150)

    main_p = Platform(new_x, y, hitbox_w, hitbox_h, images_dict, fake=False)
    platforms.append(main_p)

    if random.random() < 0.15:
        coins.append(Coin(main_p.rect.centerx - 16, main_p.get_visual_top() - 36))

    if is_fake:
        fake_y = y + random.choice([-60, 60])
        fake_x = random.randint(20, DESIGN_W - hitbox_w - 20)
        if abs(fake_x - new_x) > 100:
            platforms.append(Platform(fake_x, fake_y, hitbox_w, hitbox_h, images_dict, fake=True))

    return new_x


def reset_game():
    global platforms, coins, score, combo, game_over, floating_texts, player, coin_count, game_speed
    platforms, coins, floating_texts = [], [], []
    score = combo = coin_count = 0
    game_over, game_speed = False, 1.0

    platforms.append(Platform(DESIGN_W // 2 - 35, 750, hitbox_w, hitbox_h, images_dict, fake=False))
    player = Player(platforms[0].rect.centerx - 32, platforms[0].rect.top - 80, menu.selected_character)
    player.set_sfx_volume(menu.sfx_volume)

    lx, ly = platforms[0].rect.x, 750
    for _ in range(15):
        ly -= random.randint(145, 185)
        lx = spawn_platform(ly, lx)


reset_game()

# -----------------------
# Основной цикл
# -----------------------
soft_x, soft_y = 200, 400
running = True
pygame.mouse.set_visible(False)

while running:
    clock.tick(60)
    sc, ox, oy, sw, sh = compute_scale_and_offset(WIN_W, WIN_H)
    mx_d, my_d = real_to_design(*pygame.mouse.get_pos(), sc, ox, oy)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.VIDEORESIZE:
            WIN_W, WIN_H = event.w, event.h
            screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
        menu.handle_event(event, (mx_d, my_d))
        if game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_game()
                if sound.game_music: sound.play_music(sound.game_music)
            if event.key == pygame.K_ESCAPE: in_menu = True

    sound.set_music_volume(menu.music_volume)
    sound.set_sfx_volume(menu.sfx_volume)

    if in_menu:
        if menu.start_game:
            in_menu = False;
            menu.start_game = False
            reset_game()
            if sound.game_music: sound.play_music(sound.game_music)
        game_surface.fill((0, 0, 0));
        menu.draw(game_surface)
    else:
        if not game_over:
            game_speed = min(3.5, 1.0 + (score / 500) * 0.15)
            keys = pygame.key.get_pressed()
            player.update(keys, DESIGN_W, game_speed)

            for p in platforms:
                if hasattr(p, 'update'): p.update(DESIGN_W, game_speed)

            # Обновление монеток (анимация кручения)
            for c in coins:
                if not c.collected and hasattr(c, 'update'):
                    c.update()

            hb = player.get_hitbox()
            for p in platforms[:]:
                if hb.colliderect(p.rect) and player.vel_y > 0:
                    if p.fake:
                        platforms.remove(p)
                        continue

                    player.jump(p.rect.top)
                    current_y = p.rect.y
                    if not p.scored:
                        val = 1 + combo;
                        score += val;
                        combo += 1;
                        p.scored = True
                        floating_texts.append({"x": p.rect.centerx, "y": p.rect.y, "a": 255, "t": f"+{val}"})
                        platforms = [plat for plat in platforms if plat.rect.y <= current_y + 5]

            for c in coins:
                if not c.collected and hb.colliderect(c.get_hitbox()):
                    c.collected = True;
                    coin_count += 1;
                    score += 5
                    floating_texts.append({"x": c.x, "y": c.y, "a": 255, "t": "+5"})

            if player.y < camera_trigger:
                diff = camera_trigger - player.y;
                player.y = camera_trigger
                for p in platforms: p.rect.y += diff
                for c in coins: c.y += diff
                for ft in floating_texts: ft["y"] += diff

                platforms = [p for p in platforms if p.rect.y < 1000]
                coins = [c for c in coins if c.y < 1000]

                while len(platforms) < 16:
                    spawn_platform(min(p.rect.y for p in platforms) - random.randint(150, 190), platforms[-1].rect.x)

            if player.y > DESIGN_H:
                game_over = True;
                best_score = max(best_score, score)
                if sound.menu_music: sound.play_music(sound.menu_music)
            if keys[pygame.K_ESCAPE]:
                in_menu = True
                if sound.menu_music: sound.play_music(sound.menu_music)

        # -----------------------
        # РИСОВАНИЕ
        # -----------------------
        game_surface.blit(bg, (0, 0))
        for p in platforms: p.draw(game_surface)
        for c in coins:
            if not c.collected: c.draw(game_surface)
        player.draw(game_surface, 0)

        for ft in floating_texts[:]:
            try:
                txt_img = small_font.render(ft["t"], True, (255, 255, 0))
                txt_img.set_alpha(ft["a"])
                game_surface.blit(txt_img, (ft["x"], ft["y"]))
            except:
                pass
            ft["y"] -= 2;
            ft["a"] -= 5
            if ft["a"] <= 0: floating_texts.remove(ft)


        # --- ИНТЕРФЕЙС С ТЕНЯМИ ---
        def draw_text_with_shadow(surf, text, font_obj, color, pos):
            shadow = font_obj.render(text, True, (0, 0, 0))
            surf.blit(shadow, (pos[0] + 2, pos[1] + 2))
            main_t = font_obj.render(text, True, color)
            surf.blit(main_t, pos)


        draw_text_with_shadow(game_surface, f"Очки: {score}", main_font, (255, 255, 255), (20, 20))
        draw_text_with_shadow(game_surface, f"Рекорд: {best_score}", small_font, (200, 200, 200), (20, 55))
        draw_text_with_shadow(game_surface, f"Монеты: {coin_count}", small_font, (255, 255, 0), (20, 80))
        draw_text_with_shadow(game_surface, f"Скорость: x{game_speed:.1f}", small_font, (100, 255, 100), (20, 105))

        if game_over:
            overlay = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200));
            game_surface.blit(overlay, (0, 0))
            over_txt = big_font.render("GAME OVER", True, (255, 50, 50))
            game_surface.blit(over_txt, over_txt.get_rect(center=(DESIGN_W // 2, DESIGN_H // 2 - 50)))
            hint = small_font.render("SPACE - Restart | ESC - Menu", True, (255, 255, 255))
            game_surface.blit(hint, hint.get_rect(center=(DESIGN_W // 2, DESIGN_H // 2 + 20)))

    # Масштабирование
    soft_x += (mx_d - soft_x) * 0.4;
    soft_y += (my_d - soft_y) * 0.4
    scaled_surf = pygame.transform.smoothscale(game_surface, (sw, sh))
    screen.fill((0, 0, 0));
    screen.blit(scaled_surf, (ox, oy))
    rx, ry = design_to_real(soft_x, soft_y, sc, ox, oy)
    screen.blit(cursor_img, (rx - 16, ry - 16))
    pygame.display.flip()

pygame.quit()
