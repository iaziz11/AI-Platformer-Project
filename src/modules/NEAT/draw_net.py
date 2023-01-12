import pygame, random
import numpy, time, sys
from modules.NEAT.neat import Neat
import json
import itertools, pickle

class draw():
    def __init__(self, neat) -> None:
        self.screen_size = (1200,800)
        self.neat = neat
        self.g = None
        self.c = None
        self.s = None
        self.radius = 10
        self.nodeMap = []
        self.save = {
            "Nodes":[],
            "Connections":[]
        }

    def getBestClient(self):
        """
        get the best performing client from the best performing species
        """
        if self.neat.species.size() > 0:
            a = self.neat.species.getData().copy()
            a.sort(key=lambda x: x.getScore())
            best_species = a[-1]
            self.s = best_species
            b = best_species.clients.getData().copy()
            b.sort(key=lambda x: x.getScore())
            best_client = b[-1]
            self.c = best_client
            self.g = best_client.getGenome()

    def drawScreen(self, screen):
        """
        draw the network of the best client from the best species
        """
        self.screen = pygame.display.set_mode(self.screen_size)
        self.screen.fill((0,0,0))
        if self.neat.species.size() > 0:
            self.getBestClient()
            for n in self.g.nodes.getData():
                pygame.draw.circle(self.screen, (255,255,255), (n.getX()*self.screen_size[0], n.getY()*self.screen_size[1]), self.radius)
            for c in self.g.connections.getData():
                color = (0,255,0) if c.isEnabled() else (255,0,0)
                pygame.draw.line(self.screen, color, (c.getFrom().getX()*self.screen_size[0]+self.radius, c.getFrom().getY()*self.screen_size[1]), (c.getTo().getX()*self.screen_size[0]-self.radius,c.getTo().getY()*self.screen_size[1]))

            pygame.display.flip()
        else:
            print("Not enough species")

    def listNodes(self):
        """
        get a list of all the nodes in the network
        """
        for c in self.g.connections.getData():
            found = False
            for i in self.nodeMap:
                if c.getFrom() != i[0]:
                    continue
                else:
                    i[2] = c.hashCode()
                    found = True
            if not found:
                self.nodeMap.append([c.getFrom(), None, c.hashCode()])
            found = False
            for i in self.nodeMap:
                if c.getTo() != i[0]:
                    continue
                else:
                    i[1] = c.hashCode()
                    found = True
            if not found:
                self.nodeMap.append([c.getTo(), c.hashCode(), None])
        
    def saveClient(self, name):
        """
        save the best representative of the best performing species
        """
        with open(f"{name}.pkl", "wb") as out:
            pickle.dump(self.s.representative, out, 0)



if __name__ == "__main__":
    neat = Neat(10, 1, 1000)
    drawNet = draw(neat)
    neat.evolve()
    while True:
        drawNet.drawScreen()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    for a in neat.clients.getData():
                        b = a.getGenome()
                        b.mutate_link()
                elif event.key == pygame.K_2:
                    for a in neat.clients.getData():
                        a.getGenome().mutate_node()
                elif event.key == pygame.K_3:
                    for a in neat.clients.getData():
                        b = a.getGenome()
                        b.mutate_link_toggle()
                elif event.key == pygame.K_4:
                    for a in neat.clients.getData():
                        b = a.getGenome()
                        b.mutate_weight_shift()
                elif event.key == pygame.K_5:
                    for a in neat.clients.getData():
                        b = a.getGenome()
                        b.mutate_weight_random()
                elif event.key == pygame.K_6:
                    neat.evolve()
                    sum = 0
                    for i in neat.species.getData():
                        print(i.clients.size())
                        sum += i.clients.size()
                    print(neat.species.size())
                    print(sum)
                        




    
                









