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
# Класс Сталактита
# -----------------------
class Stalactite:
    def __init__(self, images):
        self.raw_img = random.choice(images)
        self.w, self.h = 60, 120
        self.image = pygame.transform.smoothscale(self.raw_img, (self.w, self.h))
        self.mask = pygame.mask.from_surface(self.image)
        self.x = random.randint(0, DESIGN_W - self.w)
        self.y = -self.h
        self.speed = random.uniform(3.0, 5.0)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


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
    sw, sh = max(1, int(design_w * scale)), max(1, int(design_h * scale))
    offset_x, offset_y = (window_w - sw) // 2, (window_h - sh) // 2
    return scale, offset_x, offset_y, sw, sh


def real_to_design(mx, my, scale, offset_x, offset_y):
    return (mx - offset_x) / scale, (my - offset_y) / scale


def design_to_real(dx, dy, scale, offset_x, offset_y):
    return int(dx * scale + offset_x), int(dy * scale + offset_y)


# -----------------------
# Ресурсы
# -----------------------
sound = SoundManager()
menu = Menu()
in_menu = True

if sound.menu_music:
    sound.play_music(sound.menu_music)


def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size: img = pygame.transform.smoothscale(img, size)
        return img
    except:
        return pygame.Surface(size if size else (100, 100))


bg1 = safe_load_image(os.path.join("images", "bg.jpg"), (DESIGN_W, DESIGN_H))
bg2 = safe_load_image(os.path.join("contents", "backgroundsF", "bg2.jpg"), (DESIGN_W, DESIGN_H))

stalactite_images = [
    safe_load_image(os.path.join("contents", "contentGame", "stalactite1.png")),
    safe_load_image(os.path.join("contents", "contentGame", "stalactite2.png")),
    safe_load_image(os.path.join("contents", "contentGame", "stalactite3.png"))
]

images_dict_lvl1 = {
    "cloudB": safe_load_image(os.path.join("images", "cloudB.png"), (120, 100)),
    "cloudM": safe_load_image(os.path.join("images", "cloudM.png"), (120, 100)),
    "grass": safe_load_image(os.path.join("images", "grass.png"), (120, 100)),
    "fake": safe_load_image(os.path.join("contents", "slabs", "cloudFake.png"), (100, 80))
}

images_dict_lvl2 = {
    "cloudB": safe_load_image(os.path.join("contents", "slabs", "brickPlatform.png"), (100, 80)),
    "cloudM": safe_load_image(os.path.join("contents", "slabs", "stonePlatform.png"), (100, 80)),
    "grass": safe_load_image(os.path.join("contents", "slabs", "brickPlatform.png"), (100, 80)),
    "fake": None
}


def load_game_font(size):
    path = os.path.join("fonts", "GravitasOne-Regular.ttf")
    if os.path.exists(path):
        try:
            return pygame.font.Font(path, size)
        except:
            pass
    return pygame.font.SysFont("Arial", size, bold=True)


main_font, small_font, big_font = load_game_font(26), load_game_font(18), load_game_font(50)
cursor_img = safe_load_image(os.path.join("images", "cursor.png"), (32, 32))

# -----------------------
# Геймплей
# -----------------------
platforms, coins, floating_texts, stalactites = [], [], [], []
score, best_score, coin_count, combo = 0, 0, 0, 0
game_speed, game_over = 1.0, False
player, camera_trigger = None, 350
stalactite_timer = 0


def spawn_platform(y, last_x):
    current_images = images_dict_lvl1 if menu.selected_level == 1 else images_dict_lvl2
    is_fake_chance = (menu.selected_level == 1 and random.random() < 0.20)
    side = random.choice([-1, 1])
    offset = side * random.randint(110, 230)
    new_x = last_x + offset
    if new_x < 10: new_x = random.randint(10, 100)
    if new_x > DESIGN_W - 110: new_x = DESIGN_W - 110 - random.randint(10, 100)
    main_p = Platform(new_x, y, 100, 30, current_images, fake=False)
    platforms.append(main_p)
    if random.random() < 0.15:
        coins.append(Coin(main_p.rect.centerx - 16, main_p.rect.top - 36))
    if is_fake_chance:
        fake_x = random.randint(20, DESIGN_W - 110)
        if abs(fake_x - new_x) > 100:
            platforms.append(Platform(fake_x, y + random.choice([-60, 60]), 100, 30, current_images, fake=True))
    return new_x


