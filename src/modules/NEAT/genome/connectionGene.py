from modules.NEAT.genome.gene import Gene


class connectionGene(Gene):
    def __init__(self, fromNode, toNode) -> None:
        super().__init__(None)
        self.fromNode = fromNode
        self.toNode = toNode
        self.weight = None
        self.enabled = True
        self.replaceIndex = None
        self.MAX_NODES = 2**20

    def __hash__(self) -> int:
        return self.hashCode()

    def __eq__(self, o) -> bool:
        return self.equals(o)

    def getFrom(self):
        return self.fromNode

    def getTo(self):
        return self.toNode

    def setFrom(self, a):
        self.fromNode = a

    def setTo(self, a):
        self.toNode = a

    def getWeight(self):
        return self.weight

    def setWeight(self, a):
        self.weight = a

    def isEnabled(self):
        return self.enabled

    def setEnabled(self, a):
        self.enabled = a

    def equals(self, a):
        if not isinstance(a, connectionGene):
            return False

        return self.fromNode.equals(a.fromNode) and self.toNode.equals(a.toNode)

    def hashCode(self):
        return self.fromNode.getInnovationNum() * self.MAX_NODES + self.toNode.getInnovationNum()

    def getReplaceIndex(self):
        return self.replaceIndex

    def setReplaceIndex(self, a):
        self.replaceIndex = a
