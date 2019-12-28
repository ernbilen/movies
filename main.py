import sqlite3 as sql
from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, layout
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.plotting import figure
#from bokeh.sampledata.movies_data import movie_path

conn = sql.connect('movies.db')
query = open('query.sql').read()
movies = psql.read_sql(query, conn)

#Godfather
movies.iloc[1356,24]=134900000
#LA Confidential
movies.iloc[4356,24]=64600000
#Alien
movies.iloc[1720,24]=81700000
#E.T.
movies.iloc[1960,24]=435110000
#Toy Story 2
movies.iloc[4490,24]=245850000
#Reservoir Dogs
movies.iloc[3251,24] = 2830000
#Jackie Brown
movies.iloc[4347,24] = 39600000
# Pulp Fiction
movies.iloc[3637,24] = 108000000

movies.iloc[1465,24]=134960000
movies.iloc[3435,24]=96900000
movies.iloc[4235,24]=57560000
movies.iloc[3551,24]=330450000
movies.iloc[3723,24]=75600000
movies.iloc[3709,24]=63650000
movies.iloc[4106,24]=128810000
movies.iloc[1811,24]=290270000
movies.iloc[1657,24]=461000000
movies.iloc[2062,24]=310000000
movies.iloc[801,24]=1830000
movies.iloc[4765,24]=171500000
movies.iloc[3911,24]=23000000
movies.iloc[3866,24]=141500000
movies.iloc[2690,24]=251300000
movies.iloc[2859,24]=217500000
movies.iloc[2892,24]=46900000
movies.iloc[3104,24]=130000000
movies.iloc[4050,24]=306000000
movies.iloc[4832,24]=77000000
movies.iloc[2744,24]=197000000
movies.iloc[2132,24]=179000000
movies.iloc[12303,24]=59000000
movies.iloc[4392,24]=4800000
movies.iloc[3658,24]=29000000
movies.iloc[5011,24]=40000000
movies.iloc[11535,24]=11000000
movies.iloc[4792,24]=37000000
movies.iloc[1528,24]=109000000
movies.iloc[4630,24]=217000000
movies.iloc[5076,24]=130000000
movies.iloc[3116,24]=205000000
movies.iloc[1426,24]=156000000
movies.iloc[3280,24]=101000000
movies.iloc[1609,24]=38200000
movies.iloc[1588,24]=23600000
movies.iloc[1676,24]=49000000
movies.iloc[1963,24]=6700000
movies.iloc[2372,24]=138500000
movies.iloc[1254,24]=61700000
movies.iloc[1970,24]=52700000
movies.iloc[2842,24]=184200000
movies.iloc[1553,24]=70600000
movies.iloc[2643,24]=172800000
movies.iloc[1839,24]=54700000
movies.iloc[2063,24]=21100000
movies.iloc[1341,24]=41300000
movies.iloc[1721,24]=37800000
movies.iloc[2473,24]=44000000
movies.iloc[1748,24]=106000000
movies.iloc[1286,24]=51700000
movies.iloc[2078,24]=108000000
movies.iloc[3996,24]=78600000
movies.iloc[2714,24]=106500000
movies.iloc[1873,24]=59000000
movies.iloc[2250,24]=87000000
movies.iloc[4793,24]=100000000
movies.iloc[1723,24]=83400000
movies.iloc[3903,24]=222500000

movies["color"] = np.where(movies["Oscars"] > 0, "orange", "grey")
movies["alpha"] = np.where(movies["Oscars"] > 0, 0.9, 0.25)
movies.fillna(0, inplace=True)  # just replace missing values with zero
movies["revenue"] = movies.BoxOffice.apply(lambda x: '{:,d}'.format(int(x)))
movies['BoxOffice']=movies['BoxOffice']/1000000
#movies.loc[movies['BoxOffice'] <10, 'BoxOffice'] = ''


with open("razzies-clean.csv") as f:
    razzies = f.read().splitlines()
movies.loc[movies.imdbID.isin(razzies), "color"] = "purple"
movies.loc[movies.imdbID.isin(razzies), "alpha"] = 0.9

axis_map = {
    "IMDb Rating": "imdbRating",
    "Tomatometer": "Meter",
    "Number of Reviews": "Reviews",
    "Box Office (million dollars)": "BoxOffice",
    "Length (minutes)": "Runtime",
    "Year": "Year",
}

desc = Div(text=open("description.html").read(), sizing_mode="stretch_width")

# Create Input controls
reviews = Slider(title="Minimum number of reviews", value=70, start=10, end=300, step=10)
min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
max_year = Slider(title="End Year released", start=1940, end=2014, value=2014, step=1)
oscars = Slider(title="Minimum number of Oscar wins", start=0, end=4, value=0, step=1)
boxoffice = Slider(title="Dollars at Box Office (millions)", start=0, end=800, value=0, step=1)
genre = Select(title="Genre", value="All",
               options=open('genres.txt').read().split())
director = TextInput(title="Director name contains (E.g. Miyazaki)")
cast = TextInput(title="Cast name contains (E.g. Harrison Ford)")
x_axis = Select(title="X Axis", options=sorted(axis_map.keys()), value="Tomatometer")
y_axis = Select(title="Y Axis", options=sorted(axis_map.keys()), value="IMDb Rating")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[], color=[], title=[], year=[], revenue=[], alpha=[]))

TOOLTIPS=[
    ("Title", "@title"),
    ("Year", "@year"),
    ("$", "@revenue")
]

p = figure(plot_height=600, plot_width=590, title="", toolbar_location=None, tooltips=TOOLTIPS, sizing_mode="scale_both")
p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")

#p.left[0].formatter.use_scientific = False

def select_movies():
    genre_val = genre.value
    director_val = director.value.strip()
    cast_val = cast.value.strip()
    selected = movies[
        (movies.Reviews >= reviews.value) &
        (movies.BoxOffice >= (boxoffice.value)) &
        (movies.Year >= min_year.value) &
        (movies.Year <= max_year.value) &
        (movies.Oscars >= oscars.value)
    ]
    if (genre_val != "All"):
        selected = selected[selected.Genre.str.contains(genre_val)==True]
    if (director_val != ""):
        selected = selected[selected.Director.str.contains(director_val,case=False)==True]
    if (cast_val != ""):
        selected = selected[selected.Cast.str.contains(cast_val,case=False)==True]
    return selected


def update():
    df = select_movies()
    x_name = axis_map[x_axis.value]
    y_name = axis_map[y_axis.value]

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "%d movies selected" % len(df)
    source.data = dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
        title=df["Title"],
        year=df["Year"],
        revenue=df["revenue"],
        alpha=df["alpha"],
    )

controls = [reviews, boxoffice, genre, min_year, max_year, oscars, director, cast,x_axis, y_axis]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = column(*controls, width=320, height=520)
inputs.sizing_mode = "fixed"
l = layout([
    [desc],
    [inputs, p],
], sizing_mode="scale_both")

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Movies"
