import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

############################################################################
# Database Setup
############################################################################

engine = create_engine("sqlite:///hawaii.sqlite")
Base = automap_base()
Base.prepare(engine,reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

###########################################################################
# Flask Setup
###########################################################################

app = Flask(__name__)

###########################################################################
# Flask Routes
###########################################################################

@app.route("/")
def welcome():
     return (
        f"This is the Climate Analysis API<br/>"
        f"Copy and paste in the browser any of the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"Note: Type the start date in the form of %mm-%dd<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"Note: API request takes two parameters: Start date / End date<br/>"
        f"Type dates in the form of %yyyy-%mm-%dd<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
   last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).all()
   prec = {date: prcp for date, prcp in precipitation}
   return jsonify(prec)

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(Station.station)
    stations_df = pd.read_sql_query(stations_list.statement, session.bind)
    return jsonify(stations_df.to_dict())

@app.route("/api/v1.0/tobs")
def tobs():
    last_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= last_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/<start>", methods=['GET'])
def daily_normals(start):
    """Daily Normals.
        Args:
            date (str): A date string in the format '%m-%d'
        Returns:
            TMIN, TAVE, and TMAX
    """
    sel = (func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
    result = session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == start).all()

    #convert list of tuples into normal list
    all_calculations = list(np.ravel(result))

    return jsonify(all_calculations)

@app.route("/api/v1.0/<start_date>/<end_date>", methods=['GET'])
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
    Returns:
        TMIN, TAVE, and TMAX
    """
    startend_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    #convert list of tuples into normal list
    startend_calculations = list(np.ravel(startend_results))

    return jsonify(startend_calculations)

#####################################################################
# Launch app
#####################################################################

if __name__ == "__main__":
    app.run(debug=True)