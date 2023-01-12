import pygame, os
import numpy as np
from modules import settings as s

class Enemy(pygame.sprite.Sprite):

    def __init__(self, xpos, ypos, basespeed, movespeed, direction, hitbox, group):
        super().__init__(group)
        self.rect = self.image.get_rect()
        self.rect.topleft = (xpos,ypos)
        self.direction = direction
        self.basespeed = basespeed
        self.movespeed = movespeed
        self.hitbox = pygame.Rect(0,0,hitbox[0],hitbox[1])
        self.hitbox.midbottom = self.rect.midbottom
        self.speed = np.array([basespeed, 0.0])
        self.anim_frames = 0
    
    def animate(self):
        """
        placeholder function meant to be overwritten by child classes
        """
        return

    def checkHitboxCollide(self, sprite, group):
        """
        checkHitboxCollide(sprite, group) is used to check collisions between two hitboxes

        :param sprite: the sprite we are checking
        :param group: the group to check collisions with 

        :return: a list of sprites from :group: whose hitboxes collide with :sprite:
        """
        
        s = []
        for i in group:
            if sprite.hitbox.colliderect(i.hitbox):
                s.append(i)
        return s

    def moveRectH(self, dx, other=None, left=False):

        """
        moveRectH(dx, other, left) is a wrapper for rect.move that also moves the hitbox

        :param dx: how much to move horizontally
        :param other: rect of sprite that is touching self
        :param left: Boolean representing whether or not other should be touching self.rect.left
        """

        if other:
            if left:
                self.rect.left = other.right
            else:
                self.rect.right = other.left
        else:
            self.rect = self.rect.move(dx, 0)
            
        self.hitbox.midbottom = self.rect.midbottom

    def moveRectV(self, dy, other=None, bottom=False):
        """
        moveRectV(dy, other, bottom) is a wrapper for rect.move that also moves the hitbox

        :param dy: how much to move vertically
        :param other: rect of sprite that is touching self
        :param bottom: Boolean representing whether or not other.rect should be touching self.rect.bottom
        """

        if other:
            if bottom:
                self.rect.bottom = other.top
            else:
                self.rect.top = other.bottom
        else:
            self.rect = self.rect.move(0, dy)
            
        self.hitbox.midbottom = self.rect.midbottom

    def horizontal_movement(self, blockGroup, enemyGroup, playerGroup):
        """
        horizontalMovement(blockGroup, enemyGroup, playerGroup) checks collisions after the enemy moves horizontally

        :param blockGroup: group that contains all blocks
        :param enemyGroup: group that contains all enemies
        :param playerGroup: group that contains all players
        """
        
        #check all relevant collisions
        collided_players = self.checkHitboxCollide(self, playerGroup)
        collided_blocks = pygame.sprite.spritecollide(self,blockGroup,False)
        collided_enemies = []

        #check collisions with other enemies
        for i in enemyGroup:
            if self != i:
                if self.rect.colliderect(i):
                    collided_enemies.append(i)
        
        #handle enemy collisions
        if len(collided_enemies) > 0:
            if self.speed[0]*self.direction > 0:
                self.moveRectH(0, collided_enemies[0].rect, False)
                collided_enemies[0].direction *= -1
            else:
                self.moveRectH(0, collided_enemies[0].rect, True)
                collided_enemies[0].direction *= -1
            self.direction *= -1.0

        #handle block collisions
        if len(collided_blocks) > 0:
            if self.speed[0]*self.direction < 0:
                self.moveRectH(0, collided_blocks[0].rect, True)
            else:
                self.moveRectH(0, collided_blocks[0].rect, False)
            self.direction *= -1.0
        
        #handle player collisions
        if len(collided_players) > 0:
            if collided_players[0].isBig:
                collided_players[0].small()
            else:
                if collided_players[0].iframes == 0:
                    collided_players[0].isAlive = False

    def vertical_movement(self, blockGroup, playerGroup, enemyGroup):

        """
        verticalMovement(blockGroup, playerGroup) checks collisions after the enemy moves vertically

        :param blockGroup: group that contains all blocks
        :param playerGroup: group that contains all players
        :param enemyGroup: group that contains all enemies
        """

        #check all relevant collisions
        collided_blocks = pygame.sprite.spritecollide(self, blockGroup, False)
        collided_players = self.checkHitboxCollide(self, playerGroup)
        collided_enemies = []

        #check collisions with other enemies
        for i in enemyGroup:
            if self != i:
                if self.rect.colliderect(i):
                    collided_enemies.append(i)

        #handle block collisions
        if len(collided_blocks) > 0:
            if self.speed[1] >= 0:
                self.moveRectV(0, collided_blocks[0].rect, True)
            else:
                self.moveRectV(0, collided_blocks[0].rect, False)
            self.speed[1] = 0
        
        #handle player collisions
        if len(collided_players) > 0:
            if collided_players[0].isBig:
                collided_players[0].small()
            else:
                if collided_players[0].iframes == 0:
                    collided_players[0].isAlive = False

        #handle enemy collisions
        if len(collided_enemies) > 0:
            if self.speed[1] >= 0:
                self.moveRectV(0, collided_enemies[0].rect, True)
            else:
                self.moveRectV(0, collided_enemies[0].rect, False)
            self.speed[1] = 0

    def update(self,blockGroup, enemyGroup, playerGroup):

        #change speed if the screen is scrolling
        self.speed[0] = self.basespeed if not s.SCROLLING else (self.basespeed) - (self.direction*round(s.SCROLLING_PLAYER.speed[0]))

        #move horizontally
        self.moveRectH(self.speed[0]*self.direction)
        self.horizontal_movement(blockGroup, enemyGroup, playerGroup)
        
        #constant downward acceleration
        self.speed[1] += s.GRAVITY

        #move vertically
        self.moveRectV(self.speed[1])
        self.vertical_movement(blockGroup, playerGroup, enemyGroup)

        #animate
        self.animate()

class Red_Enemy(Enemy):
    def __init__(self, xpos, ypos, group):
        self.id = "1"
        sprite = os.path.join(s.ASSETS_PATH,'enemy_1.png')
        self.image = pygame.transform.smoothscale(pygame.image.load(sprite), (s.BLOCK_SIZE, s.BLOCK_SIZE))
        super().__init__(xpos, ypos, basespeed=0, movespeed=3, direction=-1, hitbox=((4/5)*s.BLOCK_SIZE,(4/5)*s.BLOCK_SIZE), group=group)
        
    def animate(self):
        """
        handles animating the sprite
        """

        #rotate sprite 90 degrees every 25 frames
        self.anim_frames += 1
        if self.anim_frames == 25:
            self.image = pygame.transform.rotate(self.image,90 if self.direction == -1 else -90)
            self.anim_frames = 0

class Purple_Enemy(Enemy):
    def __init__(self, xpos, ypos, group):
        self.id = "2"
        self.sprites = []
        self.sprites.extend([pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH,'enemy_2-1.png')), (s.BLOCK_SIZE, 1.5*s.BLOCK_SIZE)),pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH,'enemy_2-2.png')), (s.BLOCK_SIZE, 1.5*s.BLOCK_SIZE))])
        self.image = self.sprites[0]
        super().__init__(xpos, ypos, basespeed=0, movespeed=3, direction=-1, hitbox=((4/5)*s.BLOCK_SIZE,(7/5)*s.BLOCK_SIZE), group=group)

    def animate(self):
        """
        handles animating the sprite
        """

        self.anim_frames += 0.1
        if self.anim_frames >= len(self.sprites):
            self.anim_frames = 0
        self.image = self.sprites[int(self.anim_frames)]

