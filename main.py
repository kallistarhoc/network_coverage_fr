#!/usr/bin/env python3

from operator import delitem
import sys
import csv
import math
import pyproj
import json
import numpy
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

def lamber93_to_gps(x, y):
	lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
	wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
	# x = 102980
	# y = 6847973
	long, lat = pyproj.transform(lambert, wgs84, x, y)
	return long, lat

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def find_nearest(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return array[idx]

@app.route('/search', methods=['POST'])
def search():
	input = request.form["address"].replace(' ', '+')
	info = requests.get(API + input + "&limit=1").content.decode("utf-8")
	address_properties = json.loads(info)["features"][0]["properties"]
	gps_coordinates = json.loads(info)["features"][0]["geometry"]["coordinates"]
	lambert_x = address_properties["x"]
	lambert_y = address_properties["y"]
	csv_file = csv.reader(open(CSV_FILE_PATH, "r"), delimiter=";")
	result = {
		"address": address_properties["label"],
		"operateur":"",
		"2G": False,
		"3G": False,
		"4G": False
	}
	for row in csv_file:
		if row[1] != 'X' and int(row[1]) >= lambert_x:
			result["operateur"] = OPERATORS[row[0]]
			result["2G"] = row[3]
			result["3G"] = row[4]
			result["4G"] = row[5]
			break
	return(result)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

app.run()