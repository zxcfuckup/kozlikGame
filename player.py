import pygame


class Player:
    def __init__(self, x, y, character_path=None):
        self.x = x
        self.y = y

        self.vel_y = 0
        self.base_speed = 8
        self.base_gravity = 0.5
        self.jump_strength = -15.5

        try:
            self.jump_sound = pygame.mixer.Sound("contents/sound/jumpSound.wav")
            self.jump_sound.set_volume(0.3)
        except:
            self.jump_sound = None

        self.direction = "right"
        self.char_id = 1

        # Загрузка спрайтов
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

        # Текущий активный спрайт и его маска (ВАЖНО для main.py)
        self.image = self.imgR_1  # Начальное значение
        self.mask = pygame.mask.from_surface(self.image)

        self.land_squash = 0

    def set_sfx_volume(self, volume):
        if self.jump_sound:
            self.jump_sound.set_volume(volume * 0.3)

    def move(self, keys, screen_width, speed_mult):
        current_speed = self.base_speed * speed_mult
        if keys[pygame.K_LEFT]:
            self.x -= current_speed
            self.direction = "left"
        if keys[pygame.K_RIGHT]:
            self.x += current_speed
            self.direction = "right"

        # Зацикливание экрана
        if self.x > screen_width:
            self.x = 0
        elif self.x < -80:
            self.x = screen_width

    def apply_physics(self, speed_mult):
        self.vel_y += self.base_gravity * speed_mult
        self.y += self.vel_y * speed_mult

    def get_hitbox(self):
        # Оставляем Rect для быстрой предварительной проверки
        return pygame.Rect(self.x + 20, self.y + 50, 40, 30)

    def jump(self, platform_top):
        self.y = platform_top - 75
        self.vel_y = self.jump_strength
        self.land_squash = 12
        if self.jump_sound:
            self.jump_sound.play()

    def update(self, keys, screen_width, speed_mult=1.0):
        self.move(keys, screen_width, speed_mult)
        self.apply_physics(speed_mult)

        # Обновляем self.image в зависимости от ID и направления
        if self.char_id == 1:
            self.image = self.imgR_1 if self.direction == "right" else self.imgL_1
        elif self.char_id == 2:
            self.image = self.imgR_2 if self.direction == "right" else self.imgL_2
        else:
            self.image = self.imgR_3 if self.direction == "right" else self.imgL_3

        # Эффект приземления (сплющивание)
        if self.land_squash > 0:
            new_h = int(80 - self.land_squash)
            # Если нужно визуальное сплющивание, создаем временную картинку
            # Но маску оставляем от оригинальной картинки для честности коллизий
            self.land_squash = max(0, self.land_squash - 1)

        # ОБЯЗАТЕЛЬНО обновляем маску, если персонаж повернулся
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen, shake_y):
        # Применяем визуальный эффект squash при отрисовке
        draw_h = int(self.image.get_height() - self.land_squash)
        offset_y = self.image.get_height() - draw_h

        temp_img = pygame.transform.scale(self.image, (self.image.get_width(), draw_h))
        screen.blit(temp_img, (self.x, self.y + offset_y + shake_y))
