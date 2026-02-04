
import pygame
import os

BASE = os.path.dirname(__file__)

def _full(path):
    return os.path.join(BASE, path)

class Button:
    def __init__(self, image_path, center_pos, size, hitbox_padding=(0,0,0,0)):

        self.image_path = image_path
        self.load_image(size)
        self.rect = self.image.get_rect(center=tuple(center_pos))
        self.hitbox_padding = hitbox_padding
        self._update_hitbox_from_padding()

    def load_image(self, size=None):
        if size is None:
            size = (self.image.get_width(), self.image.get_height()) if hasattr(self, "image") else (100,50)
        try:
            img = pygame.image.load(_full(self.image_path)).convert_alpha()
            self.image = pygame.transform.smoothscale(img, (int(size[0]), int(size[1])))
        except Exception:

            self.image = pygame.Surface((int(size[0]), int(size[1])), pygame.SRCALPHA)
            self.image.fill((120,120,120,255))

    def _update_hitbox_from_padding(self):
        t, r, b, l = self.hitbox_padding
        self.hitbox_rect = pygame.Rect(
            self.rect.left + l,
            self.rect.top + t,
            max(1, self.rect.width - l - r),
            max(1, self.rect.height - t - b)
        )

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def draw_hitbox(self, surface, color=(255,0,0)):
        pygame.draw.rect(surface, color, self.hitbox_rect, 2)

    def is_hitbox_hit(self, pos):
        return self.hitbox_rect.collidepoint(pos)

    def is_image_hit(self, pos):
        return self.rect.collidepoint(pos)

    # помощник редакторов
    def move_image(self, dx, dy):
        self.rect.x += int(dx)
        self.rect.y += int(dy)
        self._update_hitbox_from_padding()

    def move_hitbox(self, dx, dy):
        self.hitbox_rect.x += int(dx)
        self.hitbox_rect.y += int(dy)

    def resize_image(self, dw, dh):
        new_w = max(5, int(self.rect.width + dw))
        new_h = max(5, int(self.rect.height + dh))
        center = self.rect.center
        self.load_image((new_w, new_h))
        self.rect = self.image.get_rect(center=center)
        self._update_hitbox_from_padding()

    def resize_hitbox(self, dw, dh):
        self.hitbox_rect.width = max(5, int(self.hitbox_rect.width + dw))
        self.hitbox_rect.height = max(5, int(self.hitbox_rect.height + dh))

    #  сериализация
    def to_dict(self):
        return {
            "image_path": self.image_path,
            "image_center": [int(self.rect.centerx), int(self.rect.centery)],
            "image_size": [int(self.rect.width), int(self.rect.height)],
            "hitbox_rect": [int(self.hitbox_rect.left), int(self.hitbox_rect.top),
                            int(self.hitbox_rect.width), int(self.hitbox_rect.height)]
        }

    @classmethod
    def from_dict(cls, data):
        # robust keys
        img = data.get("image_path") or data.get("image") or "contents/buttons/debug.png"
        center = tuple(data.get("image_center") or data.get("center") or (200,400))
        size = tuple(data.get("image_size") or data.get("size") or (100,50))
        btn = cls(img, center, size)
        if "hitbox_rect" in data:
            l,t,w,h = data["hitbox_rect"]
            btn.hitbox_rect = pygame.Rect(int(l), int(t), int(w), int(h))
        else:
            btn._update_hitbox_from_padding()
        return btn