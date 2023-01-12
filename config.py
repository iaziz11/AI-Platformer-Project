#--------------------------------
#Reinforcement Learning Settings
#--------------------------------

#How many frames do you want to train for?
#(Should be at least 100_000 or else model will not be saved)
FRAMES_TO_TRAIN = 2_000_000

#What would you like the learning rate to be?
#(Controls how quickly the model learns, should not be too low or too high)
LR = 0.0001

#How many seconds before the model should end its run?
RL_TIMEOUT = 60



#-----------------------
#NEAT Algorithm Settings
#-----------------------

#How many seconds should each client wait before force killing itself?
#(This is necessary because some clients will not move, so they will potentially never die)
#(Make sure it is physically possible to beat the level in the allocated time)
NEAT_TIMEOUT = 4

#How many clients to train?
#(The more clients you have, the more diversity, but the algorithm will take longer)
#(You should never have less than 10 clients)
NUM_CLIENTS = 60

#How many generations should the clients evolve for?
#(More generations allow for more evolution)
NUM_GENERATIONS = 72

