from modules.NEAT.calculations.node import Node
from modules.NEAT.calculations.connection import Connection

class Calculator():
    def __init__(self, g) -> None:
        self.input_nodes = []
        self.hidden_nodes = []
        self.output_nodes = []
        self.nodes = g.getNodes()
        self.cons = g.getConnections()
        self.node_map = {}

        for n in self.nodes.getData():
            node = Node(n.getX())
            self.node_map.update({n.getInnovationNum():node})

            if n.getX() <= 0.1:
                self.input_nodes.append(node)
            elif n.getX() >= 0.9:
                self.output_nodes.append(node)
            else:
                self.hidden_nodes.append(node)
        
        self.hidden_nodes.sort(key=lambda a: a.x)

        for c in self.cons.getData():
            fromN = c.getFrom()
            toN = c.getTo()

            fromNode = self.node_map.get(fromN.getInnovationNum())
            toNode = self.node_map.get(toN.getInnovationNum())

            con = Connection(fromNode, toNode)
            con.setWeight(c.getWeight())
            con.setEnabled(c.isEnabled())

            toNode.getConnections().append(con)

        

    def calculate(self, input):
        """
        determine output of nn
        """
        if len(input) != len(self.input_nodes):
            raise Exception("Data doesn't fit")
        for i in range(len(self.input_nodes)):
            self.input_nodes[i].setOutput(input[i])

        for n in self.hidden_nodes:
            n.calculate()

        output = []
        for i in range(len(self.output_nodes)):
            self.output_nodes[i].calculate()
            output.append(self.output_nodes[i].getOutput())

        return output
