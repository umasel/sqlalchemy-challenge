import numpy as np
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify, Response


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
MS = Base.classes.measurement
ST = Base.classes.station

session = Session(engine)
session.query(MS.date).order_by(MS.date.desc()).first()
year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
session.close()
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
       
        
        "<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a><br/>"
        "<a href='/api/v1.0/stations'>/api/v1.0/stations</a><br/>"
        "<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a><br/>"
        "<a href='/api/v1.0/start'>/api/v1.0/start</a><br/>"
        "<a href='/api/v1.0/start_end'>/api/v1.0/start/end</a>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list """
    # Query all passengers
    results = session.query(MS.date, MS.prcp).all()

    session.close()

# Create a dictionary from the row data and append to a list 
    all_prcp = []
    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations """
    # Query all stations
    results = session.query(ST.station).group_by(ST.id).all()

    session.close()

    # Create a list of all_stations
    all_stations = []
    for result in results:
        st_dict = {}
        st_dict["station"] = result[0]
        all_stations.append(st_dict)
        
        return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations """
    # Query all dates and temperature observations of the most active station for the last year of data
    results = session.query(MS.date, MS.tobs).filter(MS.station == 'USC00519281').filter(MS.date >= year_ago).all()

    session.close()

    # Create a list of all_stations
    active_station = []
    for result in results:
        active_dict = {}
        active_dict["date"] = result[0]
        active_dict["tobs"] = result[1]
        active_station.append(active_dict)
        
        return jsonify(active_station)

@app.route("/api/v1.0/start")
def start():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of agg data"""
    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    results = session.query(func.min(MS.tobs), func.max(MS.tobs), func.avg(MS.tobs)).filter(MS.date >= year_ago).all()

    session.close()

    # Create a list of min, max, and avg
    agg_data = []
    for result in results:
        agg_dict = {}
        agg_dict["MIN"] = result[0]
        agg_dict["MAX"] = result[1]
        agg_dict["AVG"] = result[2]
        agg_data.append(agg_dict)
        
        return jsonify(agg_data)

@app.route("/api/v1.0/start_end")
def start_end():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    today = dt.datetime(2016, 8, 23)
    """Return a list of agg data"""
    # Query TMIN, TAVG, and TMAX for all dates between dates
    results = session.query(func.min(MS.tobs), func.max(MS.tobs), func.avg(MS.tobs)).filter(MS.date >= year_ago).filter(MS.date <= today).all()

    session.close()

    # Create a list of min, max, and avg
    agg_data = []
    for result in results:
        agg_dict = {}
        agg_dict["MIN"] = result[0]
        agg_dict["MAX"] = result[1]
        agg_dict["AVG"] = result[2]
        agg_data.append(agg_dict)
        
        return jsonify(agg_data)

if __name__ == '__main__':
    app.run(debug=True)
