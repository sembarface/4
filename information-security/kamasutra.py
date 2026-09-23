RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
EN = "abcdefghijklmnopqrstuvwxyz"
import random

def make_pairs(alphabet):
    char_list = list(alphabet)
    random.shuffle(char_list)
    alphabet = ''.join(char_list)
    
    pairs = {}

    half = len(alphabet) // 2

    if len(alphabet) % 2 == 0:
        first = alphabet[:half]
        second = alphabet[half:]
    else:
        first = alphabet[:half]
        middle = alphabet[half]
        second = alphabet[half + 1:]
        pairs[middle] = middle

    for a, b in zip(first, second):
        pairs[a] = b
        pairs[b] = a

    return pairs


RU_PAIRS = make_pairs(RU)
EN_PAIRS = make_pairs(EN)


def kamasutra(text, mode="encrypt"):
    # Для этого шифра зашифровка и расшифровка одинаковы.
    result = ""

    for char in text:
        lower = char.lower()

        if lower in RU_PAIRS:
            new_char = RU_PAIRS[lower]
        elif lower in EN_PAIRS:
            new_char = EN_PAIRS[lower]
        else:
            result += char
            continue

        if char.isupper():
            new_char = new_char.upper()

        result += new_char

    return result


text = "Хачатурян Владимир"
cypher = kamasutra(text, mode="encrypt")
print(cypher)
print(kamasutra(cypher, mode="decrypt"))


print({tuple(sorted((key,value))) for key, value in EN_PAIRS.items()})
print('\n\n')
print({tuple(sorted((key,value))) for key, value in RU_PAIRS.items()})
