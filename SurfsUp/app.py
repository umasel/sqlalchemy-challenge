# Import the dependencies.

# Import the dependencies.

import warnings
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables

Base.prepare(autoload_with=engine)

# Save references to each table

Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link)

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# all API routes available

@app.route("/")
def welcome():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        "<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        "<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        "<a href='/api/v1.0/temp/start=<start>'>/api/v1.0/temp/start=<start></a><br>"
        "<strong>Sample you have to choose start date Example:</strong> /api/v1.0/temp/start=2017-01-01<br/>"
        "<a href='/api/v1.0/temp/start=<start>/&end=<end>'>/api/v1.0/temp/start=<start>/&end=<end></a><br>"
        "To access temperature data from start date to end date, use the following format: /api/v1.0/temp/start=YYYY-MM-DD/&end=YYYY-MM-DD<br/>"
        
        "<strong>Example:</strong> /api/v1.0/temp/start=2017-01-01/&end=2017-12-31"
    )

# API route that shows precipitation for every day for the most recent year

@app.route("/api/v1.0/precipitation")
def get_precipitation():

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=234)


    precipitation_query = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    
    session.close()

    precipitation_dict = {date: prcp for date, prcp in precipitation_query}

    return jsonify(precipitation_dict)

# API route that shows a dictionary of all the stations in the table

@app.route("/api/v1.0/stations")
def get_stations():

    stations_query = session.query(Measurement.station).\
        group_by(Measurement.station).all()

    station_dict = [{'station': station[0]} for station in stations_query]

    session.close()

    return jsonify(station_dict)

# API route that shows most recent year's temperature for station: USC00519281

@app.route("/api/v1.0/tobs")
def get_tobs():

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=234)

    tobs_query = session.query(Measurement.tobs, Measurement.date).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(Measurement.date >= prev_year).all()

    session.close()

    tobs_dict = {date: tobs for tobs, date in tobs_query}

    return jsonify(tobs_dict)

# API route that shows most min temperature, the avg temperature, and the max temperature of Hawaii starting in 2015 to most recent date

@app.route("/api/v1.0/temp/start=<start>")
def start_temperature(start):
     # Convert the start date string to a datetime object
    try:
        start = dt.datetime.strptime(start, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
        
    session.close()
    
    #Store list of tmin, tmax, tavg
    list_data = []
    for result in results:
        list_dict = {}
        list_dict["TMIN"] = result[0]
        list_dict["TMAX"] = result[1]
        list_dict["TAVG"] = round(result[2],2)
        list_data.append(list_dict)
        
    response_data = {"Your selected date": str(start), "Here is the temperature data": list_data}
    
    return jsonify(response_data)

@app.route("/api/v1.0/temp/start=<start>/&end=<end>")
def temperature_range(start, end ):
    try:
        # Convert start and end date strings to datetime objects
        start = dt.datetime.strptime(start, "%Y-%m-%d").date()
        end = dt.datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    
    session.close()
    
    temperature_range = []
    for result in results:
        temperature_dict = {}
        temperature_dict["TMIN"] = result[0]
        temperature_dict["TMAX"] = result[1]
        temperature_dict["TAVG"] = round(result[2],2)
        temperature_range.append(temperature_dict)
        
    response_date = {"Your selected date": f"{start} to {end}", "Here is the temperature data": temperature_range}    
    return jsonify(response_date)
    

app.run(debug=True)