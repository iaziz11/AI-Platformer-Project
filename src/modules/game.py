import sys, pygame, os, time
import math
import json, pickle
import numpy as np
import modules.rl.agent as agent
from modules.misc.helper import plot
from modules.misc import button
from modules import settings as s
from modules.game_objects import blocks, enemies, player, playerAIneat, playerAIrl
from modules.levelCreator import levelCreator
from modules.NEAT.neat import Neat 
from modules.NEAT.draw_net import draw
import config

#init pygame
pygame.init()

#init joystick if one is plugged in
joystick = None
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    s.JOY = True

class Game():
    def __init__(self, isAI, autoReset, timeOut, AItype=None,FPS=None):
        #init screen and game vars
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        s.WIDTH = self.screen.get_width()
        s.HEIGHT = self.screen.get_height()
        s.SCROLL_WIDTH = 0.5*s.WIDTH
        s.BLOCK_SIZE = round(s.WIDTH, -2)/25
        s.JUMP_SPEED = round(s.HEIGHT/30)
        s.GRAVITY = round((1/16)*s.JUMP_SPEED)
        #init fonts
        pygame.font.init()
        self.font = pygame.font.SysFont('sans-serif', int(s.WIDTH*0.05))
        #init images
        self.background = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH,'bg.png')), (s.WIDTH,s.HEIGHT))
        self.main_menu_screen = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH,'main_menu_screen.png')), (s.WIDTH,s.HEIGHT))
        self.pause_screen = pygame.transform.smoothscale(pygame.image.load(os.path.join(s.ASSETS_PATH,'pause_screen.png')), (s.WIDTH*0.8,s.HEIGHT*0.7)) 
        self.name_splash = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "pause_screen.png"))), (s.WIDTH*0.4, s.HEIGHT*0.1))   
        #colors
        self.black = 0, 0, 0
        self.blue = 0, 0, 255
        self.white = 255, 255, 255
        self.green = 0, 255, 0
        self.red = 255, 0, 0
        #init clock
        self.clock = pygame.time.Clock()
        #level creator
        self.levelCreator = levelCreator(self.screen, self.font)
        #init groups
        self.button_group = pygame.sprite.Group()
        self.block_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.player_group = pygame.sprite.Group()
        self.power_up_group = pygame.sprite.Group()
        #bools
        self.done = False
        self.paused = False
        self.choosingLevel = False
        self.selectAlgo = False
        self.won = False
        self.isAI = isAI
        self.AItype = AItype
        #misc
        self.timeOut = timeOut
        self.FPS = FPS
        self.autoReset = autoReset
        self.tracking_block = None
        self.reset_frames = 0
        self.obs_size = (5,5)
        self.startTime = 0
        self.mode = 0
        self.model_name = ""
        self.button_width = self.screen.get_width()*0.5
        self.button_height = self.screen.get_height()*0.1
        self.cur_page = 1
        self.pages = 1
        self.over_char = 0

    def loadlevel(self, level_path):
        """
        loads all map objects from level_path
        """

        #load json
        with open(level_path) as l:
            a = json.load(l)['level']

        #reset all groups
        self.enemy_group.empty()
        self.player_group.empty()
        self.block_group.empty()
        self.power_up_group.empty()

        height = len(a)-1
        width = len(a[0])
        idx = 0
        flag = False
        while height-idx >= 0:
            for j in range(width):
                match a[height-idx][j]:
                    case ' ':
                        pass
                    case 'f':
                        #floor block
                        b = blocks.Floor(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.block_group)
                    case 'b':
                        #brick block
                        b = blocks.Brick(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.block_group)
                    case 's':
                        #spawn block
                        b = blocks.Spawn_Block(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.block_group)
                    case '1':
                        #enemy 1
                        e = enemies.Red_Enemy(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.enemy_group)
                    case '2':
                        #enemy 2
                        e = enemies.Purple_Enemy(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.enemy_group)
                    case 'p':
                        #player
                        if self.isAI:
                            if self.AItype == 0:
                                p = playerAIrl.PlayerRL(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.player_group, self.obs_size)
                            elif self.AItype == 1:
                                p = playerAIneat.PlayerNEAT(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.player_group, self.obs_size)
                        else:
                            p = player.Player(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1), self.player_group)
                    case 'x':
                        #flag
                        if not flag:
                            x = blocks.Flag(j*s.BLOCK_SIZE,s.HEIGHT-s.BLOCK_SIZE*(idx+1)-(8*s.BLOCK_SIZE), self.block_group)
                            flag = True
                    case _:
                        raise Exception(f"Invalid map object: please check {level_path}")
            idx += 1

        self.findFurthestBlock()
        if self.timeOut is not None:
            self.startTime = time.time()

    def checkScroll(self):
        """
        iterates over the position of all players and checks to see if the screen should be scrolling 
        """

        for p in self.player_group:
            if p.rect.right >= s.SCROLL_WIDTH:
                return
        s.SCROLLING = False

    def findFurthestBlock(self):
        """
        picks block furthest to the left to use as a reference to see how far player has traveled
        """

        min = math.inf
        for b in self.block_group:
            if b.rect.left < min and isinstance(b, blocks.Floor):
                self.tracking_block = b
                min = b.rect.left

    def checkDead(self):
        """
        iterates over the status of all players; if all players are dead, the level resets
        """
        gameOver = True
        won = False

        for p in self.player_group:
            if p.rect.bottom > s.HEIGHT:
                p.died("Fell off screen")
            if p.isAlive:
                gameOver = False
            if p.won:
                won = True

        return gameOver, won

    def getState(self):
        """
        returns the state of the game
        """
        obs_size = self.obs_size
        state = np.zeros((obs_size[0],obs_size[1]))
        bg = self.block_group
        pg = self.player_group
        pug = self.power_up_group
        eg = self.enemy_group

        for p in pg:
            for i in range(obs_size[0]):
                for j in range(obs_size[1]):
                    cur_obj = None
                    #power-ups
                    for pu in pug:
                        if p.state_boxes[i][j].collidepoint(pu.rect.center):
                            cur_obj = 1
                    #blocks
                    for b in bg:
                        if p.state_boxes[i][j].collidepoint(b.rect.center):
                            if isinstance(b, blocks.Flag):
                                cur_obj = 2
                            elif isinstance(b, blocks.Floor):
                                cur_obj = 3
                            elif isinstance(b, blocks.Spawn_Block):
                                if not b.spawned:
                                    cur_obj = 4
                                else:
                                    cur_obj = 5
                            elif isinstance(b, blocks.Brick):
                                cur_obj = 6
                    #enemies
                    for e in eg:
                        if p.state_boxes[i][j].collidepoint(e.rect.center):
                            if isinstance(e, enemies.Purple_Enemy):
                                cur_obj = 7
                            elif isinstance(e, enemies.Red_Enemy):
                                cur_obj = 8
                    #player
                    for p in pg:
                        if p.state_boxes[i][j].collidepoint(p.rect.center):
                            cur_obj = 9
                    if cur_obj:
                        state[i][j] = cur_obj
                    else:
                        state[i][j] = 0
            a = list(np.concatenate(state).flat)
            if p.speed is not None:
                a.extend([p.speed[0], p.speed[1]])
            else:
                a.extend([0,0])
            return a
        return None

    def checkEnemies(self):
        """
        activates an enemy if it is close enough to the player
        """
        for e in self.enemy_group:
            for p in self.player_group:
                if e.rect.left - (s.WIDTH - self.tracking_block.rect.left) <= s.BLOCK_SIZE:
                    e.basespeed = e.movespeed

    def playGame(self, action=None, msg=None):

        """
        play one frame of the game
        """
        if self.FPS is not None:
            self.clock.tick(self.FPS)

        key_press = [0,0,0]
        #handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYUP:
                if not self.isAI:
                    if event.key == pygame.K_ESCAPE:
                        self.paused = True
                        return
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            key_press[0] = 1
        if keys[pygame.K_d]:
            key_press[1] = 1
        if keys[pygame.K_SPACE]:
            key_press[2] = 1
        #update groups
        self.player_group.update(joystick, self.block_group, self.enemy_group, self.power_up_group, self.tracking_block, action, key_press)
        self.enemy_group.update(self.block_group, self.enemy_group, self.player_group)
        self.power_up_group.update(self.block_group)
        self.block_group.update(self.player_group, self.enemy_group, self.power_up_group)
        
        
        #draw screen
        self.screen.blit(self.background, (0,0))
        self.player_group.draw(self.screen)
        self.enemy_group.draw(self.screen)
        self.power_up_group.draw(self.screen)
        self.block_group.draw(self.screen)
        if msg is not None:
            textRect = msg.get_rect()
            textRect.topright = (s.WIDTH, 0)
            self.screen.blit(msg, textRect)
        pygame.display.flip()

        self.checkScroll()
        self.checkEnemies()
        self.done, self.won = self.checkDead()
    
        if self.timeOut is not None:
            if time.time()-self.startTime >= self.timeOut:
                self.done = True

        if self.isAI:
            if self.AItype == 0:
                a = []
                for p in self.player_group:
                    a.extend([p.reward, self.done, p.rect.left+(-self.tracking_block.rect.left)])
                    return a[0], a[1], a[2]
            elif self.AItype == 1:
                for p in self.player_group:
                    a = p.rect.left+(-self.tracking_block.rect.left)
                    return a if a >= 0 else 0
        
