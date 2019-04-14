import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, distinct

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
M = Base.classes.measurement
S = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Homework 10 Landing Page"""
    return (
        f"This is Ragavendar Kumar's Homework 10 - SQLAlchemy and Flask<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
        )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(M.date, M.prcp).all()

    all_data = []
    for date, prcp in results:
        prcp_date_dict = {}
        prcp_date_dict["date"] = date
        prcp_date_dict["prcp"] = prcp
        all_data.append(prcp_date_dict)

    return jsonify(all_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(S.station).group_by(S.station)

    all_data = []
    for station in results:
        station_dict = {}
        station_dict["station"] = station
        all_data.append(station_dict)

    return jsonify(all_data)

#Code for calculating last date and date_1_year before:
from datetime import datetime, timedelta

data = engine.execute('SELECT MAX(date) FROM ' '"measurement"' '').fetchall() #Get last date in table
last_date_str = data[0][0]

last_date_frmt = datetime.strptime(last_date_str, '%Y-%m-%d').date() #Convert datestring to datetime
from dateutil.relativedelta import relativedelta
date_1_year_ago = last_date_frmt - relativedelta(years=1)


@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(M.date, M.tobs).order_by(M.date.asc()).filter((M.date >= date_1_year_ago))

    all_data = []
    for date, tobs in results:
        tobs_date_dict = {}
        tobs_date_dict["date"] = date
        tobs_date_dict["tobs"] = tobs
        all_data.append(tobs_date_dict)

    return jsonify(all_data)

@app.route("/api/v1.0/<starting_date>")
def calc_temps1(starting_date):   
    results = session.query(func.min(M.tobs), func.avg(M.tobs), func.max(M.tobs)).filter(M.date >= starting_date).all()
    
    all_data = []
    
    for tmin, tave, tmax in results:
        temp_dict = {}
        temp_dict["tmin"] = tmin
        temp_dict["tave"] = tave
        temp_dict["tmax"] = tmax
        all_data.append(temp_dict)
    
    return jsonify(all_data)

@app.route("/api/v1.0/<start_date>/<end_date>")
def calc_temps2(start_date, end_date):   
    results = session.query(func.min(M.tobs), func.avg(M.tobs), func.max(M.tobs)).filter(M.date >= start_date).filter(M.date <= end_date).all()
    
    all_data = []
    
    for tmin, tave, tmax in results:
        temp_dict = {}
        temp_dict["tmin"] = tmin
        temp_dict["tave"] = tave
        temp_dict["tmax"] = tmax
        all_data.append(temp_dict)
    
    return jsonify(all_data)

if __name__ == '__main__':
    app.run(debug=True)