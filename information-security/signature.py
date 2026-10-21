alphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

p = 5
q = 97

n = p * q
phi = (p - 1) * (q - 1)

d = 11
e = pow(d, -1, phi)


def hash_text(text, h0=23):
    h = h0

    for letter in text.upper():
        m = alphabet.index(letter) + 1
        h = (h + m) ** 2 % n

    return h


def signature(text, verify=False, s=None):
    h = hash_text(text)

    if verify:
        h_check = pow(s, e, n)
        return h == h_check

    return pow(h, d, n)


text = "Хачатурян"

h = hash_text(text)
s = signature(text)
check = signature(text, verify=True, s=s)

print("Сообщение:", text)
print("Хэш:", h)
print("ЭЦП:", s)
print("Проверка ЭЦП:", check)