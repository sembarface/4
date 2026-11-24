
import random
from math import gcd
from sympy import factorint, totient
from rabin_miller import rabin_miller, generate_prime


def generate_p(bits):
    if bits != 1024:
        return generate_prime(bits)

    while True:
        q = generate_prime(bits - 12)
        min_c = ((1 << (bits - 1)) - 2) // (2 * q) + 1
        max_c = ((1 << bits) - 2) // (2 * q)

        for c in range(min_c, max_c + 1):
            p = 2 * c * q + 1
            if rabin_miller(p):
                return p


for bits in [6, 1024]:
    p = generate_p(bits)

    k = p - 1
    mn = sorted(factorint(k).items())
    pi = [d for d, power in mn]
    s = len(pi)
    ki = [k // d for d in pi]
    kp = int(totient(k))

    g = 3
    while True:
        aki = [pow(g, exponent, p) for exponent in ki]
        if 1 not in aki:
            break
        g += 1

    t = 0
    while gcd(t, k) != 1:
        t = random.randint(k // 2, k)

    new_g = pow(g, t, p)

    a = random.randint(2, p - 2)
    b = random.randint(2, p - 2)

    A = pow(g, a, p)
    B = pow(g, b, p)

    K_A = pow(B, a, p)
    K_B = pow(A, b, p)

    print(f'\nДлина числа: {bits} бит')
    print('p =', p)
    print('k =', k)
    print('mn =', mn)
    print('pi =', pi)
    print('s =', s)
    print('ki =', ki)
    print('kp =', kp)
    print('kp / k =', round(kp / k, 3))
    print('Первообразный корень g =', g)
    print('aki =', aki)
    print('Есть 1:', 1 in aki)
    print('t =', t)
    print('Новый первообразный корень =', new_g)
    print('Секрет Алисы a =', a)
    print('Секрет Боба b =', b)
    print('Открытый ключ Алисы A =', A)
    print('Открытый ключ Боба B =', B)
    print('Общий ключ Алисы K_A =', K_A)
    print('Общий ключ Боба K_B =', K_B)
    print('Ключи совпадают:', K_A == K_B)
