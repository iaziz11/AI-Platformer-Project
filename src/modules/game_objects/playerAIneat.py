import pygame
import numpy as np
from modules.game_objects.player import Player
from modules import settings as s


class PlayerNEAT(Player):
    def __init__(self, xpos, ypos, group, obs_size):
        super().__init__(xpos, ypos, group)
        self.state_boxes_size = ()
        self.state_boxes = None
        self.obs_size = obs_size
        self.InitStateBoxes(self.obs_size[0], self.obs_size[1], s.BLOCK_SIZE)

    def InitStateBoxes(self, boxes_height, boxes_width, box_width):
        """
        Initializes state boxes so player can "see" its surroundings
        """

        self.state_boxes = np.ones((boxes_height, boxes_width)).astype(object)
        self.state_boxes_size = (boxes_width, boxes_height)
        start_y = self.rect.top - box_width*2
        for i in range(boxes_height):
            start_x = self.rect.left - box_width
            for j in range(boxes_width):
                self.state_boxes[i][j] = pygame.rect.Rect(start_x, start_y, box_width, box_width)
                start_x += box_width
            start_y += box_width

    def getInput(self, action):
        """
        Reads input and moves player accordingly
        """

        if not action:
            return

        # Moving right
        if action == 2 or action == 4:
            self.speed[0] += s.ACC if self.onGround else s.AIR_ACC
            if self.speed[0] > s.MAX_VEL:
                self.speed[0] = s.MAX_VEL

        # Moving left
        elif action == 1:
            self.speed[0] -= s.ACC if self.onGround else s.AIR_ACC
            if self.speed[0] < -s.MAX_VEL:
                self.speed[0] = -s.MAX_VEL

        # Not moving
        elif action == 0:
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
        if action == 3 or action == 4:
            if self.onGround:
                self.jump()
        else:
            if self.onGround:
                self.canJump = True

    def update(self, _, blockGroup, enemyGroup, powerUpGroup, __, action, key_press):
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
        self.getInput(action)

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
