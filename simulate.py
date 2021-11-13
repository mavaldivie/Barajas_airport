import random, math

def uniform(a, b):
    u = random.random()
    return a + u * (b - a)

def exponential(lam):
    u = uniform(0, 1)
    return -math.log(u) / lam

def normal(mu, sigma2):
    while True:
        y = exponential(1)
        u = uniform(0, 1)
        if u <= math.pow(math.e, -(y - 1) ** 2 / 2):
            u = uniform(0, 1)
            if u <= .5:
                sign = 1
            else:
                sign = -1
            return sign * y * math.sqrt(sigma2) + mu