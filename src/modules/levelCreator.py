from modules import settings as s
from modules.game_objects import player, blocks, enemies
import os, sys, json
import pygame

class Eraser(pygame.sprite.Sprite):
    def __init__(self, group) -> None:
         super().__init__(group)
         self.image = pygame.image.load(os.path.join(s.ASSETS_PATH, "eraser.png")).convert_alpha()
         self.rect = self.image.get_rect()



class levelCreator():
    def __init__(self, screen, font) -> None:
        self.screen = screen
        self.font = font
        self.active = False
        self.selected = None
        self.selected_obj = None
        self.isPlayer = False
        self.isFlag = False
        self.erasing = False
        self.naming = False
        self.fileName = ''
        self.over_char = 0
        self.trackingBlock = None
        self.collideBox = pygame.rect.Rect(0,0,s.BLOCK_SIZE,s.BLOCK_SIZE)
        self.background = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "level_creator_bg.png"))), (s.WIDTH, s.HEIGHT)) 
        self.select_splash = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "pause_screen.png"))), (s.WIDTH, s.HEIGHT*0.1))
        self.name_splash = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "pause_screen.png"))), (s.WIDTH*0.4, s.HEIGHT*0.3))
        self.outline = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "outline.png"))), (s.BLOCK_SIZE*1.2, s.BLOCK_SIZE*1.2))
        self.help_splash = pygame.transform.smoothscale((pygame.image.load(os.path.join(s.ASSETS_PATH, "pause_screen.png"))), (s.WIDTH*0.8, s.HEIGHT*0.8))
        self.samples = pygame.sprite.Group()
        self.placed = pygame.sprite.Group()
        self.player = player.Player(0,0,self.samples)
        self.brick = blocks.Brick(0,0,self.samples)
        self.floor = blocks.Floor(0,0,self.samples)
        self.spawn_block = blocks.Spawn_Block(0,0,self.samples)
        self.flag = blocks.Flag(0,0,self.samples)
        self.enemy1 = enemies.Red_Enemy(0,0,self.samples)
        self.enemy2 = enemies.Purple_Enemy(0,0,self.samples)
        self.eraser = Eraser(self.samples)

    def show(self):
        """
        display level creator
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] < self.select_splash.get_height():
                    for i in self.samples:
                        if i.rect.collidepoint(pos):
                            self.selected = type(i)
                            self.selected_obj = i

                            if self.selected == Eraser:
                                self.erasing = True
                            else:
                                self.erasing = False
                elif pos[1] >= self.select_splash.get_height()+s.BLOCK_SIZE*2:
                    if self.selected is not None:
                        new_x = int(pos[0]/s.BLOCK_SIZE)*s.BLOCK_SIZE
                        new_y = (pos[1]+(s.BLOCK_SIZE - pos[1]%s.BLOCK_SIZE))+(s.HEIGHT % s.BLOCK_SIZE)
                        self.collideBox.bottomleft = (new_x, new_y)
                        for i in self.placed:
                            if i.rect.colliderect(self.collideBox):
                                if self.erasing:
                                    self.placed.remove(i)
                                    if isinstance(i, player.Player):
                                        self.isPlayer = False
                                    if isinstance(i, blocks.Flag):
                                        self.isFlag = False
                                return
                        match self.selected:
                            case player.Player:
                                if not self.isPlayer:
                                    p = player.Player(0, 0, self.placed)
                                    p.rect.bottomleft = (new_x, new_y)
                                    self.isPlayer = True
                                    if self.trackingBlock is None or p.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = p
                            case blocks.Floor:
                                f = blocks.Floor(0, 0, self.placed)
                                f.rect.bottomleft = (new_x, new_y)
                                if self.trackingBlock is None or f.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = f
                            case blocks.Brick:
                                b = blocks.Brick(0, 0, self.placed)
                                b.rect.bottomleft = (new_x, new_y)
                                if self.trackingBlock is None or b.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = b
                            case blocks.Spawn_Block:
                                sb = blocks.Spawn_Block(0, 0, self.placed)
                                sb.rect.bottomleft = (new_x, new_y)
                                if self.trackingBlock is None or sb.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = sb
                            case blocks.Flag:
                                if not self.isFlag:
                                    fl = blocks.Flag(0, 0, self.placed)
                                    fl.rect.bottomleft = (new_x, new_y)
                                    self.isFlag = True
                                    if self.trackingBlock is None or fl.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = fl
                            case enemies.Red_Enemy:
                                e1 = enemies.Red_Enemy(0, 0, self.placed)
                                e1.rect.bottomleft = (new_x, new_y)
                                if self.trackingBlock is None or e1.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = e1
                            case enemies.Purple_Enemy:
                                e2 = enemies.Purple_Enemy(0, 0, self.placed)
                                e2.rect.bottomleft = (new_x, new_y)
                                if self.trackingBlock is None or e2.rect.left < self.trackingBlock.rect.left:
                                        self.trackingBlock = e2
                            case _:
                                pass

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    if self.trackingBlock is not None:
                        if self.trackingBlock.rect.left < 0:
                            for i in self.placed:
                                i.rect.move_ip(s.BLOCK_SIZE, 0)
                if event.key == pygame.K_RIGHT:
                        for i in self.placed:
                            i.rect.move_ip(-s.BLOCK_SIZE, 0)
                if event.key == pygame.K_s:
                    floor_placed = False
                    for i in self.placed:
                        if isinstance(i, blocks.Floor):
                            floor_placed = True
                    if self.isPlayer and self.isFlag and floor_placed:
                        self.save()
                if event.key == pygame.K_h:
                    self.helpMenu()
                if event.key == pygame.K_ESCAPE:
                    self.reset()
                    self.active = False
                    return
                                  
        for idx, i in enumerate(self.samples):
            if not isinstance(i, blocks.Flag) and not isinstance(i, enemies.Purple_Enemy):
                i.image = pygame.transform.smoothscale(i.image, (s.BLOCK_SIZE, s.BLOCK_SIZE))
            else:
                i.image = i.image.subsurface((0, 0, s.BLOCK_SIZE, s.BLOCK_SIZE))
            i.rect.inflate_ip(i.rect.width - s.BLOCK_SIZE, i.rect.height - s.BLOCK_SIZE)
            i.rect.centerx = (s.WIDTH/(len(self.samples)+1))*(idx+1)
            i.rect.centery = s.HEIGHT*0.05

        self.screen.blit(self.background, (0,0))
        self.placed.draw(self.screen)
        self.screen.blit(self.select_splash, (0,0))
        if self.selected_obj is not None:
            self.screen.blit(self.outline, (self.selected_obj.rect.left-s.BLOCK_SIZE*0.1, self.selected_obj.rect.top-s.BLOCK_SIZE*0.1))
            
        self.samples.draw(self.screen)
        newFont = pygame.font.SysFont('sans-serif', int(s.WIDTH*0.035))
        help_msg = newFont.render("Press 'h' to show help menu", True, (0,0,0))
        rect1 = help_msg.get_rect()
        rect1.bottomright = (s.WIDTH, s.HEIGHT*0.95)
        save_msg = newFont.render("Press 's' to save level", True, (0,0,0))
        rect2 = save_msg.get_rect()
        rect2.bottomright = (s.WIDTH, s.HEIGHT)

        self.screen.blit(help_msg, rect1)
        self.screen.blit(save_msg, rect2)

        pygame.display.flip()

    def reset(self):
        self.active = False
        self.selected = None
        self.erasing = False
        self.trackingBlock = None
        self.selected_obj = None
        self.placed.empty()
        self.isFlag = False
        self.isPlayer = False
        self.fileName = ''

    def save(self):
        """
        save level
        """

        self.shift_blocks()
        highest_block = None
        rightmost_block = None

        for i in self.placed:
            if highest_block is None:
                highest_block = i
            else:
                if i.rect.top < highest_block.rect.top:
                    highest_block = i
            if rightmost_block is None:
                rightmost_block = i
            else:
                if i.rect.right > rightmost_block.rect.right:
                    rightmost_block = i

        levelHeight = int((s.HEIGHT - highest_block.rect.top)/s.BLOCK_SIZE)
        levelWidth = int(rightmost_block.rect.right/s.BLOCK_SIZE)


        savedLevel = []
        curY = s.HEIGHT - s.BLOCK_SIZE*(3/4)
        curX = s.BLOCK_SIZE/2
        for i in range(levelHeight):
            a = []
            for j in range(levelWidth):
                for p in self.placed:
                    if p.rect.collidepoint((curX, curY)):
                        a.append(p.id)
                if len(a) <= j:
                    a.append(" ")
                curX += s.BLOCK_SIZE
            savedLevel.insert(0, a)
            curY -= s.BLOCK_SIZE
            curX = s.BLOCK_SIZE/2
        
        saveDict = {
            'level':savedLevel,
        }
        
        self.naming = True
        while self.naming:
            self.nameFile()
        
        if self.fileName == '':
            return
        
        if not os.path.exists("./levels"):
            os.makedirs("./levels")
        with open(f"./levels/{self.fileName}.json", 'w') as outfile:
            json.dump(saveDict, outfile)
        
        self.reset()
        self.active = False
        return

    def nameFile(self):
        """
        menu to name level
        """
        color = (255,255,255)
        input_rect = pygame.Rect(0,0, self.name_splash.get_width()*0.8, self.name_splash.get_height()*0.265)
        input_rect.center = (s.WIDTH/2, s.HEIGHT/2)
        name_rect = self.name_splash.get_rect()
        name_rect.center = (s.WIDTH/2, s.HEIGHT/2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
    
                # Check for backspace
                if event.key == pygame.K_BACKSPACE:
                    # get text input from 0 to -1 i.e. end.
                    self.fileName = self.fileName[:-1]
                    if self.over_char > 0:
                        self.over_char -= 1
                elif event.key == pygame.K_ESCAPE:
                    self.fileName = ''
                    self.naming = False
                    return
                elif event.key == pygame.K_RETURN:
                    self.naming = False
                    return
                # Unicode standard is used for string
                # formation
                elif len(self.fileName) < 20 and event.key in s.LEGAL_CHARS:
                    self.fileName += event.unicode
            
        self.screen.blit(self.name_splash, name_rect)
        
        pygame.draw.rect(self.screen, color, input_rect)
        text_surface = self.font.render(self.fileName[self.over_char:], True, (0,0,0))
        text_rect = text_surface.get_rect()
        if text_rect.width > input_rect.width-40:
            self.over_char += 1
            text_surface = self.font.render(self.fileName[self.over_char:], True, (0,0,0))
            text_rect = text_surface.get_rect()
        text_rect.x = input_rect.x+20
        text_rect.centery = input_rect.centery
        # render at position stated in arguments
        self.screen.blit(text_surface, text_rect)
        
        newFont = pygame.font.SysFont('sans-serif', int(s.WIDTH*0.035))
        msg1 = newFont.render("Name your level:", True, (0,0,0))
        msg2 = newFont.render("Press 'enter' when complete", True, (0,0,0))
        rect1 = msg1.get_rect()
        rect2 = msg2.get_rect()
        rect1.center = (s.WIDTH*0.5, s.HEIGHT*0.425)
        rect2.center = (s.WIDTH*0.5, s.HEIGHT*0.575)

        self.screen.blit(msg1, rect1)
        self.screen.blit(msg2, rect2)

        pygame.display.flip()

    def helpMenu(self):
        """
        help menu
        """
        msgArray = [
            "To select an item, click on it from the menu.", 
            "To place the item, click on the spot where you want it to be.",
            "You can use the left and right arrow keys to scroll",
            "through your level.",
            "Once you have exactly one player, one goal, and at",
            "least one floor block, you can press 's' to save your level."
        ]
        newFont = pygame.font.SysFont('sans-serif', int(s.WIDTH*0.035))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_h or event.key == pygame.K_ESCAPE:
                        return
            
            surf1 = newFont.render(msgArray[0], True, (0,0,0))
            rect1 = surf1.get_rect()
            surf2 = newFont.render(msgArray[1], True, (0,0,0))
            rect2 = surf2.get_rect()
            surf3 = newFont.render(msgArray[2], True, (0,0,0))
            rect3 = surf3.get_rect()
            surf4 = newFont.render(msgArray[3], True, (0,0,0))
            rect4 = surf4.get_rect()
            surf5 = newFont.render(msgArray[4], True, (0,0,0))
            rect5 = surf5.get_rect()
            surf6 = newFont.render(msgArray[5], True, (0,0,0))
            rect6 = surf6.get_rect()
            rect1.center = (s.WIDTH*0.5, s.HEIGHT*0.3)
            rect2.center = (s.WIDTH*0.5, s.HEIGHT*0.4)
            rect3.center = (s.WIDTH*0.5, s.HEIGHT*0.5)
            rect4.center = (s.WIDTH*0.5, s.HEIGHT*0.55)
            rect5.center = (s.WIDTH*0.5, s.HEIGHT*0.7)
            rect6.center = (s.WIDTH*0.5, s.HEIGHT*0.75)
            self.screen.blit(self.help_splash, (s.WIDTH*0.1, s.HEIGHT*0.1))
            self.screen.blit(surf1, rect1)
            self.screen.blit(surf2, rect2)
            self.screen.blit(surf3, rect3)
            self.screen.blit(surf4, rect4)
            self.screen.blit(surf5, rect5)
            self.screen.blit(surf6, rect6)
            pygame.display.flip()

    def shift_blocks(self):

        save_player = None
        for i in self.placed:
            if isinstance(i, player.Player):
                save_player = i
        if save_player is not None:
            dif = -save_player.rect.left
            for i in self.placed:
                i.rect = i.rect.move(dif, 0)
