
from math import isqrt


def perfectSquare(x):
    return isqrt(x) ** 2 == x


def factorizeFerma(n):
    x = isqrt(n)

    if x * x < n:
        x += 1

    while not perfectSquare(x * x - n):
        x += 1

    y = isqrt(x * x - n)

    p = x - y
    q = x + y

    return p, q


n = 459815140061495110658001985470439569453709795016952965385917

p, q = factorizeFerma(n)

print(f"p = {p}")
print(f"q = {q}")
print(f"p * q = {p * q}")