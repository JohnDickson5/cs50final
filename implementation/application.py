import csv
import datetime
import os
import requests

from cs50 import SQL
from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from SPARQLWrapper import SPARQLWrapper, JSON
from tempfile import mkdtemp
from threading import Thread
from werkzeug.utils import secure_filename

from helpers import allowed_file, getData, editDB, queryURI

UPLOAD_FOLDER = '/uploads'


# Configure application
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the folder when setting up your app
os.makedirs(os.path.join(app.instance_path, 'CSVuploads'), exist_ok=True)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///data.db")


@app.route("/")
def index():
    """Show homepage form"""
    # Forget session information
    session.clear()

    return render_template("index.html")


"""Run list query and add data to database"""
def queryList(csvFile, InstanceOf, filename):
    # Get a timestamp to identify the job
    jobTime = datetime.now()

    # Interate through the lines in the csv file, querying wikidata
    for row in csvFile:
        results = queryURI(InstanceOf, row.rstrip())
        failures = 0
        # Make sure the result of the query was not empty
        if results["results"]["bindings"]:
            # Index into the results and chop the uri off of its address
            uri = results["results"]["bindings"][0]['item']['value'][31:]
            # If the uri was obtained, get the data associated with it, and add it to the database
            if uri:
                data = getData(uri)
                editDB(InstanceOf, uri, data)
                # Add the timestamp to the row
                db.execute('UPDATE :table SET "job" = :jobID WHERE id = :id',
                            table=InstanceOf, jobID=jobTime, id=uri)

    csvFile.close()

    return True


@app.route("/stats", methods=["POST"])
def retrieve():
    # Select all the data that currently has a job timestamp from the appropriate table
    everything = db.execute("SELECT * FROM :table WHERE job IS NOT NULL", table=session["listType"])

    # If nothing was select, render an error page
    if not everything:
        return render_template("error.html", error="Wikidata failed to return any results for your list")

    return render_template("stats.html", everything = everything)


@app.route("/lquery", methods=["POST"])
def listQuery():
    # Check that the post request contains a file
    if 'csvFile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['csvFile']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.instance_path, 'CSVuploads', filename))
        filePath = os.path.join(app.instance_path, 'CSVuploads', filename)
    else:
        return render_template("error.html", error="Failed to upload file")

    session["listType"] = request.form.get("LQInstanceOf")

    # Remove previous job data
    db.execute(f'UPDATE {session["listType"]} SET "job"=NULL WHERE "job" IS NOT NULL')

    csvFile = open(filePath, "r")

    # Thread the slow process of editing the db so that the request does not time out
    thr = Thread(target=queryList, args=[csvFile, session["listType"], filename])
    thr.start()

    return render_template("rest.html")


@app.route("/squery", methods=["POST"])
def singleQuery():
    InstanceOf = request.form.get("SQInstanceOf")
    NameTitle = request.form.get("NameTitle")

    # Check that the user filled out the form
    if InstanceOf and NameTitle:
        """Get a single URI from a user search"""

        results = queryURI(InstanceOf, NameTitle)

        # Check that query did not return an empty result
        if results["results"]["bindings"]:
            uri = results["results"]["bindings"][0]['item']['value'][31:]
            # Check that a uri was retrieved before querying for the data and adding it
            if uri:
                data = getData(uri)
                editDB(InstanceOf, uri, data)
                return render_template("query.html", data=data["results"]["bindings"])
        else:
            return render_template("error.html", error="Could not retrieve wikidata uri")

    return render_template("error.html", error="You must submit a category and search next (a name or title)")