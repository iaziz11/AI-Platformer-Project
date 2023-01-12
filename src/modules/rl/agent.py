import torch
import random, math
from collections import deque
import numpy as np
import config
from modules.game_objects import enemies
from modules.game_objects import blocks
from modules.rl.model import Linear_QNet, QTrainer
from modules.misc.helper import plot

MAX_MEM = 100_000
BATCH_SIZE = 1000
LR = config.LR

class Agent():
    def __init__(self):
        self.num_games = 0
        self.eps = 0 #randomness
        self.gamma = 0.9 #discount rate
        self.memory = deque(maxlen=MAX_MEM)
        self.last_ten = deque(maxlen=10)
        self.model = Linear_QNet(27, 16, 5)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.total_frames = 0
        self.inital_eps = 1
        self.final_eps = 0.01
        self.epsilon_decay = 250_000
                
    def remember(self, state, action, reward, next_state, game_over):
        """
        add info into memory
        """
        self.memory.append((state, action, reward, next_state, game_over))

    def trainLongMem(self):
        """
        training on memory after game over
        """
        if len(self.memory) > BATCH_SIZE:
            mini_batch = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_batch = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_batch)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def trainShortMem(self, state, action, reward, next_state, game_over):
        """
        train on current state
        """
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def getAction(self, state):
        """
        get action from either random action generator or from neural network
        """
        #random moves
        self.eps = self.final_eps + (self.inital_eps - self.final_eps)*math.exp(-1. * self.total_frames / self.epsilon_decay)
        final_move = [0, 0, 0, 0, 0] #nop, left, right, jump, up_right
        if random.random() < self.eps:
            move = random.randint(0,len(final_move)-1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move




