import pygame
import random
import sys
from player import Player
from game_platform import Platform
from coin import Coin
from menu import Menu

pygame.init()
pygame.mixer.init()

# ------------------ НАСТРОЙКИ ОКНА ------------------
#  разрешение — не трогает логику, рисует в этих координатах
DESIGN_W, DESIGN_H = 400, 800
# оставляет переменные, чтобы старый код использовал координаты
screen_width = DESIGN_W
screen_height = DESIGN_H

# получает реальное окно
display_info = pygame.display.Info()
actual_w, actual_h = display_info.current_w, display_info.current_h
screen = pygame.display.set_mode((actual_w, actual_h), pygame.RESIZABLE)
pygame.display.set_caption("Приключение козлика")
clock = pygame.time.Clock()

# создаёт виртуальный холст
game_surface = pygame.Surface((DESIGN_W, DESIGN_H)).convert_alpha()

# helper для масштабирования и центрирования
def compute_scale_and_offset(window_w, window_h, design_w=DESIGN_W, design_h=DESIGN_H):
    scale = min(window_w / design_w, window_h / design_h)
    sw = int(design_w * scale)
    sh = int(design_h * scale)
    offset_x = (window_w - sw) // 2
    offset_y = (window_h - sh) // 2
    return scale, offset_x, offset_y, sw, sh

scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(actual_w, actual_h)

def real_to_design(mx, my):
    dx = (mx - offset_x) / scale
    dy = (my - offset_y) / scale
    return dx, dy

def design_to_real(dx, dy):
    rx = int(dx * scale + offset_x)
    ry = int(dy * scale + offset_y)
    return rx, ry

# ------------------ ЗВУКИ ------------------

jump_sound = pygame.mixer.Sound("contents/sound/jumpSound.wav")

# меню
menu = Menu(screen)
in_menu = True

# ------------------ ФОН ------------------
bg = pygame.image.load("images/bg.jpg").convert_alpha()
# bg рисуем на виртуальном холсте — подгоняем к дизайну
bg = pygame.transform.smoothscale(bg, (DESIGN_W, DESIGN_H))

images_dict = {
    "cloudB": pygame.transform.smoothscale(pygame.image.load("images/cloudB.png").convert_alpha(), (120, 100)),
    "cloudM": pygame.transform.smoothscale(pygame.image.load("images/cloudM.png").convert_alpha(), (120, 100)),
    "fake": pygame.transform.smoothscale(pygame.image.load("contents/slabs/cloudFake.png").convert_alpha(), (100, 80)),
    "grass": pygame.transform.smoothscale(pygame.image.load("images/grass.png").convert_alpha(), (120, 100))
}
platforms = []
hitbox_width, hitbox_height = 70, 15

# ------------------ МОНЕТКИ ------------------
coins = []
coin_count = 0

font = pygame.font.Font(None, 36)

# ------------------ ШРИФТЫ И КУРСОР ------------------
font = pygame.font.Font("fonts/GravitasOne-Regular.ttf", 24)
small_font = pygame.font.Font("fonts/GravitasOne-Regular.ttf", 18)

cursor = pygame.transform.scale(pygame.image.load("images/cursor.png").convert_alpha(), (32, 32))
pygame.mouse.set_visible(False)
# soft_x/y — в design-координатах
soft_x, soft_y = 200, 400
smoothness = 0.35

# ------------------ СОСТОЯНИЕ ИГРЫ ------------------
score = 0
best_score = 0
combo = 0
camera_trigger_y = 300
game_over = False
floating_texts = []

player = None

# ------------------ ФУНКЦИИ ------------------

def spawn_platform(y, last_x):
    #Создаёт платформу и случайно монетку на ней
    is_fake = random.random() < 0.15
    new_x = max(20, min(last_x + random.randint(-180, 180), DESIGN_W - hitbox_width - 20))
    plat = Platform(new_x, y, hitbox_width, hitbox_height, images_dict, fake=is_fake)
    platforms.append(plat)

    # Фейковая платформа + безопасная рядом
    if is_fake:
        offset = random.choice([-100, 100])
        safe_x = max(20, min(new_x + offset, DESIGN_W - hitbox_width - 20))
        safe_plat = Platform(safe_x, y, hitbox_width, hitbox_height, images_dict, fake=False)
        platforms.append(safe_plat)
        spawn_coin(safe_plat)
        return safe_x# Спавн монетки с шансом только на нормальной платформе
    spawn_coin(plat)
    return new_x

def spawn_coin(plat):
    # Создаёт монетку на платформе с шансом 20% и размещает её точно над визуальной частью платформы.
    if not plat.fake and random.random() < 0.2:
        # сначала создаёт монету с временной y (0)
        coin_x = plat.rect.centerx - 16  # монета по центру платформы (ширина монеты 32)
        coin = Coin(coin_x, 0)
        # вычисляет визуальную верхушку платформы и корректируем y монеты
        visual_top = plat.get_visual_top()
        coin.y = visual_top - coin.img.get_height() - 4  # 4 px отступ над платформой
        coins.append(coin)

