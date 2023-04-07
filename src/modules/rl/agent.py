import torch
import random
import math
from collections import deque
import config
from modules.rl.model import Linear_QNet, QTrainer

MAX_MEM = 100_000
BATCH_SIZE = 1000
LR = config.LR


class Agent():
    def __init__(self):
        self.num_games = 0
        # Randomness
        self.eps = 0
        # Discount rate
        self.gamma = 0.9
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
        Write into memory
        """

        self.memory.append((state, action, reward, next_state, game_over))

    def trainLongMem(self):
        """
        Training on memory after game over
        """

        if len(self.memory) > BATCH_SIZE:
            mini_batch = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_batch = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_batch)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def trainShortMem(self, state, action, reward, next_state, game_over):
        """
        Train on current state
        """

        self.trainer.train_step(state, action, reward, next_state, game_over)

    def getAction(self, state):
        """
        Get action from either random action generator or from neural network
        """

        # Random moves
        self.eps = self.final_eps + (self.inital_eps - self.final_eps)*math.exp(-1. * self.total_frames / self.epsilon_decay)
        # nop, left, right, jump, up_right
        final_move = [0, 0, 0, 0, 0]
        if random.random() < self.eps:
            move = random.randint(0, len(final_move)-1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move
