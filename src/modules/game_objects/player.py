import pygame
import os
import numpy as np
from modules.game_objects.blocks import Brick, Spawn_Block, Flag
from modules.game_objects.power_ups import Mushroom
from modules import settings as s


class Player(pygame.sprite.Sprite):
    def __init__(self, xpos, ypos, group):
        super().__init__(group)
        self.id = "p"
        self.anim_small = [pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_walking_1.png')), (s.BLOCK_SIZE, s.BLOCK_SIZE)), pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_walking_2.png')), (s.BLOCK_SIZE, s.BLOCK_SIZE))]
        self.anim_small_jump = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_jumping.png')), (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.anim_big = [pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_big_walking_1.png')), (s.BLOCK_SIZE, 2*s.BLOCK_SIZE)), pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_big_walking_2.png')), (s.BLOCK_SIZE, 2*s.BLOCK_SIZE))]
        self.anim_big_jump = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_big_jumping.png')), (s.BLOCK_SIZE, 2*s.BLOCK_SIZE))
        self.anim_small_stand = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player.png')), (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.anim_big_stand = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_big.png')), (s.BLOCK_SIZE, 2*s.BLOCK_SIZE))
        self.anim_invincible = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH, 'player_invin.png')), (s.BLOCK_SIZE, s.BLOCK_SIZE))
        self.image = self.anim_small_stand
        self.rect = self.image.get_rect()
        self.rect.topleft = (xpos, ypos)
        self.hitbox = pygame.Rect(0, 0, (4/5)*s.BLOCK_SIZE, (4/5)*s.BLOCK_SIZE)
        self.hitbox.midbottom = self.rect.midbottom
        self.speed = np.array([0.0, 0.0])
        self.canJump = False
        self.onGround = False
        self.isAlive = True
        self.isBig = False
        self.faceRight = True
        self.iframes = 0
        self.anim_frames = 0
        self.won = False

    def checkHitboxCollide(self, sprite, group):
        """
        Return a list of sprites in :group: that collide with :sprite:
        """

        s = []
        for i in group:
            if sprite.hitbox.colliderect(i.hitbox):
                s.append(i)
        return s

    def getInput(self, joystick, action):
        """
        Reads input and moves player accordingly
        """

        RIGHT = False
        LEFT = False
        JUMP = False
        # Read from joystick if one if plugged in
        if s.JOY:
            axis = joystick.get_axis(0)
            if axis > 0.5:
                RIGHT = True
            elif axis < 0.5:
                LEFT = True
            if joystick.get_button(1):
                JUMP = True
        # Otherwise, read from keyboard
        else:
            if action[0] == 1:
                LEFT = True
            elif action[1] == 1:
                RIGHT = True
            if action[2] == 1:
                JUMP = True

        # Moving right
        if RIGHT:
            self.speed[0] += s.ACC if self.onGround else s.AIR_ACC
            if self.speed[0] > s.MAX_VEL:
                self.speed[0] = s.MAX_VEL

        # Moving left
        elif LEFT:
            self.speed[0] -= s.ACC if self.onGround else s.AIR_ACC
            if self.speed[0] < -s.MAX_VEL:
                self.speed[0] = -s.MAX_VEL

        # Not moving
        else:
            if self.speed[0] > 0:
                if self.speed[0] - s.DECEL_RATE < 0:
                    self.speed[0] = 0
                else:
                    self.speed[0] -= s.DECEL_RATE
            elif self.speed[0] < 0:
                if self.speed[0] + s.DECEL_RATE > 0:
                    self.speed[0] = 0
                else:
                    self.speed[0] += s.DECEL_RATE

        # Handle jumps
        if JUMP:
            if self.onGround:
                self.jump()
        else:
            if self.onGround:
                self.canJump = True

    def died(self, _):
        """
        Called when player dies
        """

        self.isAlive = False

    def jump(self):
        """
        Handles jumps
        """

        if not self.canJump:
            return
        self.canJump = False
        self.speed[1] = -s.JUMP_SPEED

    def big(self):
        """
        Used when the player receives a power-up mushroom
        """
        if self.isBig:
            return

        # Load new image
        self.image = self.anim_big_stand

        # Save old rect coordinates and move new rect there
        coords = (self.rect.left, self.rect.top-s.BLOCK_SIZE)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords

        # Create new larger hitbox
        self.hitbox = pygame.Rect(0, 0, (4/5)*s.BLOCK_SIZE, (9/5)*s.BLOCK_SIZE)
        self.hitbox.midbottom = self.rect.midbottom

        self.isBig = True

    def small(self):
        """
        Used when a powered-up character takes damage
        """
        if not self.isBig:
            return

        # Set invincibility frames
        self.iframes = s.IFRAMES

        # Load new image
        self.image = self.anim_small_stand

        # Save old rect coordinates and move new rect there
        coords = (self.rect.left, self.rect.top+s.BLOCK_SIZE)
        self.rect = self.image.get_rect()
        self.rect.topleft = coords

        # Create new smaller hitbox
        self.hitbox = pygame.Rect(0, 0, (4/5)*s.BLOCK_SIZE, (4/5)*s.BLOCK_SIZE)
        self.hitbox.midbottom = self.rect.midbottom

        self.isBig = False

    def moveRectH(self, dx, other=None, left=False):
        """
        Wrapper for rect.move that also moves the hitbox horizontally
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
        Wrapper for rect.move that also moves the hitbox vertically
        """

        if other:
            if bottom:
                self.rect.bottom = other.top
            else:
                self.rect.top = other.bottom
        else:
            self.rect = self.rect.move(0, dy)

        self.hitbox.midbottom = self.rect.midbottom

    def horizontalMovement(self, blockGroup, enemyGroup, powerUpGroup):
        """
        Checks collisions after the player moves horizontally
        """

        # Check all relevant collisions
        collided_blocks = pygame.sprite.spritecollide(self, blockGroup, False)
        collided_enemies = self.checkHitboxCollide(self, enemyGroup)
        collided_power = pygame.sprite.spritecollide(self, powerUpGroup, False)

        # Check to see if player is within screen bounds
        if (self.rect.right >= s.SCROLL_WIDTH):
            s.SCROLLING = True
            s.SCROLLING_PLAYER = self
            self.moveRectH(-(self.rect.right-s.SCROLL_WIDTH))
        elif (self.rect.left < 0):
            self.moveRectH(-self.rect.left)
            self.speed[0] = 0

        # Handle power up collisions
        if len(collided_power) > 0:
            if isinstance(collided_power[0], Mushroom):
                self.big()
            collided_power[0].kill()

        # Handle block collisions
        if len(collided_blocks) > 0:
            if isinstance(collided_blocks[0], Flag):
                self.won = True
                self.died("Died: Got to end")

            if self.speed[0] < 0:
                self.speed[0] = 0
                self.moveRectH(0, collided_blocks[0].rect, True)
            else:
                self.speed[0] = 0
                self.moveRectH(0, collided_blocks[0].rect, False)

        # Handle enemy collisions
        if len(collided_enemies) > 0:
            if not self.isBig:
                if self.iframes == 0:
                    self.died("Hit enemy h")
            else:
                self.small()

    def verticalMovement(self, blockGroup, enemyGroup, powerUpGroup):
        """
        Checks collisions after the player moves vertically
        """

        bounce = False
        self.onGround = False

        # Check all relevant collisions
        collided_blocks = pygame.sprite.spritecollide(self, blockGroup, False)
        collided_enemies = self.checkHitboxCollide(self, enemyGroup)
        collided_power = pygame.sprite.spritecollide(self, powerUpGroup, False)

        # Handle block collisions
        if len(collided_blocks) > 0:
            if self.speed[1] >= 0:
                self.speed[1] = 0
                self.moveRectV(0, collided_blocks[0].rect, True)
                self.onGround = True
            else:
                self.moveRectV(0, collided_blocks[0].rect, False)
                self.speed[1] = 0
                if isinstance(collided_blocks[0], Brick):
                    collided_blocks[0].broken()
                if isinstance(collided_blocks[0], Spawn_Block):
                    collided_blocks[0].spawn(powerUpGroup)

        # Handle enemy collisions
        if len(collided_enemies) > 0:
            for i in collided_enemies:
                if self.speed[1] > 0:
                    self.moveRectV(0, collided_enemies[0].hitbox, True)
                    i.kill()
                    bounce = True
                else:
                    if not self.isBig:
                        if self.iframes == 0:
                            self.died("Hit enemy v")
                    else:
                        self.small()

        # Handle power up collisions
        if len(collided_power) > 0:
            if isinstance(collided_power[0], Mushroom):
                self.big()
            collided_power[0].kill()

        # If enemy was killed, bounce
        if bounce:
            self.speed[1] = -s.BOUNCE

    def animate(self):
        """
        Handles animating the sprite
        """

        if (self.iframes % 2) != 0:
            self.image = self.anim_invincible
            return

        if self.anim_frames >= len(self.anim_small):
            self.anim_frames = 0

        # If powered up
        if self.isBig:
            # If jumping
            if not self.onGround:
                if self.speed[0] >= 0:
                    self.image = self.anim_big_jump
                    self.faceRight = True
                    return
                elif self.speed[0] < 0:
                    self.image = pygame.transform.flip(self.anim_big_jump, True, False)
                    self.faceRight = False
                    return
            # If not jumping
            elif self.speed[0] > 0:
                self.image = self.anim_big[int(self.anim_frames)]
                self.anim_frames += 0.2
                self.faceRight = True
            elif self.speed[0] < 0:
                self.image = pygame.transform.flip(self.anim_big[int(self.anim_frames)], True, False)
                self.anim_frames += 0.2
                self.faceRight = False
            else:
                self.image = self.anim_big_stand if self.faceRight else pygame.transform.flip(self.anim_big_stand, True, False)
        # If not powered up
        else:
            # If jumping
            if not self.onGround:
                if self.speed[0] >= 0:
                    self.image = self.anim_small_jump
                    self.faceRight = True
                    return
                elif self.speed[0] < 0:
                    self.image = pygame.transform.flip(self.anim_small_jump, True, False)
                    self.faceRight = False
                    return
            # If not jumping
            elif self.speed[0] > 0:
                self.image = self.anim_small[int(self.anim_frames)]
                self.anim_frames += 0.2
                self.faceRight = True
            elif self.speed[0] < 0:
                self.image = pygame.transform.flip(self.anim_small[int(self.anim_frames)], True, False)
                self.anim_frames += 0.2
                self.faceRight = False
            else:
                self.image = self.anim_small_stand if self.faceRight else pygame.transform.flip(self.anim_small_stand, True, False)

    def update(self, joystick, blockGroup, enemyGroup, powerUpGroup, _, __, key_press):
        """
        Update all members of group
        """

        # If player is dead, stop updating
        if not self.isAlive:
            return

        # Update invincibility frames
        if self.iframes > 0:
            self.iframes -= 1

        # Get inputs
        self.getInput(joystick, key_press)

        # Change speed if the screen is scrolling
        if s.SCROLLING and (s.SCROLLING_PLAYER != self):
            self.moveRectH(-s.SCROLLING_PLAYER.speed[0])

        # Move horizontally
        self.moveRectH(self.speed[0])
        self.horizontalMovement(blockGroup, enemyGroup, powerUpGroup)

        # Constant downward acceleration
        self.speed[1] += s.GRAVITY

        # Move vertically
        self.moveRectV(self.speed[1])
        self.verticalMovement(blockGroup, enemyGroup, powerUpGroup)

        # Animate
        self.animate()