def reset_game():
    global platforms, coins, floating_texts, stalactites, score, combo, coin_count, game_over, game_speed, stalactite_timer
    platforms, coins, floating_texts, stalactites = [], [], [], []
    score = combo = coin_count = stalactite_timer = 0
    game_over, game_speed = False, 1.0
    current_images = images_dict_lvl1 if menu.selected_level == 1 else images_dict_lvl2
    start_p = Platform(DESIGN_W // 2 - 50, 750, 100, 30, current_images, fake=False)
    platforms.append(start_p)
    global player
    player = Player(start_p.rect.centerx - 32, start_p.rect.top - 80, menu.selected_character)
    player.set_sfx_volume(menu.sfx_volume)
    lx, ly = start_p.rect.x, 750
    for _ in range(15):
        ly -= random.randint(150, 190)
        lx = spawn_platform(ly, lx)


reset_game()

# -----------------------
# Основной цикл
# -----------------------
soft_x, soft_y, running = 200, 400, True
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

        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    if sound.game_music: sound.play_music(sound.game_music)
                if event.key == pygame.K_ESCAPE:
                    in_menu = True
                    if sound.menu_music: sound.play_music(sound.menu_music)
            elif not in_menu:
                if event.key == pygame.K_ESCAPE:
                    in_menu = True
                    if sound.menu_music: sound.play_music(sound.menu_music)

    if in_menu:
        if player: player.set_sfx_volume(menu.sfx_volume)
        sound.set_volumes(menu.music_volume, menu.sfx_volume)
        if menu.start_game:
            in_menu, menu.start_game = False, False
            reset_game()
            if sound.game_music: sound.play_music(sound.game_music)
        game_surface.fill((0, 0, 0))
        menu.draw(game_surface)
    else:
        if not game_over:
            game_speed = min(3.5, 1.0 + (score / 500) * 0.15)
            keys = pygame.key.get_pressed()
            player.update(keys, DESIGN_W, game_speed)
            p_mask = pygame.mask.from_surface(player.image)

            # Сталактиты (Уровень 2)
            if menu.selected_level == 2:
                spawn_interval = max(50, 240 - (score // 10) * 8)
                stalactite_timer += 1
                if stalactite_timer >= spawn_interval:
                    stalactites.append(Stalactite(stalactite_images))
                    stalactite_timer = 0
                for s in stalactites[:]:
                    s.update()
                    s_offset = (s.rect.x - player.x, s.rect.y - player.y)
                    if p_mask.overlap(s.mask, s_offset): game_over = True
                    if s.y > DESIGN_H: stalactites.remove(s)

            for p in platforms: p.update(DESIGN_W, game_speed)
            for c in coins:
                if not c.collected: c.update()

            # Коллизии с платформами
            for p in platforms[:]:
                if player.vel_y > 0 and player.get_hitbox().colliderect(p.rect):
                    offset = (p.rect.x - player.x, p.rect.y - player.y)
                    if p_mask.overlap(p.mask, offset):
                        if player.y + 55 <= p.rect.centery:
                            if p.fake:
                                platforms.remove(p)
                                continue
                            player.jump(p.rect.top)
                            if not p.scored:
                                val = 1 + combo
                                score, combo = score + val, combo + 1
                                p.scored = True
                                floating_texts.append({"x": p.rect.centerx, "y": p.rect.y, "a": 255, "t": f"+{val}"})

            # Коллизии с монетами
            for c in coins:
                if not c.collected and player.get_hitbox().colliderect(c.get_hitbox()):
                    c.collected = True
                    coin_count, score = coin_count + 1, score + 5
                    floating_texts.append({"x": c.x, "y": c.y, "a": 255, "t": "+5"})

            # Камера
            if player.y < camera_trigger:
                diff = camera_trigger - player.y
                player.y = camera_trigger
                for p in platforms: p.rect.y += diff
                for c in coins: c.y += diff
                for ft in floating_texts: ft["y"] += diff
                for s in stalactites: s.y += diff

            # --- ВОТ ТУТ ЖЕСТКАЯ ОЧИСТКА ---
            # 1. Удаляем все платформы и монеты, которые ушли ниже экрана
            platforms = [p for p in platforms if p.rect.y < DESIGN_H]
            coins = [c for c in coins if c.y < DESIGN_H]

            # 2. Удаляем те, что под игроком (когда мы быстро летим вверх)
            # Если платформа ниже игрока на 500 пикселей - долой её
            platforms = [p for p in platforms if p.rect.y < player.y + 500]

            # Спавн новых платформ взамен удаленных
            while len(platforms) < 16:
                spawn_platform(min(p.rect.y for p in platforms) - random.randint(150, 190), platforms[-1].rect.x)

            if player.y > DESIGN_H:
                game_over = True
                best_score = max(best_score, score)
                if sound.menu_music: sound.play_music(sound.menu_music)

        # РИСОВАНИЕ
        game_surface.blit(bg1 if menu.selected_level == 1 else bg2, (0, 0))
        for p in platforms: p.draw(game_surface)
        for c in coins:
            if not c.collected: c.draw(game_surface)
        for s in stalactites: s.draw(game_surface)
        player.draw(game_surface, 0)

        for ft in floating_texts[:]:
            try:
                txt_img = small_font.render(ft["t"], True, (255, 255, 0))
                txt_img.set_alpha(ft["a"])
                game_surface.blit(txt_img, (ft["x"], ft["y"]))
            except:
                pass
            ft["y"] -= 2
            ft["a"] -= 5
            if ft["a"] <= 0: floating_texts.remove(ft)


        def draw_t(s, t, f, c, p):
            sh = f.render(t, True, (0, 0, 0))
            s.blit(sh, (p[0] + 2, p[1] + 2))
            s.blit(f.render(t, True, c), p)


        draw_t(game_surface, f"Очки: {score}", main_font, (255, 255, 255), (20, 20))
        draw_t(game_surface, f"Рекорд: {best_score}", small_font, (200, 200, 200), (20, 55))
        draw_t(game_surface, f"Монеты: {coin_count}", small_font, (255, 255, 0), (20, 80))
        draw_t(game_surface, f"Скорость: x{game_speed:.1f}", small_font, (100, 255, 100), (20, 105))

        if game_over:
            ov = pygame.Surface((DESIGN_W, DESIGN_H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 200))
            game_surface.blit(ov, (0, 0))
            t1 = big_font.render("GAME OVER", True, (255, 50, 50))
            game_surface.blit(t1, t1.get_rect(center=(DESIGN_W // 2, DESIGN_H // 2 - 50)))
            hint = small_font.render("SPACE - Restart | ESC - Menu", True, (255, 255, 255))
            game_surface.blit(hint, hint.get_rect(center=(DESIGN_W // 2, DESIGN_H // 2 + 20)))

    soft_x += (mx_d - soft_x) * 0.4
    soft_y += (my_d - soft_y) * 0.4
    scaled_s = pygame.transform.smoothscale(game_surface, (sw, sh))
    screen.fill((0, 0, 0))
    screen.blit(scaled_s, (ox, oy))
    rx, ry = design_to_real(soft_x, soft_y, sc, ox, oy)
    screen.blit(cursor_img, (rx - 16, ry - 16))
    pygame.display.flip()

pygame.quit()
