import pygame


class Player:
    def __init__(self, x, y, character_path=None):
        self.x = x
        self.y = y

        self.vel_y = 0
        self.base_speed = 8  # Базовая скорость
        self.base_gravity = 0.5  # Базовая гравитация
        self.jump_strength = -15.5
        self.jump_sound = pygame.mixer.Sound("contents/sound/jumpSound.wav")
        self.jump_sound.set_volume(0.3)

        self.direction = "right"
        self.char_id = 1

        # Загрузка картинок (оставляю твой код без изменений для краткости)
        self.imgL_1 = pygame.transform.smoothscale(pygame.image.load("images/playerL.png").convert_alpha(), (80, 80))
        self.imgR_1 = pygame.transform.smoothscale(pygame.image.load("images/player1R.png").convert_alpha(), (80, 80))
        self.imgL_2 = pygame.transform.smoothscale(pygame.image.load("contents/characters/svinL.png").convert_alpha(),
                                                   (80, 80))
        self.imgR_2 = pygame.transform.smoothscale(pygame.image.load("contents/characters/svinR.png").convert_alpha(),
                                                   (80, 80))
        self.imgL_3 = pygame.transform.smoothscale(pygame.image.load("contents/characters/horseL.png").convert_alpha(),
                                                   (90, 90))
        self.imgR_3 = pygame.transform.smoothscale(pygame.image.load("contents/characters/horseR.png").convert_alpha(),
                                                   (90, 90))

        if character_path:
            if "player1" in character_path:
                self.char_id = 1
            elif "svin" in character_path:
                self.char_id = 2
            elif "horse" in character_path:
                self.char_id = 3

        self.land_squash = 0

    def set_sfx_volume(self, volume):
        self.jump_sound.set_volume(volume * 0.3)

    def move(self, keys, screen_width, speed_mult):
        # Умножаем скорость на множитель
        current_speed = self.base_speed * speed_mult
        if keys[pygame.K_LEFT]:
            self.x -= current_speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            self.x += current_speed
            self.direction = "right"
        self.x %= screen_width

    def apply_physics(self, speed_mult):
        # Гравитация и перемещение тоже зависят от скорости игры
        self.vel_y += self.base_gravity * speed_mult
        self.y += self.vel_y * speed_mult

    def get_hitbox(self):
        return pygame.Rect(self.x + 20, self.y + 50, 24, 14)

    def jump(self, platform_top):
        self.y = platform_top - 80
        self.vel_y = self.jump_strength  # Силу прыжка не умножаем, иначе он улетит
        self.land_squash = 8
        self.jump_sound.play()

    def update(self, keys, screen_width, speed_mult=1.0):
        self.move(keys, screen_width, speed_mult)
        self.apply_physics(speed_mult)

    def draw(self, screen, shake_y):
        s_y = int(80 - self.land_squash)
        self.land_squash = max(0, self.land_squash - 1)

        if self.char_id == 1:
            img = self.imgR_1 if self.direction == "right" else self.imgL_1
        elif self.char_id == 2:
            img = self.imgR_2 if self.direction == "right" else self.imgL_2
        else:
            img = self.imgR_3 if self.direction == "right" else self.imgL_3

        screen.blit(pygame.transform.scale(img, (80, s_y)), (self.x, self.y + (80 - s_y) + shake_y))
