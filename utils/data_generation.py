import random
import string

SPECIAL = list("@$#-_!%*?&\"()/{}[]~':.;Ñ°^")  # все символы из скриншота

def strong_password(length: int = 12) -> str:
    """
    Генерирует пароль, удовлетворяющий требованиям:
    - минимум 8 символов
    - латиница
    - обе буквы в разных регистрах
    - хотя бы одна цифра
    - хотя бы один спец-символ из списка
    """
    if length < 8:
        raise ValueError("Минимальная длина пароля — 8 символов")

    # Гарантируем присутствие каждой категории
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(string.digits),
        random.choice(SPECIAL),
    ]

    # Остальное набираем случайно
    pool = string.ascii_letters + string.digits + "".join(SPECIAL)
    password += random.choices(pool, k=length - len(password))

    random.shuffle(password)
    return "".join(password)