def reset_game():
    global platforms, score, combo, game_over, floating_texts
    global player, coins, coin_count

    platforms = []
    floating_texts = []
    coins = []

    score = 0
    combo = 0
    coin_count = 0
    game_over = False

    # Стартовые платформы
    y = 700
    for _ in range(3):
        plat = Platform(random.randint(80, 220), y, hitbox_width, hitbox_height, images_dict, fake=False)
        platforms.append(plat)
        y -= 90

    start_x = platforms[0].rect.centerx - 32
    start_y = platforms[0].rect.top - 64
    player = Player(start_x, start_y)

    last_x = platforms[-1].rect.x
    for _ in range(15):
        y -= random.randint(130, 160)
        last_x = spawn_platform(y, last_x)

reset_game()

# ------------------ ГЛАВНЫЙ ЦИКЛ ------------------
running = True
while running:
    clock.tick(60)
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # проверка нажатий при Game Over внутри цикла событий
        if game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    reset_game()  # перезапуск
                if event.key == pygame.K_ESCAPE:
                    in_menu = True  # выход в меню
                    menu.start_game = False

        # ESC в игре (не в Game Over) — выход в меню
        if (not game_over) and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                in_menu = True
                menu.start_game = False

        # обработка ресайза окна (окно/ориентация)
        if event.type == pygame.VIDEORESIZE:
            actual_w, actual_h = event.w, event.h
            screen = pygame.display.set_mode((actual_w, actual_h), pygame.RESIZABLE)
            scale, offset_x, offset_y, scaled_w, scaled_h = compute_scale_and_offset(actual_w, actual_h)

    if in_menu:
        menu.handle_events(events)  # теперь self + events — ок
        menu.draw()

        mx, my = pygame.mouse.get_pos()
        soft_x += (mx - soft_x) * smoothness
        soft_y += (my - soft_y) * smoothness
        screen.blit(cursor, (soft_x - 16, soft_y - 16))

        if menu.start_game:
            reset_game()
            in_menu = False
            menu.start_game = False
        pygame.display.update()
        continue

    # --- Игровой блок ---
    if not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys, DESIGN_W)
        hitbox = player.get_hitbox()

        # --- Платформы ---
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
                    floating_texts.append({
                        "x": plat.rect.centerx,
                        "y": plat.rect.y - 20,
                        "a": 255,
                        "txt": f"+{pts}"
                    })

        # --- Монетки ---
        for c in coins:
            if not c.collected and hitbox.colliderect(c.get_hitbox()):
                c.collected = True
                coin_count += 1
                score += 1
                floating_texts.append({
                    "x": c.x + 16,
                    "y": c.y - 10,
                    "a": 255,
                    "txt": "+1"
                })

        # --- Камера ---
        if player.y < camera_trigger_y:
            diff = camera_trigger_y - player.y
            player.y = camera_trigger_y
            for plat in platforms:
                plat.rect.y += diff
            for c in coins:
                c.y += diff
            for t in floating_texts:
                t["y"] += diff
            platforms = [p for p in platforms if p.rect.y < 900]
            coins = [c for c in coins if c.y < 900]
            while len(platforms) < 12:
                y = min(p.rect.y for p in platforms) - random.randint(140, 170)
                spawn_platform(y, platforms[-1].rect.x)

        # --- Проверка падения ---
        if player.y > DESIGN_H:
            game_over = True
            best_score = max(best_score, score)

    # --- ОТРИСОВКА на виртуальном холсте ---
    game_surface.blit(bg, (0, 0))

    for plat in platforms:
        plat.draw(game_surface, 0)
    for c in coins:
        c.draw(game_surface, 0)
    player.draw(game_surface, 0)

    for t in floating_texts[:]:
        txt = small_font.render(t["txt"], True, (255, 220, 0))
        txt.set_alpha(t["a"])
        game_surface.blit(txt, (t["x"], t["y"]))
        t["y"] -= 2
        t["a"] -= 5
        if t["a"] <= 0:
            floating_texts.remove(t)

    # HUD на виртуальном холсте
    coin_text = font.render(f"Coins: {coin_count}", True, (255, 255, 255))
    game_surface.blit(coin_text, (20, 70))
    game_surface.blit(font.render(f"Очки: {score}", True, (255, 255, 255)), (10, 10))
    game_surface.blit(font.render(f"Рекорд: {best_score}", True, (255, 255, 255)), (10, 40))

    if game_over:
        game_surface.blit(font.render("GAME OVER", True, (255, 60, 60)), (110, 300))
        game_surface.blit(
            small_font.render("Нажми SPACE чтобы начать заново", True, (255, 255, 255)),
            (50, 350)
        )

    # --- Масштабируем виртуальный кадр и выводим в окно ---
    scaled_surf = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))
    screen.fill((0, 0, 0))
    screen.blit(scaled_surf, (offset_x, offset_y))

    # курсор: переводим реальные координаты в дизайн-координаты для плавного курсора
    mx_real, my_real = pygame.mouse.get_pos()
    mx_design, my_design = real_to_design(mx_real, my_real)
    soft_x += (mx_design - soft_x) * smoothness
    soft_y += (my_design - soft_y) * smoothness
    cur_x, cur_y = design_to_real(soft_x, soft_y)
    screen.blit(cursor, (cur_x - 16, cur_y - 16))

    pygame.display.update()

pygame.quit()
sys.exit()
