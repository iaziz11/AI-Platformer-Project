import random
from modules.NEAT.data_structs.randomHashSet import RandomHashSet
from modules.NEAT.genome.connectionGene import connectionGene

class Genome():
    def __init__(self, neat) -> None:
        self.connections = RandomHashSet()
        self.nodes = RandomHashSet()
        self.neat = neat

    def getConnections(self):
        return self.connections
    
    def getNodes(self):
        return self.nodes

    def getNeat(self):
        return self.neat

    def distance(self, g2):
        """
        returns the "distance" between two genomes, or how dissimilar two genomes are from each other
        """
        g1 = self

        highest_inn_num_g1 = 0
        if g1.getConnections().size() != 0:
            highest_inn_num_g1 = g1.getConnections().get_object(-1).getInnovationNum()

        highest_inn_num_g2 = 0
        if g2.getConnections().size() != 0:
            highest_inn_num_g2 = g2.getConnections().get_object(-1).getInnovationNum()

        if highest_inn_num_g1 < highest_inn_num_g2:
            g1, g2 = g2, g1

        idx1 = 0
        idx2 = 0
        disjoint_genes = 0
        excess_genes = 0
        weight_diff = 0
        similar = 0

        while(idx1 < g1.getConnections().size() and idx2 < g2.getConnections().size()):
            gene1 = g1.getConnections().get_object(idx1)
            gene2 = g2.getConnections().get_object(idx2)

            in1 = gene1.getInnovationNum()
            in2 = gene2.getInnovationNum()

            if in1 == in2:
                idx1 += 1
                idx2 += 1
                similar += 1
                weight_diff += abs(gene1.getWeight() - gene2.getWeight())
            elif in1 > in2:
                idx2 += 1
                disjoint_genes += 1
            else:
                idx1 += 1
                disjoint_genes += 1
        
        weight_diff /= max(similar, 1)
        excess_genes = g1.getConnections().size()-idx1

        N = max(g1.getConnections().size(), g2.getConnections().size())
        if(N < 20):
            N = 1

        return (self.neat.getC1() * disjoint_genes / N) + (self.neat.getC2() * excess_genes / N) + (self.neat.getC3() * weight_diff)

    def mutate(self):
        if self.neat.getPROB_MUTATE_LINK() > random.random():
            self.mutate_link()
        if self.neat.getPROB_MUTATE_NODE() > random.random():
            self.mutate_node()
        if self.neat.getPROB_MUTATE_TOGGLE() > random.random():
            self.mutate_link_toggle()
        if self.neat.getPROB_MUTATE_WEIGHT_SHIFT() > random.random():
            self.mutate_weight_shift()
        if self.neat.getPROB_MUTATE_WEIGHT_RANDOM() > random.random():
            self.mutate_weight_random()
        

    def mutate_link(self):
        """
        add a new link between two nodes
        """
        for _ in range(100):
            a = self.nodes.random_element()
            b = self.nodes.random_element()

            if a is None or b is None:
                continue
            if a.getX() == b.getX():
                continue
            
            con = None
            if a.getX() < b.getX():
                con = connectionGene(a, b)
            else:
                con = connectionGene(b, a)

            if self.connections.contains(con):
                continue

            con = self.neat.getConnection(con.getFrom(), con.getTo())
            con.setWeight((random.random() * 2 - 1) * self.neat.getWEIGHT_RANDOM_STRENGTH())
            self.connections.add_sorted(con)
            return

    def mutate_node(self):
        """
        add a new node in between two nodes
        """
        con = self.connections.random_element()
        if con is None:
            return
        
        fromNode = con.getFrom()
        toNode = con.getTo()

        replaceIndex = self.neat.getReplaceIndex(fromNode, toNode)
        middle = None
        if replaceIndex == 0 or replaceIndex == None:
            middle = self.neat.getNode()
            middle.setX((fromNode.getX() + toNode.getX()) / 2)
            middle.setY((fromNode.getY() + toNode.getY()) / 2 + random.random()*0.1-0.05)
            self.neat.setReplaceIndex(fromNode, toNode, middle.getInnovationNum())
        else:
            middle = self.neat.getNode(replaceIndex) 

        con1 = self.neat.getConnection(fromNode, middle)
        con2 = self.neat.getConnection(middle, toNode)

        con1.setWeight(1)
        con2.setWeight(con.getWeight())
        con2.setEnabled(con.isEnabled())

        self.connections.remove_object(con)
        self.connections.add(con1)
        self.connections.add(con2)

        self.nodes.add(middle)

    def mutate_weight_shift(self):
        """
        shift the weight of a connection     
        """
        con = self.connections.random_element()
        if con != None:
            con.setWeight(con.getWeight() + (random.random() * 2 - 1) * self.neat.getWEIGHT_SHIFT_STRENGTH())

    def mutate_weight_random(self):
        """
        randomly change the weight of a connection
        """
        con = self.connections.random_element()
        if con != None:
            con.setWeight((random.random() * 2 - 1) * self.neat.getWEIGHT_RANDOM_STRENGTH())
        
    def mutate_link_toggle(self):
        """
        toggle a connection on or off
        """
        con = self.connections.random_element()
        if con != None:
            con.setEnabled(not con.isEnabled())

    def crossover(self, g1, g2):
        """
        return a new genome that is a crossover of two existing genomes
        """
        neat = g1.getNeat()
        new_genome = neat.empty_genome()

        idx1 = 0
        idx2 = 0
       
        while(idx1 < g1.getConnections().size() and idx2 < g2.getConnections().size()):

            gene1 = g1.getConnections().get_object(idx1)
            gene2 = g2.getConnections().get_object(idx2)
            in1 = gene1.getInnovationNum()
            in2 = gene2.getInnovationNum()

            if in1 == in2:
                if(random.random() > 0.5):
                    new_genome.getConnections().add(neat.getConnection(None, None, gene1))
                else:
                    new_genome.getConnections().add(neat.getConnection(None, None, gene2))
                idx1 += 1
                idx2 += 1
            elif in1 > in2:
                idx2 += 1
            else:
                new_genome.getConnections().add(neat.getConnection(None, None, gene1))
                idx1 += 1
        
        while(idx1 < g1.getConnections().size()):
            gene1 = g1.getConnections().get_object(idx1)
            new_genome.getConnections().add(neat.getConnection(None, None, gene1))
            idx1 += 1

        for i in new_genome.getConnections().getData():
            new_genome.getNodes().add(i.getFrom())
            new_genome.getNodes().add(i.getTo())


        return new_genome


    
