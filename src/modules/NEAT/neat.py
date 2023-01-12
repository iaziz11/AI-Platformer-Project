from modules.NEAT.data_structs.randomHashSet import RandomHashSet
from modules.NEAT.data_structs.randomSelector import randomSelector 
from modules.NEAT.genome.nodeGene import NodeGene
from modules.NEAT.genome.genome import Genome
from modules.NEAT.genome.connectionGene import connectionGene
from modules.NEAT.client import Client
from modules.NEAT.species import Species

class Neat():
    def __init__(self, input_size, output_size, clients) -> None:
        self.MAX_NODES = 2**20
        self.SURVIVORS = 0.3
        self.WEIGHT_SHIFT_STRENGTH = 0.3
        self.WEIGHT_RANDOM_STRENGTH = 0.02
        self.PROB_MUTATE_LINK = 0.80
        self.PROB_MUTATE_NODE = 0.60
        self.PROB_MUTATE_WEIGHT_SHIFT = 0.50
        self.PROB_MUTATE_WEIGHT_RANDOM = 0.40
        self.PROB_MUTATE_TOGGLE = 0.15
        self.c1, self.c2, self.c3 = 1, 1, 1
        self.all_connections = {}
        self.all_nodes = RandomHashSet()
        self.clients = RandomHashSet()
        self.species = RandomHashSet()
        self.species_threshold = 1.5
        self.reset(input_size, output_size, clients)

    def printSpecies(self):
        """
        prints all the species
        """
        print("#########################")
        for s in self.species.getData():
            print(f"{s}.....{s.getScore()}......{s.size()}")

    def empty_genome(self):
        """
        create an empty genome
        """
        g = Genome(self)
        for i in range(self.input_size+self.output_size):
            g.getNodes().add(self.getNode(i+1))
        return g

    def reset(self,input_size, output_size, clients):
        self.input_size = input_size
        self.output_size = output_size
        self.max_clients = clients
        self.all_connections.clear()
        self.all_nodes.clear()
        self.clients.clear()
        for i in range(self.input_size):
            n = self.getNode()
            n.setX(0.1)
            n.setY((i+1)/(self.input_size+1))
            
        for i in range(self.output_size):
            n = self.getNode()
            n.setX(0.9)
            n.setY((i+1)/(self.output_size+1))

        for i in range(self.max_clients):
            c = Client()
            c.setGenome(self.empty_genome())
            c.generate_calculator()
            self.clients.add(c)

    def getClient(self, i):
        return self.clients.get_object(i)


    def getNode(self, id=None):
        if id is not None:
            if id <= self.all_nodes.size():
                return self.all_nodes.get_object(id-1)
            return self.getNode()
        n = NodeGene(self.all_nodes.size()+1)
        self.all_nodes.add(n)
        return n
    
    def getConnection(self, node1, node2, copy=None):

        if copy is not None:
            cg = connectionGene(copy.getFrom(), copy.getTo())
            cg.setInnovationNum(copy.getInnovationNum())
            cg.setWeight(copy.getWeight())
            cg.setEnabled(copy.isEnabled())
            return cg

        cg = connectionGene(node1, node2)

        if cg in self.all_connections.keys():
            cg.setInnovationNum(self.all_connections.get(cg).getInnovationNum())
        else:
            cg.setInnovationNum(len(self.all_connections)+1)
            self.all_connections.update({cg:cg})
        
        return cg

    def getC1(self):
        return self.c1
    
    def getC2(self):
        return self.c2

    def getC3(self):
        return self.c3

    def getWEIGHT_SHIFT_STRENGTH(self):
        return self.WEIGHT_SHIFT_STRENGTH

    def getWEIGHT_RANDOM_STRENGTH(self):
        return self.WEIGHT_RANDOM_STRENGTH

    def getPROB_MUTATE_LINK(self):
        return self.PROB_MUTATE_LINK

    def getPROB_MUTATE_NODE(self):
        return self.PROB_MUTATE_NODE

    def getPROB_MUTATE_WEIGHT_SHIFT(self):
        return self.PROB_MUTATE_WEIGHT_SHIFT

    def getPROB_MUTATE_WEIGHT_RANDOM(self):
        return self.PROB_MUTATE_WEIGHT_RANDOM
    
    def getPROB_MUTATE_TOGGLE(self):
        return self.PROB_MUTATE_TOGGLE

    def getSpeciesThreshold(self):
        return self.species_threshold

    def setSpeciesThreshold(self, a):
        self.species_threshold = a


    def evolve(self):
        self.gen_species()
        self.kill()
        self.remove_extinct()
        self.reproduce()
        self.mutate()
        for c in self.clients.getData():
            c.generate_calculator()
        

    def gen_species(self):
        """
        generate all the species for current generation
        """
        for s in self.species.getData():
            s.reset()

        for c in self.clients.getData():
            if c.getSpecies() is not None:
                continue
            found = False
            for s in self.species.getData():
                if s.put(c):
                    found = True
                    break
            if not found:
                self.species.add(Species(c))

        for s in self.species.getData():
            s.evalScore()

    def kill(self):
        """
        kill off percentage of clients from each species
        """
        for s in self.species.getData():
            s.kill(1-self.SURVIVORS)

    def remove_extinct(self):
        """
        delete extinct species
        """
        i = self.species.size()-1
        while i >= 0:
            if self.species.get_object(i).size() <= 0:
                self.species.get_object(i).goExtinct()
                self.species.remove_index(i)
            i -= 1
            
    def reproduce(self):
        """
        breed two clients
        """
        selector = randomSelector()
        for s in self.species.getData():
            selector.add(s, s.getScore())

        if len(selector.objects) == 0:
            return

        for c in self.clients.getData():
            if c.getSpecies() is None:
                s = selector.random()
                c.setGenome(s.breed())
                s.forcePut(c)

    def mutate(self):
        for c in self.clients.getData():
            c.mutate()

    def setReplaceIndex(self, node1, node2, index):
        self.all_connections.get(connectionGene(node1, node2)).setReplaceIndex(index)

    def getReplaceIndex(self, node1, node2):
        con = connectionGene(node1, node2)
        data = self.all_connections.get(con)
        if data is None:
            return 0
        return data.getReplaceIndex()





        


    






