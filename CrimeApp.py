from Tkinter import *
import ttk
import pg8000
import folium
from folium import plugins
import webbrowser
import os
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import datetime
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter, DayLocator, HourLocator
import pandas as pd
import getpass

#login = input('login: ')
#secret = getpass.getpass('password: ')

credentials = {'user'    : 'zsmialek',
               'password': 'TheH@mLun@',
               'database': 'csci403',
               'host'    : 'flowers.mines.edu'}

try:
    db = pg8000.connect(**credentials)
except pg8000.Error as e:
    print('Database error: ', e.args[2])
    exit()

# uncomment next line if you want every insert/update/delete to immediately                                                  
# be applied; you can remove all db.commit() and db.rollback() statements
#db.autocommit = True

cursor = db.cursor()
master_results = []
traffic_offense_per_hour = []

# Populate the various lists from the tables in the database
cursor.execute("""SELECT DISTINCT offense_category_name FROM description
WHERE is_crime = '1' ORDER BY offense_category_name""")
results = cursor.fetchall()
cCrimes = ()
for row in results:
    cCrimes = cCrimes + (row[0],)

cursor.execute("""SELECT DISTINCT offense_category_name FROM description
WHERE is_traffic = '1' ORDER BY offense_category_name""")
results = cursor.fetchall()
tCrimes = ()
for row in results:
    tCrimes = tCrimes + (row[0],)

cursor.execute("""SELECT DISTINCT neighborhood_id FROM offense ORDER BY neighborhood_id""")
results = cursor.fetchall()
neighborhoods = ()
for row in results:
    neighborhoods = neighborhoods + (row[0].replace('-',' ').title(),)

cursor.execute("""SELECT DISTINCT precinct_id FROM offense ORDER BY precinct_id""")
results = cursor.fetchall()
precincts = ()
for row in results:
    precincts = precincts + (row[0],)

# Define the functions for different events
def toggleCrime(*args):
    if CorT.get() == 'crime':
        CorTBox.config(textvariable=cCrimeNames)
        CorTBox.config(values=cCrimes)
        CorTBox.set(cCrimes[0])
    else:
        CorTBox.config(textvariable=tCrimeNames)
        CorTBox.config(values=tCrimes)
        CorTBox.set(tCrimes[0])
    root.update()


def toggleSearch(*args):
    if NorP.get() == 'neighborhood':
        lblNorPBox.config(text='Select the neighborhood:')
        NorPBox.config(textvariable=neighborhoodNames)
        NorPBox.config(values=neighborhoods)
        NorPBox.set(neighborhoods[0])
    else:
        lblNorPBox.config(text='Select the precinct:')
        NorPBox.config(textvariable=precinctNames)
        NorPBox.config(values=precincts)
        NorPBox.set(precincts[0])
    root.update()


def submit(*args):
    #query_statment = "SELECT geo_lat, geo_lon FROM offense WHERE is_traffic IS TRUE LIMIT 100"
    query = "SELECT c.geo_lat, c.geo_lon, d.offense_type_name FROM crime c, description d WHERE d.offense_category_name = %s AND d.offense_code = c.offense_code AND d.offense_code_extension = c.offense_code_extension"
    if CorT.get() == 'crime':
        query = query + " AND c.is_crime = '1'"
    else:
        query = query + " AND c.is_traffic = '1'"
    if NorP.get() == 'neighborhood':
        query = query + " AND c.neighborhood_id = %s"
        place = NorPBox.get().lower().replace(' ', '-')
    else:
        query = query + " AND c.precinct_id = %s"
        place = NorPBox.get()

    cursor.execute(query, (CorTBox.get(), place))
    #cursor.execute(query_statment)
    result = cursor.fetchall()
    data_point = list(result)

    for data in data_point:
        master_results.append(data)

    #if not result:
    #    print('no results')
    #for row in result:
    #    print(row)


def refresh(*args):
    root.update()


def open_web_broswer():

    for files in os.listdir(os.getcwd()):
        if files.endswith(".html"):
            path = os.path.realpath(files)
            webbrowser.open('file://' + path)


def heat_map(lat_longs):
    points = []
    name = "search_HeatMapResults.html"

    heat = folium.Map(location=[39.7392, -104.9903], zoom_start=13)

    for temp in lat_longs:
        points.append(temp[0:2])

    heat.add_children(plugins.HeatMap(points))
    heat.save(name)


def marker_map(lat_long):

    map_marker = folium.Map(location=[39.7392, -104.9903], zoom_start=13)
    name = "search_MarkerResults.html"

    for data in lat_long:
        folium.Marker(data[0:2], popup=data[2]).add_to(map_marker)

    map_marker.save(name)


