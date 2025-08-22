import random

# def generateOTP():
#     digits = "0123456789"
#     return "".join(random.choices(digits, k=4))

# print("OTP:", generateOTP())




def generateOTP():
    digits = "0123456789"
    otp = ""
    for _ in range(4):
        otp += random.choice(digits)
    return otp

print("OTP:", generateOTP())

