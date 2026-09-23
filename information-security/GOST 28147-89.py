# ГОСТ 28147-89
# Один цикл алгоритма


text = "ХАЧАТУРЯН ВЛАДИМИР ГАРИКОВИЧ"


# Таблица подстановки из Приложения В
S = [
    [1, 15, 13, 0, 5, 7, 10, 4, 9, 2, 3, 14, 6, 11, 8, 12],
    [13, 11, 4, 1, 3, 15, 5, 9, 0, 10, 14, 7, 6, 8, 2, 12],
    [4, 11, 10, 0, 7, 2, 1, 13, 3, 6, 8, 5, 9, 12, 15, 14],
    [6, 12, 7, 1, 5, 15, 13, 8, 4, 10, 9, 14, 0, 3, 11, 2],
    [7, 13, 10, 1, 0, 8, 9, 15, 14, 4, 6, 12, 11, 2, 5, 3],
    [5, 8, 1, 13, 10, 3, 4, 2, 14, 15, 12, 7, 6, 0, 9, 11],
    [14, 11, 4, 12, 6, 13, 15, 10, 2, 3, 8, 1, 0, 7, 5, 9],
    [4, 10, 9, 2, 13, 8, 0, 14, 6, 11, 1, 12, 7, 15, 5, 3]
]


def binary(value):
    bits = f"{value:032b}"
    return " ".join(bits[i:i + 4] for i in range(0, 32, 4))


def gost(text):

    # Переводим текст в байты по таблице из Приложения Б
    data = text.encode("cp1251")

    # Первые 8 символов - исходный 64-битный блок
    block = data[:8]

    # Следующие 4 символа - первый подключ X0
    key = data[8:12]

    # Делим исходный блок пополам
    L0 = int.from_bytes(block[:4], "big")
    R0 = int.from_bytes(block[4:], "big")

    # Первый подключ
    X0 = int.from_bytes(key, "big")


    # 1. R0 + X0 по mod 2^32
    value = (R0 + X0) % (2 ** 32)


    # 2. Блок подстановки
    result = 0

    for i in range(8):
        shift = 28 - 4 * i
        part = (value >> shift) & 0xF

        result = (result << 4) | S[i][part]


    # 3. Циклический сдвиг на 11 бит влево
    result = ((result << 11) | (result >> 21)) & 0xFFFFFFFF


    # 4. R1 = f(R0, X0) XOR L0
    R1 = result ^ L0


    print("Исходный блок:", text[:8])
    print("Первый подключ X0:", text[8:12])

    print("\nL0:")
    print(binary(L0))

    print("\nR0:")
    print(binary(R0))

    print("\nX0:")
    print(binary(X0))

    print("\nR0 + X0 mod 2^32:")
    print(binary(value))

    print("\nПосле блока подстановки:")
    print(binary(
        ((result >> 11) | (result << 21)) & 0xFFFFFFFF
    ))

    print("\nf(R0, X0) после сдвига на 11 бит:")
    print(binary(result))

    print("\nR1 = f(R0, X0) XOR L0:")
    print(binary(R1))

    return R1


gost(text)