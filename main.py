import sys
sys.path.append('./src')
from src.modules.game import Game
from modules.misc import button
import pygame
import pickle
import torch
import numpy as np
from modules.rl.model import Linear_QNet

env = Game(isAI=False, autoReset=False, timeOut=None, AItype=None, FPS=60)

# Main loop
while True:

    # Get events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            env.checkButtons(pos)

    match env.mode:
        # Main menu
        case 0:
            env.model_name = ""
            buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.5), env.font, "Play Game", (env.button_width, env.button_height), 1),
                       button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.6), env.font, "Create Level", (env.button_width, env.button_height), 2),
                       button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.7), env.font, "AI Menu", (env.button_width, env.button_height), 3),
                       button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.8), env.font, "Quit", (env.button_width, env.button_height), 4)]
            env.loadButtons(buttons)

            # Show main menu screen
            env.mainScreen()

        # Play level menu
        case 1:
            buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.925), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                       button.intButton((env.screen.get_width()*0.7, env.screen.get_height()*0.925), env.font, ">", (env.button_width*0.2, env.button_height), 1),
                       button.intButton((env.screen.get_width()*0.3, env.screen.get_height()*0.925), env.font, "<", (env.button_width*0.2, env.button_height), -1)]
            env.loadButtons(buttons)

            path = env.selectLevel()
            if path is None:
                continue

            env.loadlevel(path)

            buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.45), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                       button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.55), env.font, "Quit", (env.button_width, env.button_height), 4)]
            env.loadButtons(buttons)

            # Play game until game over
            env.done = False
            while not env.done:
                if env.paused:
                    env.pauseMenu()
                else:
                    env.playGame()

            # If done, show finish screen
            if env.mode == 1:
                env.levelDone()
                env.mode = 0

        # Level creator
        case 2:
            # Load level creator
            env.levelCreator.active = True
            while env.levelCreator.active:
                env.levelCreator.show()
            env.mode = 0

        # AI menu
        case 3:
            buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.4), env.font, "Train AI", (env.button_width, env.button_height), 0),
                       button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.5), env.font, "Test AI", (env.button_width, env.button_height), 1)]
            env.loadButtons(buttons)

            action = env.selectAIAction()

            # If esc is pressed, return
            if action == -1:
                env.mode = 0
                continue

            # Train AI
            elif action == 0:
                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.4), env.font, "Reinforcement Learning", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.5), env.font, "NEAT", (env.button_width, env.button_height), 1)]
                env.loadButtons(buttons)

                env.trainAIMenu(action)

                env.nameModel()

                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.925), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.7, env.screen.get_height()*0.925), env.font, ">", (env.button_width*0.2, env.button_height), 1),
                           button.intButton((env.screen.get_width()*0.3, env.screen.get_height()*0.925), env.font, "<", (env.button_width*0.2, env.button_height), -1)]
                env.loadButtons(buttons)

                level_path = env.selectLevel()
                if level_path is None:
                    continue

                env.trainModel(level_path)
                env.isAI = False
                env.FPS = 60
                env.mode = 0

            # Test AI
            elif action == 1:
                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.4), env.font, "Reinforcement Learning", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.5), env.font, "NEAT", (env.button_width, env.button_height), 1)]
                env.loadButtons(buttons)
                env.trainAIMenu(action)
                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.925), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.7, env.screen.get_height()*0.925), env.font, ">", (env.button_width*0.2, env.button_height), 1),
                           button.intButton((env.screen.get_width()*0.3, env.screen.get_height()*0.925), env.font, "<", (env.button_width*0.2, env.button_height), -1)]
                env.loadButtons(buttons)
                model_path = env.chooseModel()
                if model_path is None:
                    continue

                # Load reinforcement learning model
                if env.AItype == 0:
                    model = Linear_QNet(27, 16, 5)
                    model.load_state_dict(torch.load(model_path))
                    model.eval()

                # Load NEAT client
                elif env.AItype == 1:
                    file = open(model_path, 'rb')
                    client = pickle.load(file)

                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.925), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.7, env.screen.get_height()*0.925), env.font, ">", (env.button_width*0.2, env.button_height), 1),
                           button.intButton((env.screen.get_width()*0.3, env.screen.get_height()*0.925), env.font, "<", (env.button_width*0.2, env.button_height), -1)]
                env.loadButtons(buttons)

                level_path = env.selectLevel()
                if level_path is None:
                    continue

                env.isAI = True
                env.loadlevel(level_path)

                env.done = False
                buttons = [button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.45), env.font, "Return to Menu", (env.button_width, env.button_height), 0),
                           button.intButton((env.screen.get_width()*0.5, env.screen.get_height()*0.55), env.font, "Quit", (env.button_width, env.button_height), 4)]
                env.loadButtons(buttons)

                while not env.done:
                    # Test rl model
                    if env.AItype == 0:
                        state = env.getState()
                        # nop, left, right, jump, up_right
                        final_move = [0, 0, 0, 0, 0]
                        state0 = torch.tensor(state, dtype=torch.float)
                        prediction = model(state0)
                        move = torch.argmax(prediction).item()
                        final_move[move] = 1
                        env.playGame(final_move)
                    
                    # Test NEAT client
                    if env.AItype == 1:
                        state = env.getState()
                        out = client.calculate(state)
                        move = np.argmax(out)
                        env.playGame(move)
                
                env.isAI = False
                env.mode = 0

        # Quit
        case 4:
            sys.exit()