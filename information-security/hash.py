alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

p = 5
q = 97
n = p * q


def hash_text(text, h0=23):
    h = h0

    for letter in text.upper():
        m = alphabet.index(letter) + 1
        h = (h + m) ** 2 % n

    return h


text = "Хачатурян"

h = hash_text(text)

print("Сообщение:", text)
print("Хэш:", h)