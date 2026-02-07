import pygame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.vel_y = 0
        self.speed = 8
        self.gravity = 0.5
        self.jump_strength = -15.5
        self.jump_sound = pygame.mixer.Sound("contents/sound/jumpSound.wav")
        self.jump_sound.set_volume(0.3)  # громкость (0.0–1.0)

        self.direction = "right"
        self.char_id = 1  # 1 = козлик, 2 = свин, 3 = лошадь

        # Козлик
        self.imgL_1 = pygame.transform.smoothscale(
            pygame.image.load("images/playerL.png").convert_alpha(), (80, 80)
        )
        self.imgR_1 = pygame.transform.smoothscale(
            pygame.image.load("images/player1R.png").convert_alpha(), (80, 80)
        )

        # Свин
        self.imgL_2 = pygame.transform.smoothscale(
            pygame.image.load("contents/characters/svinL.png").convert_alpha(), (80, 80)
        )
        self.imgR_2 = pygame.transform.smoothscale(
            pygame.image.load("contents/characters/svinR.png").convert_alpha(), (80, 80)
        )

        # Лошадь
        self.imgL_3 = pygame.transform.smoothscale(
            pygame.image.load("contents/characters/horseL.png").convert_alpha(), (90, 90)
        )
        self.imgR_3 = pygame.transform.smoothscale(
            pygame.image.load("contents/characters/horseR.png").convert_alpha(), (90, 90)
        )

        self.land_squash = 0

    def switch_character(self, char_id):
        self.char_id = char_id

    def move(self, keys, screen_width):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = "right"

        self.x %= screen_width

    def apply_physics(self):
        self.vel_y += self.gravity
        self.y += self.vel_y

    def get_hitbox(self):
        return pygame.Rect(self.x + 20, self.y + 50, 24, 14)

    def jump(self, platform_top):
        self.y = platform_top - 80  # изменено с 64 на 80
        self.vel_y = self.jump_strength
        self.land_squash = 8
        self.jump_sound.play()

    def update(self, keys, screen_width):
        # Переключение персонажей клавишами 1, 2 и 3
        if keys[pygame.K_1]:
            self.switch_character(1)
        elif keys[pygame.K_2]:
            self.switch_character(2)
        elif keys[pygame.K_3]:
            self.switch_character(3)

        self.move(keys, screen_width)
        self.apply_physics()

    def draw(self, screen, shake_y):
        s_y = int(80 - self.land_squash)
        self.land_squash = max(0, self.land_squash - 1)

        # выбор картинки по персонажу и направлению
        if self.char_id == 1:  # козлик
            img = self.imgR_1 if self.direction == "right" else self.imgL_1
        elif self.char_id == 2:  # свин
            img = self.imgR_2 if self.direction == "right" else self.imgL_2
        else:  # лошадь
            img = self.imgR_3 if self.direction == "right" else self.imgL_3

        screen.blit(
            pygame.transform.scale(img, (80, s_y)),
            (self.x, self.y + (80 - s_y) + shake_y)
        )