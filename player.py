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

        self.imgL = pygame.transform.smoothscale(
            pygame.image.load("images/playerL.png").convert_alpha(), (64, 64)
        )
        self.imgR = pygame.transform.smoothscale(
            pygame.image.load("images/player1R.png").convert_alpha(), (64, 64)
        )

        self.land_squash = 0

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
        self.y = platform_top - 64
        self.vel_y = self.jump_strength
        self.land_squash = 8
        self.jump_sound.play()

    def update(self, keys, screen_width):
        self.move(keys, screen_width)
        self.apply_physics()

    def draw(self, screen, shake_y):
        s_y = int(64 - self.land_squash)
        self.land_squash = max(0, self.land_squash - 1)

        img = self.imgR if self.direction == "right" else self.imgL  # ✅ исправлено
        screen.blit(
            pygame.transform.scale(img, (64, s_y)),
            (self.x, self.y + (64 - s_y) + shake_y)
        )