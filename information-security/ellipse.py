from math import isqrt
from rabin_miller import rabin_miller


def next_prime(n):
    if n < 2:
        return 2

    p = n + 1

    if p % 2 == 0:
        p += 1

    while not rabin_miller(p):
        p += 2

    return p


def find_point(a, b, p):
    for x in range(1, p):
        y2 = (x ** 3 + a * x + b) % p

        for y in range(p):
            if y ** 2 % p == y2:
                return x, y


def add_points(P, Q, a, p):
    if P is None:
        return Q

    if Q is None:
        return P

    x1, y1 = P
    x2, y2 = Q

    if x1 == x2 and (y1 + y2) % p == 0:
        return None

    if P == Q:
        k = (3 * x1 ** 2 + a) * pow(2 * y1, -1, p) % p
    else:
        k = (y2 - y1) * pow(x2 - x1, -1, p) % p

    x = (k ** 2 - x1 - x2) % p
    y = (k * (x1 - x) - y1) % p

    return x, y


def multiply_point(n, P, a, p, show=False):
    points = [P]

    while 2 ** len(points) <= n:
        points.append(add_points(points[-1], points[-1], a, p))

    result = None
    total = 0

    if show:
        for i, point in enumerate(points):
            print(f"{2 ** i}P = {format_point(point)}")
        print()

    for i, point in enumerate(points):
        if n & (2 ** i):
            result = add_points(result, point, a, p)
            total += 2 ** i

            if show:
                print(f"{total}P = {format_point(result)}")

    return result


def curve_order(a, b, p):
    order = 1

    for x in range(p):
        y2 = (x ** 3 + a * x + b) % p

        if y2 == 0:
            order += 1
        elif pow(y2, (p - 1) // 2, p) == 1:
            order += 2

    return order


def prime_divisors(n):
    divisors = []

    for d in range(2, isqrt(n) + 1):
        if n % d == 0:
            divisors.append(d)

            while n % d == 0:
                n //= d

    if n > 1:
        divisors.append(n)

    return divisors


def point_order(P, N, a, p):
    order = N

    for d in prime_divisors(N):
        while order % d == 0:
            k = order // d
            Q = multiply_point(k, P, a, p)
            print(f"{k}P = {format_point(Q)}")

            if Q is not None:
                break

            order = k

    return order


def format_point(P):
    return "E" if P is None else str(P)


alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
initials = "ХВГ"

number = int("".join(str(alphabet.index(c) + 1) for c in initials))

p = next_prime(number)
a, b = 1, 0

print(f"Инициалы: {initials}")
print(f"Исходное число: {number}")
print(f"p = {p}")

P = find_point(a, b, p)
print(f"\nP = {P}")

print("\nВычисление 151P:")
Q = multiply_point(151, P, a, p, show=True)

N = curve_order(a, b, p)
print(f"\nПорядок кривой: {N}")

print("\nВычисление порядка точки:")
order = point_order(P, N, a, p)

print(f"\nПорядок точки P: {order}")