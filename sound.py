# sound.py
import pygame
import os

BASE = os.path.dirname(__file__)

def _full(path):
    return os.path.join(BASE, path)

class SoundManager:
    def __init__(self):
        # Инициализируем микшер, если он еще не инициализирован
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Пути к музыке
        self.menu_music = _full("contents/sound/menu.wav")
        self.game_music = _full("contents/sound/Game1.wav")

        self.current_music = None

        # Громкость (0.0 - 1.0)
        self.music_volume = 1.0
        self.sfx_volume = 1.0

        # Загрузка SFX
        try:
            self.jump_sound = pygame.mixer.Sound(_full("contents/sound/jumpSound.wav"))
            self.jump_sound.set_volume(self.sfx_volume)
        except:
            print("Предупреждение: jumpSound.wav не найден")
            self.jump_sound = None

    # НОВЫЙ МЕТОД: для синхронизации со слайдерами из main.py
    def set_volumes(self, music_vol, sfx_vol):
        self.set_music_volume(music_vol)
        self.set_sfx_volume(sfx_vol)

    # Воспроизвести музыку, зациклить
    def play_music(self, path):
        try:
            # Если уже играет эта музыка — ничего не делаем
            if self.current_music == path and pygame.mixer.music.get_busy():
                return

            if os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1) # бесконечный цикл
                pygame.mixer.music.set_volume(self.music_volume)
                self.current_music = path
            else:
                print(f"Файл музыки не найден: {path}")
        except Exception as e:
            print("Ошибка загрузки музыки:", e)

    # Изменяем громкость музыки
    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    # Изменяем громкость звуков
    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))
        if self.jump_sound:
            self.jump_sound.set_volume(self.sfx_volume)

    # Воспроизвести эффект
    def play_sfx(self, sfx_sound):
        if sfx_sound and isinstance(sfx_sound, pygame.mixer.Sound):
            sfx_sound.set_volume(self.sfx_volume)
            sfx_sound.play()
