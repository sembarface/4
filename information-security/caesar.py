RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
EN = "abcdefghijklmnopqrstuvwxyz"


def caesar(text, key=3, mode="encrypt"):
    if mode == "decrypt":
        key = -key

    result = ""

    for char in text:
        lower = char.lower()

        if lower in RU:
            alphabet = RU
        elif lower in EN:
            alphabet = EN
        else:
            result += char
            continue

        index = alphabet.index(lower)
        new_char = alphabet[(index + key) % len(alphabet)]

        if char.isupper():
            new_char = new_char.upper()

        result += new_char

    return result


text = "Хачатурян Владимир"
cypher = caesar(text, key=1001, mode="encrypt")
print(cypher)
print(caesar(cypher, key=1001, mode="decrypt"))
