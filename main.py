import pygame
import random
import sys
import math
from player import Player
from game_platform import Platform
from coin import Coin

# ИНИЦИАЛИЗАЦИЯ PYGAME
pygame.init()
pygame.mixer.init()

# --- ОКНО: set_mode должен быть до любых convert_alpha() ---
display_info = pygame.display.Info()
WIN_W, WIN_H = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
pygame.display.set_caption("Приключение козлика")


from menu import Menu, DESIGN_W, DESIGN_H

# ВИРТУАЛЬНЫЙ ХОЛСТ
game_surface = pygame.Surface((DESIGN_W, DESIGN_H)).convert_alpha()

clock = pygame.time.Clock()

#  Функции масштабирования
def compute_scale_and_offset(window_w, window_h, design_w=DESIGN_W, design_h=DESIGN_H):
    scale = min(window_w / design_w, window_h / design_h)
    sw = int(design_w * scale)
    sh = int(design_h * scale)
    offset_x = (window_w - sw) // 2
    offset_y = (window_h - sh) // 2
    return scale, offset_x, offset_y, sw, sh

scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(WIN_W, WIN_H)

def real_to_design(mx, my):
    dx = (mx - offset_x) / scale
    dy = (my - offset_y) / scale
    return dx, dy

def design_to_real(dx, dy):
    rx = int(dx * scale + offset_x)
    ry = int(dy * scale + offset_y)
    return rx, ry

#  ЗВУК
try:
    jump_sound = pygame.mixer.Sound("contents/sound/jumpSound.wav")
except Exception:
    jump_sound = None

#  МЕНЮ
menu = Menu()
in_menu = True
menu.load_layout_if_exists()

#  ГРАФИКА
bg = pygame.image.load("images/bg.jpg").convert_alpha()
bg = pygame.transform.smoothscale(bg, (DESIGN_W, DESIGN_H))

images_dict = {
    "cloudB": pygame.transform.smoothscale(pygame.image.load("images/cloudB.png").convert_alpha(), (120,100)),
    "cloudM": pygame.transform.smoothscale(pygame.image.load("images/cloudM.png").convert_alpha(), (120,100)),
    "fake": pygame.transform.smoothscale(pygame.image.load("contents/slabs/cloudFake.png").convert_alpha(), (100,80)),
    "grass": pygame.transform.smoothscale(pygame.image.load("images/grass.png").convert_alpha(), (120,100))
}

#  Состояние игры
hitbox_width, hitbox_height = 70, 15
platforms = []
coins = []
coin_count = 0

font = pygame.font.Font("fonts/GravitasOne-Regular.ttf", 24)
small_font = pygame.font.Font("fonts/GravitasOne-Regular.ttf", 18)

cursor = pygame.transform.scale(pygame.image.load("images/cursor.png").convert_alpha(), (32,32))
pygame.mouse.set_visible(False)
soft_x, soft_y = 200.0, 400.0

#  плавность курсора
LERP_SPEED = 0.5

score = 0
best_score = 0
combo = 0
camera_trigger_y = 300
game_over = False
floating_texts = []

player = None

#  Функции спавна/сброса
def spawn_platform(y, last_x):
    is_fake = random.random() < 0.15
    new_x = max(20, min(last_x + random.randint(-180, 180), DESIGN_W - hitbox_width - 20))
    plat = Platform(new_x, y, hitbox_width, hitbox_height, images_dict, fake=is_fake)
    platforms.append(plat)
    if is_fake:
        offset = random.choice([-100, 100])
        safe_x = max(20, min(new_x + offset, DESIGN_W - hitbox_width - 20))
        safe_plat = Platform(safe_x, y, hitbox_width, hitbox_height, images_dict, fake=False)
        platforms.append(safe_plat)
        spawn_coin(safe_plat)
        return safe_x
    spawn_coin(plat)
    return new_x

def spawn_coin(plat):
    if not plat.fake and random.random() < 0.2:
        coin_x = plat.rect.centerx - 16
        coin = Coin(coin_x, 0)
        visual_top = plat.get_visual_top()
        coin.y = visual_top - coin.img.get_height() - 4
        coins.append(coin)

def reset_game():
    global platforms, score, combo, game_over, floating_texts, player, coins, coin_count
    platforms = []
    floating_texts = []
    coins = []
    score = 0
    combo = 0
    coin_count = 0
    game_over = False

    y = 700
    for _ in range(3):
        plat = Platform(random.randint(80,220), y, hitbox_width, hitbox_height, images_dict, fake=False)
        platforms.append(plat)
        y -= 90

    start_x = platforms[0].rect.centerx - 32
    start_y = platforms[0].rect.top - 64
    player = Player(start_x, start_y)

    last_x = platforms[-1].rect.x
    for _ in range(15):
        y -= random.randint(130,160)
        last_x = spawn_platform(y, last_x)

