# sound.py
import pygame
import os

BASE = os.path.dirname(__file__)

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        # Фоновая музыка
        self.menu_music = self.load_music("contents/sound/menu.wav")
        self.game_music = self.load_music("contents/sound/Game1.wav")
        # Эффекты
        self.jump_sound = self.load_sound("contents/sound/jumpSound.wav")
        # Статус
        self.current_music = None

    def load_music(self, path):
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Ошибка загрузки музыки {path}: {e}")
        return None

    def load_sound(self, path):
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Ошибка загрузки звука {path}: {e}")
        return None

    def play_music(self, music, loops=-1):
        if music and self.current_music != music:
            self.stop_music()
            music.play(loops)
            self.current_music = music

    def stop_music(self):
        if self.current_music:
            self.current_music.stop()
            self.current_music = None

    def play_jump(self):
        if self.jump_sound:
            self.jump_sound.play()