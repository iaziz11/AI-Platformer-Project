import pygame, os
import numpy as np
from modules.game_objects.power_ups import Mushroom
from modules import settings as s

class Block(pygame.sprite.Sprite):
    def __init__(self, left, top, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (left,top)
        self.speed = np.array([0.0,0.0])
        self.spawned = False

    def update(self, playerGroup, enemyGroup, powerUpGroup):

        #if screen should be scrolling, move block to the left
        if s.SCROLLING:
            self.speed[0] = -round(s.SCROLLING_PLAYER.speed[0])
            self.rect = self.rect.move(self.speed)
            self.speed[0] = 0

        #check if running into any players, enemies, or power-ups, and push them if floor is moving
        collided_players = pygame.sprite.spritecollide(self, playerGroup, False)
        collided_enemies = pygame.sprite.spritecollide(self, enemyGroup, False)
        collided_power = pygame.sprite.spritecollide(self, powerUpGroup, False)

        #handle player collisions
        if len(collided_players) > 0:
            for i in collided_players:
                i.moveRectH(0, self.rect, False)

        #handle enemy collisions
        if len(collided_enemies) > 0:
            for i in collided_enemies:
                i.moveRectH(0, self.rect, False)
                i.direction *= -1
        
        #handle power-up collisions
        if len(collided_power) > 0:
            for i in collided_power:
                i.rect.right = self.rect.left
                i.direction *= -1

class Brick(Block):
    def __init__(self, left, top, group):
        image_path = os.path.join(s.ASSETS_PATH,'brick.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path), (s.BLOCK_SIZE,s.BLOCK_SIZE))
        self.id = "b"
        super().__init__(left,top,group)

    def broken(self):
        """
        removes bricks from block group
        """
        self.kill()   

class Floor(Block):
    def __init__(self, left, top, group):
        self.id = "f"
        image_path = os.path.join(s.ASSETS_PATH,'floor.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path), (s.BLOCK_SIZE,s.BLOCK_SIZE))
        super().__init__(left,top, group)

class Spawn_Block(Block):
    def __init__(self, left, top, group):
        self.id = "s"
        image_path = os.path.join(s.ASSETS_PATH,'spawn_block_1.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path), (s.BLOCK_SIZE,s.BLOCK_SIZE))
        super().__init__(left,top, group)
    
    def spawn(self,power_up_group):
        """
        spawns a mushroom and changes image of spawn block
        """

        if self.spawned:
            return
        p = os.path.join(s.ASSETS_PATH,'spawn_block_2.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(p), (s.BLOCK_SIZE,s.BLOCK_SIZE))
        m = Mushroom(self.rect.left,self.rect.top-s.BLOCK_SIZE)
        power_up_group.add(m)
        self.spawned = True
    
class Flag(Block):
    def __init__(self, left, top, group):
        self.id = "x"
        image_path = os.path.join(s.ASSETS_PATH,'flag.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(image_path), (s.BLOCK_SIZE,s.BLOCK_SIZE*9))
        super().__init__(left,top, group)