import random

# 21-битное число: старший и младший биты равны 1.
p = random.getrandbits(21) | (1 << 20) | 1
small_primes = [2, 3, 5, 7, 11, 13, 17, 19]

print('Начальное 21-битное нечётное число:')
print(f'p = {p}')
print(f'В двоичной системе: {p:021b}')

while True:
    # При прибавлении 2 число не должно стать 22-битным.
    if p >= 2**21:
        p = random.getrandbits(21) | (1 << 20) | 1
        print(f'\nВышли за 21 бит. Новое число: {p} ({p:021b})')

    print(f'\n Проверяем p = {p} ')
    print('1. Проверка делимости на небольшие простые числа:')

    divisor = None
    for k in small_primes:
        remainder = p % k
        print(f'   {p} mod {k} = {remainder}')
        if remainder == 0:
            divisor = k

    if divisor is not None:
        print(f'p делится на {divisor}, значит, оно составное.')
        print('Увеличиваем p на 2 и повторяем проверку.')
        p += 2
        continue

    print('На малые простые числа p не делится.')
    print('\n2. Представим p - 1 = 2^b * m, где m нечётное:')

    m = p - 1
    b = 0
    while m % 2 == 0:
        m //= 2
        b += 1

    print(f'   {p} - 1 = 2^{b} * {m}')
    print(f'   b = {b}, m = {m}')

    print('\n3. Выполняем 5 тестов Рабина — Миллера:')
    passed_tests = 0

    for test in range(1, 6):
        a = random.randint(2, p - 2)
        z = pow(a, m, p)

        print(f'\n   Тест {test}/5. Случайное a = {a}')
        print(f'   j = 0: z = {a}^{m} mod {p} = {z}')

        if z == 1 or z == p - 1:
            print('   z = 1 или p - 1. Тест пройден.')
            passed_tests += 1
            continue

        test_passed = False
        for j in range(1, b):
            z = (z * z) % p
            print(f'   j = {j}: z = z^2 mod {p} = {z}')

            if z == p - 1:
                print('   z = p - 1. Тест пройден.')
                test_passed = True
                break

            if z == 1:
                print('   При j > 0 получили z = 1. Число составное.')
                break

        if test_passed:
            passed_tests += 1
        else:
            print('   Тест не пройден: p — составное число.')
            break

    if passed_tests == 5:
        error = (1 / 4) ** 5
        print('\n РЕЗУЛЬТАТ ')
        print(f'Число p = {p} прошло все 5 тестов.')
        print('Вывод: p — вероятно простое число.')
        print(f'Оценка вероятности ошибки: не более {error:.8%} (1/1024).')
        print(f'Оценка надёжности теста: не менее {1 - error:.8%}.')
        break

    print('\nУвеличиваем p на 2 и ищем следующего кандидата.')
    p += 2
