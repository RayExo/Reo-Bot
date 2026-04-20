from random import choice

def generate_password(length=8) -> str:
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$_"
    password = ''.join(choice(letters) for i in range(length))
    return password
