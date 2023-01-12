from modules.NEAT.calculations.calculator import Calculator

class Client():
    def __init__(self) -> None:
        self.genome = None
        self.score = 0
        self.species = None
        self.calculator = None

    def generate_calculator(self):
        self.calculator = Calculator(self.genome)

    def calculate(self, a):
        if self.calculator is None:
            self.generate_calculator()
        return self.calculator.calculate(a)

    def getCalculator(self):
        return self.calculator

    def getGenome(self):
        return self.genome
    
    def setGenome(self, a):
        self.genome = a
    
    def getScore(self):
        return self.score

    def setScore(self, a):
        self.score = a
    
    def getSpecies(self):
        return self.species

    def setSpecies(self, a):
        self.species = a

    def distance(self, other):
        return self.getGenome().distance(other.getGenome())

    def mutate(self):
        self.getGenome().mutate()
