# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/start<br/>"
        f"/api/v1.0/date_range/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Retrieve last 12 months of precipitation data
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).all()
    session.close()

    #Convert to dictionary
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        precipitation.append(prcp_dict)
    
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    #Retrieve list of stations
    results = session.query(Station.station).all()
    session.close()

    #convert list of tuples to normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    #Query the dates and temperature observations of the most-active station for the previous year of data.
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()
    session.close()

    temperature = []
    for station, date, tobs in results:
        temp_dict = {}
        temp_dict["station"] = station
        temp_dict["date"] = date
        temp_dict["temp"] = tobs
        temperature.append(temp_dict)
    
    return jsonify(temperature)

@app.route("/api/v1.0/start_date/<date>")
def get_date(date):
    session = Session(engine)

    #Return JSON list with min, avg, and max for dates greater or equal to start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= date).all()
    session.close()

    dates = []
    for min, avg, max in results:
        date_dict={}
        date_dict["min"] = min
        date_dict["avg"] = avg
        date_dict["max"]= max
        dates.append(date_dict)

    return jsonify(dates)

@app.route("/api/v1.0/date_range/<start>/<end>")
def get_dates(start, end):
    session = Session(engine)

    #Return JSON list with min, avg, and max for dates between start and end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    dates = []
    for min, avg, max in results:
        date_dict={}
        date_dict["min"] = min
        date_dict["avg"] = avg
        date_dict["max"]= max
        dates.append(date_dict)   

    return jsonify(dates) 


if __name__ == '__main__':
    app.run(debug=True)

#################################################
