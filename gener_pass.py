'''
generate a random password from the systems
'''
import random

def generate_password():
    letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    special_characters = "!@#$%^&*()"

    all_characters = letters + digits + special_characters

    password = ""
    for i in range(16):
        password = password + random.choice(all_characters)

    return password

# Generate password
print(" Your password is:", generate_password())
