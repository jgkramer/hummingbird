
import random

def jump():
    x = random.random()
    #print(x)
    n = 0
    while(x < 1):
        x = x*2
        n = n+1
    return n

def frog(N, target):
    hits = 0
    for i in range(N):
        place = 0
        while(place < target):
            place = place + jump()
        if(place == target):
            hits = hits+1

    print(N, hits, hits/N)

if __name__ == "__main__":
    frog(1000000, 20)




