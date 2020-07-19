#import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask
#import flask dependencies, this always comes last 
from flask import Flask, jsonify
#import database engine/database file
#add connect_args to prevent flask from looking at the same thread as the previous one
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})
#reflect database into our classes
Base = automap_base()
#reflect the tables
Base.prepare(engine, reflect=True)
#create variables for each class
Measurement = Base.classes.measurement
Station = Base.classes.station
#Create a session link
session = Session(engine)
#define the Flask App
##create the Flask App called "app"
app = Flask(__name__)
#When running flask later on make sure to run the command where the files are found i.e. the surfs_up folder
#Build the app routes
##Build the welcome route, the "root"
@app.route('/')
###Create a welcome function
###Add precipitation, station, tobs and temp routes
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:<br/>
    /api/v1.0/precipitation<br/>
    /api/v1.0/stations<br/>
    /api/v1.0/tobs<br/>
    /api/v1.0/temp/start/end<br/>
    ''')
##Build the precipitation route
@app.route("/api/v1.0/precipitation")
###Define the precipitation function
###Create a dictionary with the date as key and the precipitation as value
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
      filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
##Build the station route
@app.route("/api/v1.0/stations")
###Define the stations function
def stations():
####Query the database for all the stations
    results = session.query(Station.station).all()
####Unravel using the np.ravel() function
    stations = list(np.ravel(results))
    return jsonify(stations=stations)
##Build the temperature observations (tobs) route
@app.route("/api/v1.0/tobs")
###Define the tobs function
def temp_monthly():
####calculate the date one year ago from the last date in the database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
####Query the prim station for all temp observations from the previous year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
#unravel the results into a one-dimensional array using np.ravel()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)
##Build the statistics analysis route
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
###Define the tobs function
def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]           
    if not end:
        results = session.query(*sel).\
	        filter(Measurement.date <= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
	    filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)