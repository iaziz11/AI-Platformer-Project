import math

class Node():
    def __init__(self, x) -> None:
        self.x = x
        self.output = None
        self.connections = []

    def getX(self):
        return self.x

    def getOutput(self):
        return self.output

    def getConnections(self):
        return self.connections

    def setX(self, a):
        self.x = a
    
    def setOutput(self, a):
        self.output = a

    def setConnections(self, a):
        self.connections = a

    def calculate(self):
        """
        returns output of node
        """
        sum = 0
        for c in self.connections:
            if c.isEnabled():
                sum += c.getWeight() * c.getFrom().getOutput()
        self.output = self.activation_fun(sum)
            
    def activation_fun(self, x):
        """
        returns sigmoid(x)
        """
        return 1/(1+math.exp(-x))

    def compareTo(self, o):
        """
        compares self to other
        """
        if self.getX() > o.getX():
            return -1
        if self.getX() < o.getX():
            return 1
        return 0
    
