
import math
import random


def instance(details = False):
    random.seed()
    ROOT = 2023
    alpha = 0
    beta = random.randrange(1, ROOT)
    while beta == alpha:
        beta = random.randrange(1, ROOT)
        
    alpha_rad = alpha * 2 * math.pi / ROOT
    beta_rad = beta * 2 * math.pi / ROOT

    a1 = math.cos(alpha_rad)
    b1 = math.sin(alpha_rad)
    a2 = math.cos(beta_rad)
    b2 = math.sin(beta_rad)

    a3 = a1 + a2
    b3 = b1 + b2

    if details:
        print(alpha, beta)
        # print (a3*a3 + b3*b3, 2 + math.sqrt(3))
    return a3*a3 + b3*b3


def simulation(N):
    count = 0
    threshold = 2 + math.sqrt(3)

    for i in range(N):
        x = instance((N <= 100))
        if x >= threshold:
            count = count + 1

    print(N, count, count / N)

simulation(10000000)




