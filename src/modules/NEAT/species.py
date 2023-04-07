from modules.NEAT.data_structs.randomHashSet import RandomHashSet
from modules.NEAT.genome.genome import Genome


class Species():
    def __init__(self, repr) -> None:
        self.clients = RandomHashSet()
        self.representative = repr
        self.representative.setSpecies(self)
        self.clients.add(self.representative)
        self.score = 0

    def put(self, a):
        if a.distance(self.representative) < self.representative.getGenome().getNeat().getSpeciesThreshold():
            a.setSpecies(self)
            self.clients.add(a)
            return True
        return False

    def forcePut(self, a):
        a.setSpecies(self)
        self.clients.add(a)

    def goExtinct(self):
        for c in self.clients.getData():
            c.setSpecies(None)

    def evalScore(self):
        v = 0
        for c in self.clients.getData():
            v += c.getScore()
        self.score = v/self.clients.size()

    def reset(self):
        self.representative = self.clients.random_element()
        for c in self.clients.getData():
            c.setSpecies(None)

        self.clients.clear()
        self.clients.add(self.representative)
        self.representative.setSpecies(self)
        self.score = 0

    def kill(self, percentage):
        if len(self.clients.getData()) <= 1:
            return
        self.clients.getData().sort(key=lambda a: a.getScore())

        amount = percentage*self.clients.size()
        for _ in range(int(amount)):
            self.clients.get_object(0).setSpecies(None)
            self.clients.remove_index(0)

    def breed(self):
        c1 = self.clients.random_element()
        c2 = self.clients.random_element()

        if (c1.getScore() > c2.getScore()):
            return Genome.crossover(None, c1.getGenome(), c2.getGenome())
        return Genome.crossover(None, c2.getGenome(), c1.getGenome())

    def size(self):
        return self.clients.size()

    def getClients(self):
        return self.clients

    def getRepresentative(self):
        return self.representative

    def getScore(self):
        return self.score
