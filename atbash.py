RU = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
EN = "abcdefghijklmnopqrstuvwxyz"


def atbash(text, mode="encrypt"):
    # Для Атбаша зашифровка и расшифровка одинаковы.
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
        new_char = alphabet[-index - 1]

        if char.isupper():
            new_char = new_char.upper()

        result += new_char

    return result


text = "Старый Бог здесь"
cypher = atbash(text, mode="encrypt")
print(cypher)
print(atbash(cypher, mode="decrypt"))
