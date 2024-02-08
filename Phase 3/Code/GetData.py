from Login import Login, sessionObject
from bs4 import BeautifulSoup
import re

patterns = [re.compile(r'https://bama.ir/car/detail\-[A-Za-z0-9]+\-([A-Za-z0-9]+)\-.+'),
            re.compile(r'https://bama.ir/car/detail\-[A-Za-z0-9]+\-[A-Za-z0-9]+\-([A-Za-z0-9]+)\-.+'), 
            re.compile(r'https://bama.ir/car/detail\-[A-Za-z0-9]+\-[A-Za-z0-9]+\-[A-Za-z0-9]+\-(.+)\-\d{4}'),
            re.compile(r'(\d{4})'),
            re.compile(r'([0-9]+),([0-9]+)')]
            # index 0 for Company
            # index 1 for Car (model)
            # index 2 for tream
            # index 3 for year
            # index 4 for kilometer


def get_data(i):
    status = Login()

    if status == 200:
        Companies, Year, Model, Tream, Prices, Kilometer = [], [], [], [], [], []
        Finaldata = []

        extract = sessionObject.get(f"http://utproject.ir/bp/Cars/page{i}.php")
        soup = BeautifulSoup(extract.text, "html.parser")
        cars = soup.find_all(class_="car-list-item-li")
        kilometerDivs = soup.find_all(class_="car-func-details")

        for kmd in kilometerDivs:
            tmp = kmd.span
            if re.search(patterns[4], str(tmp)):
                km = re.findall(patterns[4], str(tmp))[0]
                Kilometer.append(int(km[0]+km[1]))
            else:
                Kilometer.append(0)

        for car in cars:
            Companies.append(re.findall(patterns[0], car["data-url"])[0])
            Year.append(re.findall(patterns[3], car["data-url"])[-1])
            tmp = re.findall(patterns[1], car["data-url"])

            if tmp:
                Model.append(tmp[0])
            else:
                Model.append(None)

            tmp = re.findall(patterns[2], car["data-url"])
                        
            if tmp:
                Tream.append(tmp[-1])
            else:
                Tream.append(None)

            tmp = car.p["class"][-1]
            
            if tmp == "single-price":
                Prices.append(car.p.span["content"])
            else:
                Prices.append(-1)

        for i in range(len(cars)):
            tmp = {"company" : Companies[i],
                    "car" : Model[i],
                    "tream" : Tream[i],
                    "kilometer" : Kilometer[i],
                    "year" : Year[i], 
                    "price" : Prices[i]}
            Finaldata.append(tmp)
    return Finaldata

def run():
    Data = []
    for i in range(0, 1):
        Data = Data + get_data(i)

    return Data