from modules.NEAT.genome.gene import Gene

class NodeGene(Gene):
    def __init__(self, innovation_num) -> None:
        super().__init__(innovation_num)
        self.x = None
        self.y = None

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def setX(self, x):
        self.x = x

    def setY(self, y):
        self.y = y

    def equals(self, a):
        if not isinstance(a, NodeGene):
            return False
        return self.innovation_num == a.getInnovationNum()
    
    def hashCode(self):
        return self.innovation_num


