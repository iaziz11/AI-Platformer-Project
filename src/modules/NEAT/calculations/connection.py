class Connection():
    def __init__(self, fromNode, toNode) -> None:
        self.fromNode = fromNode
        self.toNode = toNode
        self.weight = None
        self.enabled = True

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

