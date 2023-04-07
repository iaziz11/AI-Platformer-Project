import pygame
import os
from modules import settings as s


class Button(pygame.sprite.Sprite):
    def __init__(self, center, font, text, size) -> None:
        super().__init__()
        self.image = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, "button_template.png")),  (size[0], size[1]))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.text = font.render(text, True, (0, 0, 0), None)
        self.textRect = self.text.get_rect()
        self.textRect.center = self.rect.center


class stringButton(Button):

    def __init__(self, center, font, text, size, string) -> None:
        super().__init__(center, font, text, size)
        self.string = string

    def activate(self):
        """
        Called when button is clicked
        """

        return self.string


class intButton(Button):
    def __init__(self, center, font, text, size, num) -> None:
        super().__init__(center, font, text, size)
        self.num = num

    def activate(self):
        """
        Called when button is clicked
        """

        return self.num
