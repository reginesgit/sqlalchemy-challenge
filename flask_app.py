import numpy as np

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
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/yyyy.mm.dd<br/>"
        f"/api/v1.0/yyyy.mm.dd,yy.mm.dd<br/>"
    )


# Return a list of all precipitation readings
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all precipitation readings
    results = session.query(Measurements.date, Measurements.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_precipitations
    all_precips = []
    for date, prcp in results:
        precips_dict = {}
        precips_dict["date"] = date
        precips_dict["precipitation"] = prcp
        all_precips.append(precips_dict)

    
    return jsonify(all_precips)


# Return a list of station data including the name and ID of each station
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Stations.name, Stations.id).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for name, id in results:
        station_dict = {}
        station_dict["name"] = name
        station_dict["id"] = id
        all_stations.append(station_dict)

    return jsonify(all_stations)


# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for most active station
    most_active = session.query(Measurements.station).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc()).first()    

    # Convert tuple 'most_active' to list and extract first value ('answer')
    most_active_list = list(np.ravel(most_active))
    answer = most_active_list[0]

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the observed temperatures for the calculated date range.
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == answer).\
    filter(Measurements.date <= '2017-08-23').filter(Measurements.date >= year_ago)


    session.close()

    # Create a dictionary from the row data and append to a list of all_temperatures
    all_temps = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["observed temperature"] = tobs
        all_temps.append(temp_dict)

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(all_temps) 

# Return a JSON list of the minimum temperature, the average temperature, and the 
# max temperature for a range of dates with a given start date.
@app.route("/api/v1.0/<start>")
def calc_temp(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for minimum, average and maximum temperatures on or after a given start date
    results = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start).all()
     
    session.close()
    
    # Unravel results from tuples to list form
    results_list = list(np.ravel(results))

    # Save values for dictionary below
    min = results_list[0]
    avg = results_list[1]
    max = results_list[2]

    # Create dictionary for return of labeled values
    dict = {
    "Minimum Temp.": min,
    "Average Temp.": avg,
    "Maximum Temp.": max
    }

    # Return the dictionary
    return dict


# Return a JSON list of the minimum temperature, the average temperature, and the 
# max temperature for a given start-end range.
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start_date, end_date):
    
    session = Session(engine)
    
    values = session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
        filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).all()

    session.close()
    
    values_list = list(np.ravel(values))

    min_tmp = values_list[0]
    avg_tmp = values_list[1]
    max_tmp = values_list[2]

    dictionary = {
    "Minimum Temp.": min_tmp,
    "Average Temp.": avg_tmp,
    "Maximum Temp.": max_tmp
    }

    return dictionary


if __name__ == '__main__':
    app.run(debug=True)
