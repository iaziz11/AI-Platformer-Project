import random

class randomSelector():
    def __init__(self) -> None:
        self.objects = []
        self.scores = []
        self.total_score = 0

    def add(self, element, score):
        self.objects.append(element)
        self.scores.append(score)
        self.total_score += score

    def random(self):
        if len(self.objects) == 0:
            raise Exception("Nothing in random selector")
        v = random.random() * self.total_score
        c = 0
        
        for i in range(len(self.objects)):
            c += self.scores[i]
            if c >= v:
                return self.objects[i]

        return None

    def reset(self):
        self.objects.clear()
        self.scores.clear()
        self.total_score = 0