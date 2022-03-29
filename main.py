#!/usr/bin/env python3

import csv
import json
from flask import Flask, render_template, request
import flask
import requests

CSV_FILE_PATH = "./utils/2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv"
API = "https://api-adresse.data.gouv.fr/search/?q="
OPERATORS = {
    "20801": "Orange",
    "20810": "SFR",
    "20815": "Free",
    "20820": "Bouygue"
}

app = Flask(__name__)
def get_result(csv_file, address_properties, closest, index):
    result = {}
    for row in csv_file:
        if row[index] == closest:
            result[OPERATORS[row[0]].lower()] = {
                "address": address_properties["label"],
                "2G": True if row[3] == "1" else False,
                "3G": True if row[4] == "1" else False,
                "4G": True if row[5] == "1" else False
            }
            break
    return result


def get_closest(csv_file, lambert_x, lambert_y):
    x_list = [row[1] for row in csv_file]
    y_list = [row[2] for row in csv_file]
    closest_x = min(x_list, key=lambda x: abs(int(x)-lambert_x))
    closest_y = min(y_list, key=lambda x: abs(int(x)-lambert_y))
    return (closest_x, closest_y)


@app.route('/search', methods=['POST'])
def search():
    csv_file = list(csv.reader(open(CSV_FILE_PATH, "r"), delimiter=";"))[1:-1]
    input = request.form["address"].replace(' ', '+')
    info = requests.get(API + input + "&limit=1").content.decode("utf-8")
    print(info)
    address_properties = json.loads(info)["features"][0]["properties"]
    lambert_x = address_properties["x"]
    lambert_y = address_properties["y"]
    x, y = get_closest(csv_file, lambert_x, lambert_y)
    result = get_result(csv_file, address_properties, y, 2)
    result.update(get_result(csv_file, address_properties, x, 1))
    return(result)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


app.run()