#menu displays

    def loadButtons(self, buttons):
        """
        load all buttons into button group
        """
        self.button_group.empty()
        for i in buttons:
            self.button_group.add(i)
        
    def checkButtons(self, coords):
        """
        check if any buttons were pressed
        """
        clicked = False
        ret = None
        for b in self.button_group:
            if b.rect.collidepoint(coords):
                ret = b.activate()
                clicked = True
        return ret, clicked

    def mainScreen(self):
        """
        main menu screen
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    mode, clicked = self.checkButtons(pos)
                    if clicked:
                        self.mode = mode
                        return


            self.screen.blit(self.main_menu_screen, (0,0))
            self.button_group.draw(self.screen)
            for i in self.button_group:
                self.screen.blit(i.text, i.textRect)
            pygame.display.flip()

    def pauseMenu(self):
        """
        pause menu
        """
        self.clock.tick(s.MENU_FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.paused = False
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                ret, clicked = self.checkButtons(pos)
                if clicked:
                    self.mode = ret
                    self.paused = False
                    self.done = True
                    return
        
        self.screen.blit(self.pause_screen, (s.WIDTH*0.1, s.HEIGHT*0.15))
        self.button_group.draw(self.screen)
        for i in self.button_group:
            self.screen.blit(i.text, i.textRect)
        pygame.display.flip()

    def trainAIMenu(self, action):
        """
        menu to choose which algorithm you want to train or test
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    ret, clicked = self.checkButtons(pos)
                    if clicked:
                        self.AItype = ret
                        return

            self.screen.fill((136,158,181))
            self.screen.blit(pygame.transform.smoothscale(self.pause_screen,(s.WIDTH*0.9, s.HEIGHT*0.8)), (s.WIDTH*0.05, s.HEIGHT*0.05))
            self.button_group.draw(self.screen)
            for i in self.button_group:
                    self.screen.blit(i.text, i.textRect)
            if action == 0:
                msg = self.font.render("Pick an algorithm to train with:", True, self.black, None)
            else:
                msg = self.font.render("Pick an algorithm to test:", True, self.black, None)
            textRect = msg.get_rect()
            textRect.center = (s.WIDTH*0.5, s.HEIGHT*0.1)
            self.screen.blit(msg, textRect)
            pygame.display.flip()

    def selectLevel(self):
        """
        menu to select a level
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    ret, clicked = self.checkButtons(pos)
                    if clicked and isinstance(ret, str):
                        self.choosingLevel = False
                        self.cur_page = 1
                        return ret
                    elif clicked and ret != 0:
                        if self.cur_page + ret > 0 and self.cur_page + ret <= self.pages:
                            self.cur_page += ret
                        for i in self.button_group:
                            if isinstance(i, button.stringButton):
                                self.button_group.remove(i)
                    elif clicked and ret == 0:
                        self.mode = 0
                        return None

            self.screen.fill((136,158,181))
            self.screen.blit(pygame.transform.smoothscale(self.pause_screen,(s.WIDTH*0.9, s.HEIGHT*0.8)), (s.WIDTH*0.05, s.HEIGHT*0.05))
            levelPath = os.path.join(".", "levels")
            levels = self.getLevels(levelPath)
            self.pages = math.ceil(len(levels)/6)
            
            for idx, l in enumerate(levels):
                if idx < (self.cur_page-1)*6:
                    continue
                if idx >= self.cur_page*6:
                    continue
                b = button.stringButton((self.screen.get_width()*0.5, self.screen.get_height()*0.2 + self.button_height*(idx%6)), self.font, l[:-5], (self.button_width, self.button_height),os.path.join(levelPath, l))
                self.button_group.add(b)
            if len(self.button_group) <= 3:
                msg1 = self.font.render("No levels yet", True, self.black, None)
                rect1 = msg1.get_rect()
                rect1.center = (s.WIDTH/2, s.HEIGHT*0.4)
                msg2 = self.font.render("Please create a level from the main menu", True, self.black)
                rect2 = msg2.get_rect()
                rect2.top = rect1.bottom
                rect2.centerx = s.WIDTH/2
                self.screen.blit(msg1, rect1)
                self.screen.blit(msg2, rect2)


            self.button_group.draw(self.screen)
            for i in self.button_group:
                    self.screen.blit(i.text, i.textRect)
            
            selectMsg = self.font.render("Select a level", True, self.black)
            msgBox = selectMsg.get_rect()
            msgBox.center = (s.WIDTH*0.5, s.HEIGHT*0.10)
            self.screen.blit(selectMsg, msgBox)
            pygame.display.flip()

    def getLevels(self,path):
        """
        returns a list of levels from path
        """
        if not os.path.exists(path):
                os.makedirs(path)
        files = os.listdir(path)
        for f in files:
            if not f.endswith('.json'):
                files.remove(f)
        return files

    def getModels(self,path):
        """
        returns a list of models from path
        """
        if not os.path.exists(path):
                os.makedirs(path)
        files = os.listdir(path)
        for f in files:
            if not f.endswith('.pth') and not f.endswith('.pkl'):
                files.remove(f)
        return files

    def trainModel(self, path):
        """
        train model
        """
        self.isAI = True
        #rl model
        if self.AItype == 0:
            rlAgent = agent.Agent()
            plot_scores = []
            plot_avg_scores = []
            tot_score = 0
            best_score = 0
            self.loadlevel(path)
            self.FPS = None
            self.timeOut = config.RL_TIMEOUT
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_ESCAPE:
                            return
                old_state = self.getState()
                action = rlAgent.getAction(old_state)
                msg = self.font.render(f"Frame #{rlAgent.total_frames}/{config.FRAMES_TO_TRAIN}", True, self.black, None)
                reward, gameOver, score = self.playGame(action, msg)
                new_state = self.getState()
                rlAgent.trainShortMem(old_state, action, reward, new_state, gameOver)
                rlAgent.remember(old_state, action, reward, new_state, gameOver)
                
                if gameOver:
                    #train on long memory
                    rlAgent.num_games += 1
                    rlAgent.trainLongMem()

                    if score > best_score:
                        best_score = score
                    
                    rlAgent.last_ten.append(score)

                    print(f'Game: {rlAgent.num_games}, Score: {score}, Frames trained: {rlAgent.total_frames}')
                    if len(rlAgent.last_ten) >= 10:
                        print("Last 10 Games Average: ", sum(rlAgent.last_ten)/10)
                    
                    plot_scores.append(score)
                    tot_score += score
                    mean_score = tot_score / rlAgent.num_games
                    plot_avg_scores.append(mean_score)
                    self.loadlevel(path)

                rlAgent.total_frames += 1

                #save checkpoint
                if rlAgent.total_frames % 100_000 == 0:
                    model_name = f'{self.model_name}_{rlAgent.total_frames}_frames.pth'
                    rlAgent.model.save(model_name)
                
                #finish training
                if rlAgent.total_frames >= config.FRAMES_TO_TRAIN:
                    print("Done training!")
                    print(f"The model can be found in Python Project/models/{self.model_name}.pth")
                    self.model_name = ""
                    return
        #NEAT algorithm
        elif self.AItype == 1:
            self.timeOut = config.NEAT_TIMEOUT
            self.FPS = None
            neat = Neat(27,5,config.NUM_CLIENTS)
            neat.evolve()
            for i in range(config.NUM_GENERATIONS):
                cnum = 0
                for c in neat.clients.getData():
                    score = 0
                    self.loadlevel(path)
                    cnum += 1
                    while not self.done:
                        msg = self.font.render(f"Client #{cnum}/{config.NUM_CLIENTS}, Generation #{i+1}/{config.NUM_GENERATIONS}", True, self.black, None)
                        for event in pygame.event.get():
                            if event.type == pygame.KEYUP:
                                if event.key == pygame.K_ESCAPE:
                                    return
                        input = self.getState()
                        output = c.calculate(input)
                        move = np.argmax(output)
                        score = self.playGame(move, msg)
                    self.done = False
                    c.setScore(score)
                neat.evolve()
                neat.printSpecies()
            self.timeOut = None
            if not os.path.exists("./clients"):
                os.makedirs("./clients")
            with open(f"./clients/{self.model_name}.pkl", "wb") as out:
                neat.species.getData().sort(key=lambda x: x.score, reverse=True)
                pickle.dump(neat.species.getData()[0].representative, out, 0)
            self.model_name = ""
            print("All generations complete!")
            print(f"The representative of the highest performing species can be found in Python Project/clients/{self.model_name}.pkl")
            return

    def levelDone(self):
        """
        show whether you won or lost
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        return
            
            if self.won:
                msg1 = self.font.render("You Won!",True,self.green,None)
            else:
                msg1 = self.font.render("You Lost!",True,self.red,None)

            msg2 = self.font.render("Press Space to Return to Menu",True,self.black,None)

            rect1 = msg1.get_rect()
            rect2 = msg2.get_rect()

            rect1.center = (s.WIDTH/2,s.HEIGHT*0.10)
            rect2.top = rect1.bottom
            rect2.centerx = s.WIDTH/2

            self.screen.blit(msg1, rect1)
            self.screen.blit(msg2, rect2)
            pygame.display.flip()

    def selectAIAction(self):
        """
        menu to choose whether you want to train or test an AI 
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    ret, clicked = self.checkButtons(pos)
                    if clicked:
                        return ret
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        return -1
                if event.type == pygame.QUIT:
                    sys.exit()

            self.screen.fill((136,158,181))
            self.screen.blit(pygame.transform.smoothscale(self.pause_screen,(s.WIDTH*0.9, s.HEIGHT*0.8)), (s.WIDTH*0.05, s.HEIGHT*0.05))
            self.button_group.draw(self.screen)
            for i in self.button_group:
                self.screen.blit(i.text, i.textRect)
            msg = self.font.render("Select an action", False, self.black)
            msgBox = msg.get_rect()
            msgBox.center = (s.WIDTH*0.5,s.HEIGHT*0.1)
            self.screen.blit(msg, msgBox)
            pygame.display.flip()

    def chooseModel(self):
        """
        menu to choose a model to test
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    ret, clicked = self.checkButtons(pos)
                    if clicked and isinstance(ret, str):
                        self.choosingLevel = False
                        self.cur_page = 1
                        return ret
                    elif clicked and ret != 0:
                        if self.cur_page + ret > 0 and self.cur_page + ret <= self.pages:
                            self.cur_page += ret
                        for i in self.button_group:
                            if isinstance(i, button.stringButton):
                                self.button_group.remove(i)
                    elif clicked and ret == 0:
                        self.mode = 0
                        return None

            self.screen.fill((136,158,181))
            self.screen.blit(pygame.transform.smoothscale(self.pause_screen,(s.WIDTH*0.9, s.HEIGHT*0.8)), (s.WIDTH*0.05, s.HEIGHT*0.05))
            if self.AItype == 0:
                modelPath = os.path.join(".", "model")
            else:
                modelPath = os.path.join(".", "clients")

            levels = self.getModels(modelPath)
            self.pages = math.ceil(len(levels)/6)
            
            for idx, l in enumerate(levels):
                if idx < (self.cur_page-1)*6:
                    continue
                if idx >= self.cur_page*6:
                    continue
                b = button.stringButton((self.screen.get_width()*0.5, self.screen.get_height()*0.2 + self.button_height*(idx%6)), self.font, l[:-4], (self.button_width, self.button_height),os.path.join(modelPath, l))
                self.button_group.add(b)
            if len(self.button_group) <= 3:
                if self.AItype == 0:
                    msg1 = self.font.render("No models yet", True, self.black, None)
                else:
                    msg1 = self.font.render("No clients yet", True, self.black, None)
                rect1 = msg1.get_rect()
                rect1.center = (s.WIDTH/2, s.HEIGHT*0.4)
                msg2 = self.font.render("Please train an AI model/client first", True, self.black, None)
                rect2 = msg2.get_rect()
                rect2.top = rect1.bottom
                rect2.centerx = s.WIDTH/2
                self.screen.blit(msg1, rect1)
                self.screen.blit(msg2, rect2)


            self.button_group.draw(self.screen)
            for i in self.button_group:
                    self.screen.blit(i.text, i.textRect)
            selectMsg = self.font.render("Select a model/client", True, self.black)
            msgBox = selectMsg.get_rect()
            msgBox.center = (s.WIDTH*0.5, s.HEIGHT*0.10)
            self.screen.blit(selectMsg, msgBox)

            pygame.display.flip()

    def nameModel(self):
        """
        menu to name a model
        """
        while True:
            self.clock.tick(s.MENU_FPS)
            self.screen.fill((136,158,181))
            color = (255,255,255)
            input_rect = pygame.Rect(0,0, self.name_splash.get_width()*0.8, self.name_splash.get_height()*0.7)
            input_rect.center = (s.WIDTH/2, s.HEIGHT/2)
            name_rect = self.name_splash.get_rect()
            name_rect.center = (s.WIDTH/2, s.HEIGHT/2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
        
                    # Check for backspace
                    if event.key == pygame.K_BACKSPACE:
                        # get text input from 0 to -1 i.e. end.
                        self.model_name = self.model_name[:-1]
                        if self.over_char > 0:
                            self.over_char -= 1
                    elif event.key == pygame.K_RETURN:
                        if len(self.model_name) > 0:
                            return
                    # Unicode standard is used for string
                    # formation
                    elif len(self.model_name) < 20 and event.key in s.LEGAL_CHARS:
                        self.model_name += event.unicode
                
            self.screen.blit(self.name_splash, name_rect)
            
            pygame.draw.rect(self.screen, color, input_rect)
            text_surface = self.font.render(self.model_name[self.over_char:], True, (0,0,0))
            text_rect = text_surface.get_rect()
            if text_rect.width > input_rect.width-40:
                self.over_char += 1
                text_surface = self.font.render(self.model_name[self.over_char:], True, (0,0,0))
                text_rect = text_surface.get_rect()
            text_rect.x = input_rect.x+20
            text_rect.y = input_rect.y
            # render at position stated in arguments
            self.screen.blit(text_surface, text_rect)
            
            # display.flip() will update only a portion of the
            # screen to updated, not full area
            nameMsg = self.font.render("Name your model", False, self.black)
            msgBox = nameMsg.get_rect()
            msgBox.center = (s.WIDTH*0.5, s.HEIGHT*0.2)
            self.screen.blit(nameMsg, msgBox)
            pygame.display.flip()
