import pygame, os
import numpy as np
from modules import settings as s

class Mushroom(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos):
        super().__init__()
        self.p = os.path.join(s.ASSETS_PATH,'mushroom.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(self.p), (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.rect = self.image.get_rect()
        self.rect.topleft = (xpos,ypos)
        self.direction = 1.0
        self.basespeed = 3.0
        self.speed = np.array([self.basespeed*self.direction, 0.0])
    
    def horizontal_movement(self, blockGroup):

        """
        checks collisions after the power-up moves horizontally
        """

        #despawn if off-screen
        if self.rect.right < 0:
            self.kill()
            
        #check all relevant collisions
        collided_blocks = pygame.sprite.spritecollide(self,blockGroup,False)        

        #handle block collisions
        if len(collided_blocks) > 0:
            if self.speed[0]*self.direction > 0:
                self.rect.right = collided_blocks[0].rect.left
            else:
                self.rect.left = collided_blocks[0].rect.right
            self.direction *= -1.0

    def vertical_movement(self, blockGroup):

        """
        checks collisions after the power-up moves vertically
        """

        #check all relevant collisions
        collided_blocks = pygame.sprite.spritecollide(self,blockGroup,False)

        #handle block collisions
        if len(collided_blocks) > 0:
            if self.speed[1] >= 0:
                self.rect.bottom = collided_blocks[0].rect.top
            else:
                self.rect.top = collided_blocks[0].rect.bottom
            self.speed[1] = 0.0

    def update(self,blockGroup):
        
        #change speed if the screen is scrolling
        if s.SCROLLING:
            self.speed[0] = (self.basespeed) - (self.direction*s.SCROLLING_PLAYER.speed[0])
        else:
            self.speed[0] = self.basespeed

        #move horizontally
        self.rect = self.rect.move(self.speed[0]*self.direction,0)
        self.horizontal_movement(blockGroup)
        
        #move vertically
        self.speed[1] += s.GRAVITY
        self.rect = self.rect.move(0,self.speed[1])
        self.vertical_movement(blockGroup)