reset_game()

# игровой цикл
running = True
while running:
    dt_ms = clock.tick(60)
    dt = dt_ms / 1000.0
    events = pygame.event.get()

    # 1. Получает координаты мыши ОДИН РАЗ за кадр
    mx_real, my_real = pygame.mouse.get_pos()
    mx_design, my_design = real_to_design(mx_real, my_real)

    # 2. Единый цикл обработки событий
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            WIN_W, WIN_H = event.w, event.h
            screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
            scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(WIN_W, WIN_H)

        # Передает события в меню
        if in_menu:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu.handle_event(event, mouse_pos_design=(mx_design, my_design))
            else:
                menu.handle_event(event, mouse_pos_design=None)

    # 3. Плавное движение курсора
    soft_x += (mx_design - soft_x) * LERP_SPEED
    soft_y += (my_design - soft_y) * LERP_SPEED

    if in_menu:
        #  ЛОГИКА МЕНЮ
        menu.draw(game_surface, debug=False)
        if menu.start_game:
            in_menu = False
            menu.start_game = False
            menu.load_layout_if_exists()
            continue
    else:
        #  ВСЯ ИГРОВАЯ ЛОГИКА
        keys = pygame.key.get_pressed()
        player.update(keys, DESIGN_W)
        hitbox = player.get_hitbox()

        for plat in platforms[:]:
            if hitbox.colliderect(plat.rect) and player.vel_y > 0:
                if plat.fake:
                    platforms.remove(plat)
                    continue
                player.jump(plat.rect.top)
                if not plat.scored:
                    pts = 1 + combo
                    score += pts
                    combo += 1
                    plat.scored = True
                    floating_texts.append({"x": plat.rect.centerx, "y": plat.rect.y - 20, "a": 255, "txt": f"+{pts}"})

        for c in coins:
            if not c.collected and hitbox.colliderect(c.get_hitbox()):
                c.collected = True
                coin_count += 1
                score += 1
                floating_texts.append({"x": c.x + 16, "y": c.y - 10, "a": 255, "txt": "+1"})

        if player.y < camera_trigger_y:
            diff = camera_trigger_y - player.y
            player.y = camera_trigger_y
            for plat in platforms: plat.rect.y += diff
            for c in coins: c.y += diff
            for t in floating_texts: t["y"] += diff

        platforms = [p for p in platforms if p.rect.y < 900]
        coins = [c for c in coins if c.y < 900]

        while len(platforms) < 12:
            y = min(p.rect.y for p in platforms) - random.randint(140, 160)
            spawn_platform(y, platforms[-1].rect.x)

        if player.y > DESIGN_H:
            game_over = True
            best_score = max(best_score, score)

        #  ОТРИСОВКА ИГРЫ
        game_surface.blit(bg, (0, 0))
        for plat in platforms: plat.draw(game_surface, 0)
        for c in coins: c.draw(game_surface, 0)
        player.draw(game_surface, 0)

        for t in floating_texts[:]:
            txt = small_font.render(t["txt"], True, (255, 220, 0))
            txt.set_alpha(t["a"])
            game_surface.blit(txt, (t["x"], t["y"]))
            t["y"] -= 2
            t["a"] -= 5
            if t["a"] <= 0: floating_texts.remove(t)

        # элементы интерфейса
        coin_text = font.render(f"Coins: {coin_count}", True, (255, 255, 255))
        game_surface.blit(coin_text, (20, 70))
        game_surface.blit(font.render(f"Очки: {score}", True, (255, 255, 255)), (10, 10))
        game_surface.blit(font.render(f"Рекорд: {best_score}", True, (255, 255, 255)), (10, 40))

        if game_over:
            game_surface.blit(font.render("GAME OVER", True, (255, 60, 60)), (110, 300))
            game_surface.blit(small_font.render("Нажми SPACE чтобы начать заново", True, (255, 255, 255)), (50, 350))
            game_surface.blit(small_font.render("ESC - в меню", True, (255, 255, 255)), (50, 380))

        if keys[pygame.K_ESCAPE]:
            in_menu = True
            menu.start_game = False
        if game_over and keys[pygame.K_SPACE]:
            reset_game()

    #  ФИНАЛЬНЫЙ ВЫВОД НА ЭКРАН

    scaled = pygame.transform.scale(game_surface, (scaled_w, scaled_h))
    screen.fill((0, 0, 0))
    screen.blit(scaled, (offset_x, offset_y))

    # Рисует курсор всегда в самом конце
    cur_x, cur_y = design_to_real(soft_x, soft_y)
    screen.blit(cursor, (cur_x - 16, cur_y - 16))

    pygame.display.flip()

pygame.quit()
sys.exit()
