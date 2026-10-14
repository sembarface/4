ru = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
en = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

p = 5
q = 97

n = p * q
phi = (p - 1) * (q - 1)

d = 11
e = pow(d, -1, phi)


def rsa(text, decrypt=False, language="ru"):
    alphabet = ru if language == "ru" else en

    if decrypt:
        result = ""
        for number in text.split():
            m = pow(int(number), d, n)
            if m == 0:
                result += " "
            else:
                result += alphabet[m - 1]
        return result

    result = []
    for letter in text.upper():
        if letter == " ":
            result.append("0")
        else:
            m = alphabet.index(letter) + 1
            result.append(str(pow(m, e, n)))

    return " ".join(result)


text = "ХВГ"

encrypted = rsa(text, decrypt=False)
decrypted = rsa(encrypted, decrypt=True)

print("Открытый ключ:", (e, n))
print("Закрытый ключ:", (d, n))
print("Исходное сообщение:", text)
print("Зашифровано:", encrypted)
print("Расшифровано:", decrypted)