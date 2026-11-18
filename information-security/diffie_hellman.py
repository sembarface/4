
from math import gcd
from random import randint


def factorize(n):
    factors = []
    d = 2

    while d * d <= n:
        power = 0

        while n % d == 0:
            n //= d
            power += 1

        if power > 0:
            factors.append((d, power))

        d += 1

    if n > 1:
        factors.append((n, 1))

    return factors


for p, candidates in [(13, [3, 7]), (1022333835329657, [3])]:
    k = p - 1
    mn = factorize(k)
    pi = [d for d, power in mn]
    s = len(pi)
    ki = [k // d for d in pi]

    kp = k
    for d in pi:
        kp = kp // d * (d - 1)

    print("\np =", p)
    print("k =", k)
    print("mn =", mn)
    print("pi =", pi)
    print("s =", s)
    print("ki =", ki)
    print("kp =", kp)
    print("kp / k =", round(kp / k, 3))

    for a in candidates:
        aki = [pow(a, n, p) for n in ki]

        print("\na =", a)
        print("aki =", aki)
        print("Есть 1:", 1 in aki)
        print("Первообразный корень:", 1 not in aki)

    if p != 13:
        t = 0

        while gcd(t, k) != 1:
            t = randint(k // 2, k)

        new_a = pow(3, t, p)

        print("\nt =", t)
        print("Новый первообразный корень =", new_a)
