import pygame
import random
import sys
import os
from player import Player
from game_platform import Platform
from coin import Coin
from sound import SoundManager
from menu import Menu, DESIGN_W, DESIGN_H


class Stalactite:
    def __init__(self, images):
        self.raw_img = random.choice(images)
        self.w, self.h = 40, 80
        self.image = pygame.transform.smoothscale(self.raw_img, (self.w, self.h))
        hit_mask_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        hitbox_rect = pygame.Rect(self.w // 2 - 8, self.h - 25, 16, 20)
        pygame.draw.rect(hit_mask_surf, (255, 255, 255), hitbox_rect)
        self.mask = pygame.mask.from_surface(hit_mask_surf)
        self.x = random.randint(0, DESIGN_W - self.w)
        self.y = -self.h
        self.speed = random.uniform(2.0, 3.5)
        self.rect = self.image.get_rect(topleft=(self.x, self.y))

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))


class Bird:
    def __init__(self, images, start_y, direction):
        self.images = images
        self.frame = 0
        self.animation_timer = 0
        self.w, self.h = 70, 60

        self.scaled_images = []
        for img in self.images:
            scaled = pygame.transform.smoothscale(img, (self.w, self.h))
            self.scaled_images.append(scaled)

        self.direction = direction
        self.x = -self.w if direction == 1 else DESIGN_W + self.w
        self.y = start_y
        self.speed = random.uniform(1.5, 2.5)
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.mask = None
        self.phase = 0
        self.warning_timer = 45
        self.blink_timer = 0

    def update(self):
        if self.phase == 0:
            self.warning_timer -= 1
            self.blink_timer += 1
            if self.warning_timer <= 0:
                self.phase = 1
            return False

        self.x += self.speed * self.direction
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.frame = (self.frame + 1) % len(self.scaled_images)

        return True

    def get_mask(self):
        if self.phase == 0:
            return None
        img = self.scaled_images[self.frame]
        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)
        return pygame.mask.from_surface(img)

    def draw(self, surface):
        if self.phase == 0:
            if (self.blink_timer // 8) % 2 == 0:
                warn_x = 10 if self.direction == 1 else DESIGN_W - 40
                pygame.draw.circle(surface, (255, 50, 50), (warn_x + 15, int(self.y) - 25), 15)
                pygame.draw.circle(surface, (255, 255, 255), (warn_x + 15, int(self.y) - 25), 12)
                f = pygame.font.SysFont("Arial", 20, bold=True)
                t = f.render("!", True, (255, 50, 50))
                surface.blit(t, (warn_x + 11, int(self.y) - 35))
            return

        img = self.scaled_images[self.frame]
        if self.direction == -1:
            img = pygame.transform.flip(img, True, False)
        surface.blit(img, (self.x, self.y))

    def is_off_screen(self):
        if self.direction == 1:
            return self.x > DESIGN_W + 100
        else:
            return self.x < -self.w - 100


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


sound = SoundManager()
menu = Menu()
in_menu = True

if sound.menu_music:
    sound.play_music(sound.menu_music)


def safe_load_image(path, size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        return img
    except:
        surf = pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf


bg1 = safe_load_image(os.path.join("images", "bg.jpg"), (DESIGN_W, DESIGN_H))
bg2 = safe_load_image(os.path.join("contents", "backgroundsF", "bg2.jpg"), (DESIGN_W, DESIGN_H))
bg3 = safe_load_image(os.path.join("contents", "backgroundsF", "forestbg3.jpg"), (DESIGN_W, DESIGN_H))

stalactite_images = [
    safe_load_image(os.path.join("contents", "contentGame", "stalactite1.png")),
    safe_load_image(os.path.join("contents", "contentGame", "stalactite2.png")),
    safe_load_image(os.path.join("contents", "contentGame", "stalactite3.png"))
]

bird_images = [
    safe_load_image(os.path.join("contents", "contentGame", "bierd1.png")),
    safe_load_image(os.path.join("contents", "contentGame", "bierd2.png")),
    safe_load_image(os.path.join("contents", "contentGame", "bierd3.png"))
]

PLATFORM_WIDTH = 80
PLATFORM_HEIGHT = 30

images_dict_lvl1 = {
    "cloudB": safe_load_image(os.path.join("images", "cloudB.png"), (PLATFORM_WIDTH, 60)),
    "cloudM": safe_load_image(os.path.join("images", "cloudM.png"), (PLATFORM_WIDTH, 60)),
    "grass": safe_load_image(os.path.join("images", "grass.png"), (PLATFORM_WIDTH, 60)),
    "fake": safe_load_image(os.path.join("contents", "slabs", "cloudFake.png"), (PLATFORM_WIDTH, 50))
}

images_dict_lvl2 = {
    "cloudB": safe_load_image(os.path.join("contents", "slabs", "brickPlatform.png"), (PLATFORM_WIDTH, 60)),
    "cloudM": safe_load_image(os.path.join("contents", "slabs", "stonePlatform.png"), (PLATFORM_WIDTH, 60)),
    "grass": safe_load_image(os.path.join("contents", "slabs", "brickPlatform.png"), (PLATFORM_WIDTH, 60)),
    "fake": None
}

images_dict_lvl3 = {
    "cloudB": safe_load_image(os.path.join("contents", "slabs", "planks.png"), (PLATFORM_WIDTH, 60)),
    "cloudM": safe_load_image(os.path.join("contents", "slabs", "planks.png"), (PLATFORM_WIDTH, 60)),
    "grass": safe_load_image(os.path.join("contents", "slabs", "planks.png"), (PLATFORM_WIDTH, 60)),
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

platforms, coins, floating_texts, stalactites, birds = [], [], [], [], []
score, best_score, coin_count, combo = 0, 0, 0, 0
game_speed, game_over = 1.0, False
player, camera_trigger = None, 350
stalactite_timer = 0
bird_timer = 0


def spawn_platform(y, last_x):
    current_images = get_level_images()
    roll = random.random()
    is_fake_chance = (menu.selected_level == 1 and random.random() < 0.20)

    if roll < 0.5:
        _spawn_single_platform(y, last_x, current_images, is_fake_chance)
    elif roll < 0.9:
        _spawn_double_platforms(y, current_images, is_fake_chance)
    else:
        _spawn_triple_platforms(y, current_images)
    return last_x


def get_level_images():
    if menu.selected_level == 1:
        return images_dict_lvl1
    elif menu.selected_level == 2:
        return images_dict_lvl2
    else:
        return images_dict_lvl3


def _spawn_single_platform(y, last_x, current_images, is_fake=False):
    side = random.choice([-1, 1])
    offset = side * random.randint(90, 200)
    new_x = last_x + offset
    new_x = max(10, min(new_x, DESIGN_W - PLATFORM_WIDTH - 10))

    main_p = Platform(new_x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images, fake=False)
    platforms.append(main_p)

    if is_fake:
        fake_side = 1 if side == -1 else -1
        fake_offset = fake_side * random.randint(80, 150)
        fake_x = new_x + fake_offset
        fake_x = max(20, min(fake_x, DESIGN_W - PLATFORM_WIDTH - 20))
        if abs(fake_x - new_x) > 60:
            platforms.append(
                Platform(fake_x, y + random.randint(-40, 40), PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images,
                         fake=True))

    if random.random() < 0.15:
        coins.append(Coin(main_p.rect.centerx - 16, main_p.rect.top - 36))
    return new_x


def _spawn_double_platforms(y, current_images, is_fake=False):
    gap = 40
    left_x = random.randint(15, DESIGN_W // 2 - PLATFORM_WIDTH - gap)
    left_p = Platform(left_x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images, fake=False)
    platforms.append(left_p)

    right_x = random.randint(DESIGN_W // 2 + gap, DESIGN_W - PLATFORM_WIDTH - 15)
    right_p = Platform(right_x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images, fake=False)
    platforms.append(right_p)

    if is_fake and menu.selected_level == 1:
        fake_x = random.randint(20, DESIGN_W - PLATFORM_WIDTH - 20)
        if abs(fake_x - left_x) > 50 and abs(fake_x - right_x) > 50:
            platforms.append(
                Platform(fake_x, y + random.randint(-30, 30), PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images,
                         fake=True))

    if random.random() < 0.5:
        target = left_p if random.random() < 0.5 else right_p
        coins.append(Coin(target.rect.centerx - 16, target.rect.top - 36))
    elif random.random() < 0.3:
        mid_x = (left_p.rect.centerx + right_p.rect.centerx) // 2
        coins.append(Coin(mid_x - 16, y - 60))


def _spawn_triple_platforms(y, current_images):
    gap = 20
    total_width = 3 * PLATFORM_WIDTH + 2 * gap
    start_x = (DESIGN_W - total_width) // 2
    left_p = Platform(start_x, y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images, fake=False)
    platforms.append(left_p)
    center_p = Platform(start_x + PLATFORM_WIDTH + gap, y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images, fake=False)
    platforms.append(center_p)
    right_p = Platform(start_x + 2 * (PLATFORM_WIDTH + gap), y, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images,
                       fake=False)
    platforms.append(right_p)
    if random.random() < 0.7:
        coins.append(Coin(center_p.rect.centerx - 16, center_p.rect.top - 36))
    else:
        target = random.choice([left_p, right_p])
        coins.append(Coin(target.rect.centerx - 16, target.rect.top - 50))


def reset_game():
    global platforms, coins, floating_texts, stalactites, birds
    global score, combo, coin_count, game_over, game_speed, stalactite_timer, bird_timer

    platforms, coins, floating_texts, stalactites, birds = [], [], [], [], []
    score = combo = coin_count = stalactite_timer = bird_timer = 0
    game_over, game_speed = False, 1.0

    current_images = get_level_images()
    start_p = Platform(DESIGN_W // 2 - PLATFORM_WIDTH // 2, 750, PLATFORM_WIDTH, PLATFORM_HEIGHT, current_images,
                       fake=False)
    platforms.append(start_p)

    global player
    player = Player(start_p.rect.centerx - 32, start_p.rect.top - 80, menu.selected_character)
    player.set_sfx_volume(menu.sfx_volume)

    lx, ly = start_p.rect.x, 750
    for _ in range(15):
        ly -= random.randint(140, 180)
        lx = spawn_platform(ly, lx)


reset_game()

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

            # Сохраняем позицию ДО обновления для проверки коллизии
            old_player_y = player.y

            player.update(keys, DESIGN_W, game_speed)

            # Уровень 2 — сталактиты
            if menu.selected_level == 2:
                spawn_interval = max(80, 300 - (score // 15) * 5)
                stalactite_timer += 1
                if stalactite_timer >= spawn_interval:
                    stalactites.append(Stalactite(stalactite_images))
                    stalactite_timer = 0
                for s in stalactites[:]:
                    s.update()
                    if 0 < s.y < DESIGN_H:
                        if s.rect.colliderect(player.get_hitbox()):
                            game_over = True
                    if s.y > DESIGN_H:
                        stalactites.remove(s)

            # Уровень 3 — птички
            if menu.selected_level == 3:
                bird_timer += 1
                if bird_timer >= 60:
                    bird_timer = 0
                    if random.random() < 0.4:
                        bird_y = random.randint(200, DESIGN_H - 200)
                        direction = random.choice([-1, 1])
                        birds.append(Bird(bird_images, bird_y, direction))

                for b in birds[:]:
                    is_active = b.update()
                    if is_active:
                        if b.rect.colliderect(player.get_hitbox()):
                            game_over = True
                    if b.is_off_screen():
                        birds.remove(b)

                while len(birds) > 2:
                    birds.pop(0)

            for p in platforms:
                p.update(DESIGN_W, game_speed)
            for c in coins:
                if not c.collected:
                    c.update()

            # === ИСПРАВЛЕННАЯ КОЛЛИЗИЯ С ПЛАТФОРМАМИ ===
            # Находим ближайшую платформу под игроком
            player_hitbox = player.get_hitbox()
            player_feet = player_hitbox.bottom
            player_center_x = player_hitbox.centerx

            landed_platform = None

            for p in platforms[:]:
                # Проверяем только если игрок падает
                if player.vel_y <= 0:
                    continue

                # Проверяем горизонтальное пересечение (игрок над платформой)
                if not (player_hitbox.left < p.rect.right and player_hitbox.right > p.rect.left):
                    continue

                # Проверяем вертикальное пересечение:
                # игрок должен был быть выше платформы в прошлом кадре
                # и опуститься ниже верха платформы в этом кадре
                platform_top = p.rect.top + 5  # небольшой допуск

                old_player_feet = old_player_y + (player_hitbox.bottom - player.y)

                # Игрок пересек верх платформы сверху вниз?
                if old_player_feet <= platform_top and player_feet >= platform_top:
                    # Это самая высокая платформа под игроком?
                    if landed_platform is None or p.rect.top > landed_platform.rect.top:
                        landed_platform = p

            # Обрабатываем приземление только на одну платформу
            if landed_platform:
                p = landed_platform
                if p.fake:
                    platforms.remove(p)
                else:
                    # Приземляем игрока точно на платформу
                    player.y = p.rect.top - (player_hitbox.bottom - player.y)
                    player.vel_y = 0
                    player.on_ground = True

                    # === ИСПРАВЛЕНО: передаем platform_top в jump() ===
                    player.jump(p.rect.top)

                    if not p.scored:
                        val = 1 + combo
                        score, combo = score + val, combo + 1
                        p.scored = True
                        floating_texts.append({"x": p.rect.centerx, "y": p.rect.y, "a": 255, "t": f"+{val}"})

            # Монеты
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
                for b in birds: b.y += diff

            # Очистка
            platforms = [p for p in platforms if p.rect.y < DESIGN_H]
            coins = [c for c in coins if c.y < DESIGN_H]
            platforms = [p for p in platforms if p.rect.y < player.y + 500]

            while len(platforms) < 18:
                min_y = min(p.rect.y for p in platforms) if platforms else 400
                spawn_platform(min_y - random.randint(140, 180), platforms[-1].rect.x if platforms else DESIGN_W // 2)

            if player.y > DESIGN_H + 100:
                game_over = True
                best_score = max(best_score, score)
                if sound.menu_music:
                    sound.play_music(sound.menu_music)

        # Рисование
        if menu.selected_level == 1:
            game_surface.blit(bg1, (0, 0))
        elif menu.selected_level == 2:
            game_surface.blit(bg2, (0, 0))
        else:
            game_surface.blit(bg3, (0, 0))

        for p in platforms: p.draw(game_surface)
        for c in coins:
            if not c.collected: c.draw(game_surface)
        for s in stalactites: s.draw(game_surface)
        for b in birds: b.draw(game_surface)
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