import sqlite3 as sql
from os.path import dirname, join

import numpy as np
import pandas.io.sql as psql

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
reviews = Slider(title="Minimum number of reviews", value=80, start=10, end=300, step=10)
min_year = Slider(title="Year released", start=1940, end=2014, value=1970, step=1)
max_year = Slider(title="End Year released", start=1940, end=2014, value=2014, step=1)
oscars = Slider(title="Minimum number of Oscar wins", start=0, end=4, value=0, step=1)
boxoffice = Slider(title="Dollars at Box Office (millions)", start=0, end=800, value=0, step=1)
genre = Select(title="Genre", value="All",
               options=open('genres.txt').read().split())
director = TextInput(title="Director name contains")
cast = TextInput(title="Cast name contains")
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