def traffic_by_hour():
    query_traffic_occurence ="select count(incident_date), date_trunc('day',incident_date) from offense where is_traffic is true group by date_trunc('day',incident_date) order by date_trunc('day', incident_date) asc;"
    print(query_traffic_occurence)
    try:
        cursor.execute(query_traffic_occurence)
    except pg8000.Error as e:

        print('Database error traffic by hour query: ', e.args[2])

    hourly_traffic = cursor.fetchall()

    hourly_traffic = list(hourly_traffic)

    for by_hour in hourly_traffic:
        traffic_offense_per_hour.append(by_hour)


def traffic_offense_per_hour_plot(offense_per_hour):

    traffic_by_hour()
    years = YearLocator()
    month = MonthLocator()
    day_loc = DayLocator()
    hours = HourLocator()

    day_format = DateFormatter('%d%m%Y%H')

    offense_number = []
    year_of_offense = []

    fig, ax = plt.subplots()

    for dates in offense_per_hour:
        print(dates)
        offense_number.append(dates[0])
        d = datetime.datetime.strftime(dates[1], "%d%m%Y%H")
        year_of_offense.append(d)

    ax.plot_date(year_of_offense, offense_number)
    ax.set_title('Rate of Traffic Offense by Day')
    ax.xaxis.set_major_locator(day_loc)
    ax.xaxis.set_major_formatter(day_format)
    ax.xaxis.set_minor_locator(hours)
    ax.autoscale_view()

    ax.fmt_xdate = DateFormatter('%Y%m%d%H')
    ax.fmt_ydate = offense_number

    ax.grid(True)
    fig.autofmt_xdate()
    plt.show()

# Set up the window

root = Tk()
root.title('Find Crime. Stop Crime.')

frame = ttk.Frame(root, padding=(5,5,12,12))
frame.grid(column=0, row=0, sticky=(N,W,E,S))
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0,weight=1)


# Define the string variables
cCrimeNames = StringVar()
tCrimeNames = StringVar()
neighborhoodNames = StringVar()
precinctNames = StringVar()
CorT = StringVar()
NorP = StringVar()


# Create all the objects in the frame
lblCorT = ttk.Label(frame, text='Search for:')
crimeButton = ttk.Radiobutton(frame, text='Crime', variable=CorT, value='crime', state=ACTIVE, command=toggleCrime)
trafficButton = ttk.Radiobutton(frame, text='Traffic', variable=CorT, value='traffic', command=toggleCrime)
lblCorTBox = ttk.Label(frame, text='Filter by:')
CorTBox = ttk.Combobox(frame, values=cCrimes, textvariable=cCrimeNames, state='readonly')
lblNorP = ttk.Label(frame, text='Search Method:')
neighborhoodButton = ttk.Radiobutton(frame, text='Neighborhood', variable=NorP, value='neighborhood', state=ACTIVE, command=toggleSearch)
precinctButton = ttk.Radiobutton(frame, text='Precinct', variable=NorP, value='precinct', command=toggleSearch)
lblNorPBox = ttk.Label(frame, text='Select the neighborhood:')
NorPBox = ttk.Combobox(frame, values=neighborhoods, textvariable=neighborhoodNames, state='readonly')
submitButton = ttk.Button(frame, text='Submit', command=submit)

# Place all the objects in the right place
lblCorT.grid(row=0, sticky=W)
crimeButton.grid(row=1, sticky=W)
trafficButton.grid(row=2, sticky=W)
lblCorTBox.grid(row=3, sticky=W)
CorTBox.grid(row=4)
lblNorP.grid(row=0, column=1, sticky=W)
neighborhoodButton.grid(row=1, column=1, sticky=W)
precinctButton.grid(row=2, column=1, sticky=W)
lblNorPBox.grid(row=3, column=1, sticky=W)
NorPBox.grid(row=4, column=1, sticky=N)
submitButton.grid(row=5, column=0, columnspan=2)

# Set the initial values
CorT.set('crime')
CorTBox.set(cCrimes[0])
NorP.set('neighborhood')
NorPBox.set(neighborhoods[0])

# Give everyone some space
for child in frame.winfo_children():
    child.grid_configure(padx=5, pady=3)

CorTBox.bind('<<ComboboxSelected>>', refresh)
NorPBox.bind('<<ComboboxSelected>>', refresh)
root.bind('<Return>', submit)

mainloop()
marker_map(master_results)
heat_map(master_results)
#traffic_offense_per_hour_plot(traffic_offense_per_hour)
open_web_broswer()
