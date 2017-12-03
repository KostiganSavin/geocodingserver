import os
import datetime
import pandas as pd
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print(BASE_DIR)
app = Flask(__name__)

def get_data(filehandler):
    
    def lat(row):
        geolocator = Nominatim()
        location = geolocator.geocode(row.address)
        if location:
            row["latitude"] = location.latitude
            row["longitude"] = location.longitude
        return row

    source_data = pd.read_csv(filehandler)

    if "Address" in source_data.columns:
        source_data.rename(columns={"Address": "address"}, inplace=True)
        source_data = source_data.apply(lat, axis=1)
        source_data.rename(columns={"address": "Address"}, inplace=True)
        return source_data
    elif "address" in source_data:
        source_data = source_data.apply(lat, axis=1)
        return source_data
    else:
        return


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=["POST"])
def success():
    html_data = None
    if request.method == "POST":
        f = request.files["file"]

        data = get_data(f)
        if data is not None:
            html_data = data.to_html()
            global uploaded_file
            uploaded_file = os.path.join(BASE_DIR,
                                     "upload",
                                     ".".join([datetime.datetime.now().strftime(
                                     "%Y-%m-%d-%H-%M-%S"), "csv"]))
            data.to_csv(uploaded_file)
            return render_template("index.html", html_data=html_data, btn="download.html")    
        else:         
            html_data = "Please make sure your file contains Address column"
            return render_template("index.html", html_data=html_data)

@app.route("/download")
def download():
    return send_file(uploaded_file, attachment_filename="yourfile.csv", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)