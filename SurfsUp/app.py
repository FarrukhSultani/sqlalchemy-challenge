
# Import dependencies
import datetime as dt
import numpy as np
import pandas as pd
import datetime as dt
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)


Measurement = Base.classes.measurement
Station = Base.classes.station
# create an app
app = Flask(__name__)

# Define homepage route and list all available routes
@app.route("/")
def home():
    return (
        f"Welcome to the Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# Define precipitation route and convert results to dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
# Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
 # Query for date and precipitation for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year).all()
    session.close()
# Convert query results to a dictionary
    prcp_data = {date: prcp for date, prcp in results}
    return jsonify(prcp_data)

# Define stations route and return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    session.close()
    # Convert list of tuples to JSON list
    stations_data = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations_data.append(station_dict)
    return jsonify(stations_data)

# Define tobs route and return a JSON list of temperature observations for the previous year
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the most active station for the last 12 months of temperature observation data
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    session.close()
    # Convert list of tuples to JSON list
    tobs_data = list(np.ravel(results))
    return jsonify(tobs_data)

# Define start route and return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    # Define the start and end dates
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
    # Calculate the minimum, average, and maximum temperatures for the start date and beyond
    temperatures = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    session.close()
    # Convert list of tuples to JSON list
    temperatures_list = list(np.ravel(temperatures))
    return jsonify(temperatures_list)
if __name__ == '__main__':
    app.run()