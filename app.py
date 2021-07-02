import os
import pathlib
import re
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import cufflinks as cf

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Covid"
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_lat_lon = pd.read_csv(
    os.path.join(APP_PATH, os.path.join("data", "lat_lon_counties.csv"))
)
df_lat_lon["FIPS "] = df_lat_lon["FIPS "].apply(lambda x: str(x).zfill(5))

df_full_data = pd.read_csv(
    os.path.join(
        APP_PATH, os.path.join("data", "covid.csv")
    )
)
#df_full_data["State"] = df_full_data["State"].apply(
    #lambda x: str(x).zfill(5)
#)
#df_full_data["County"] = (
# df_full_data["Unnamed: 0"] + ", " + df_full_data.County.map(str)
#)

YEARS = [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015]
MONTHS = ["Jan", "Feb", "Mar"]
MY_BINS = [
    "0-100",
    "101-200",
    "201-300",
    "301-400",
    "401-500",
    "501-600",
    "601-700",
    "701-800",
    "801-900",
    "901-1000",
    "1001-2000",
    "2001-3000",
    "3001-4000",
    "4001-5000",
    "5001-6000",
    ">6000",
]

BINS = [
    "0-2",
    "2.1-4",
    "4.1-6",
    "6.1-8",
    "8.1-10",
    "10.1-12",
    "12.1-14",
    "14.1-16",
    "16.1-18",
    "18.1-20",
    "20.1-22",
    "22.1-24",
    "24.1-26",
    "26.1-28",
    "28.1-30",
    ">30",
]

DEFAULT_COLORSCALE = [
    "#FFDBCE",
    "#FFCCBA",
    "#FFBCA4",
    "#FEAF93",
    "#FFA484",
    "#FF9773",
    "#FE8C64",
    "#FF7D50",
    "#FF7242",
    "#FF632D",
    "#FE5318",
    "#FD4404",
    "#DD4702",
    "#C94102",
    "#B53B02",
    "#9C3302",
]

DEFAULT_OPACITY = 0.8

mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.Img(id="logo", src=app.get_asset_url("logo2.png")),
                html.H5(children="Analyzing Covid-Related Deaths vs Ethnicity"),
                html.H4(children="Color and the Coronavirus: A Covid Dashboard to Illustrate the Effects of Ethnicity on Health Outcomes"),
                html.P(
                    id="description",
                    children="† Deaths are classified according to the refined CDC guidelines as mentioned on April 14, 2020. Covid-19 was made a nationally notifiable disease on April 5, 2020 by the Council for State and Territorial Epidemiologists. All data derived from NY times.",
                ),
            ],
        ),
        
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Covid Timeline: April 2020 to December 2020",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    marks={
                                        str(month): {
                                            "label": str(month),
                                             "style": {"color": "#7fafdf"},
                                        }
                                        for month in MONTHS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Heatmap of age adjusted mortality rates \
                            from poisonings in year {0}".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                style=mapbox_style,
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.5,
                                            ),
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart: Then drag on the map to select counties"),
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Total number of deaths by county",
                                    "value": "all_deaths",
                                },
                                {
                                    "label": "Absolute deaths per county by ethnicity",
                                    "value": "all_deaths_ethnicity",
                                },
                                {
                                    "label": "Population distribution adj. deaths per county by ethnicity",
                                    "value": "deaths_adjusted",
                                },
                                {
                                    "label": "Trends in pop-adjusted death rate",
                                    "value": "trends",
                                },
                            ],
                            value="show_death_rate_single_year",
                            id="chart-dropdown",
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
     ],
   ),
         html.Div(
            id="footer",
            children=[
                html.H5(children="MIT License: 2020 Data Pixel. Author: Sanjana Sreenath, Texas Tech University Health Sciences Center - El Paso"),
              
            ],
        ),
 ],
   
)


@app.callback(
    Output("county-choropleth", "figure"),
    [Input("years-slider", "value")],
    [State("county-choropleth", "figure")],
)
def display_map(year, figure):
    cm1 = dict(zip(MY_BINS, DEFAULT_COLORSCALE))
    cm = dict(zip(BINS, DEFAULT_COLORSCALE))


    data = [
        dict(
            lat=df_lat_lon["Latitude "],
            lon=df_lat_lon["Longitude"],
            text=df_lat_lon["Hover"],
            type="scattermapbox",
            hoverinfo="text",
            marker=dict(size=5, color="white", opacity=0),
        )
    ]

    annotations = [
        dict(
            showarrow=False,
            align="right",
            text="<b>Covid-19 death rate per county<br>adjusted for pop. distribution</b>",
            font=dict(color="#F4F4F8"),
            bgcolor="#000000",
            x=0.95,
            y=0.95,
        )
    ]

    for i, my_bin in enumerate(MY_BINS):
        color = cm1[my_bin]
        print(my_bin)
        annotations.append(
            dict(
                arrowcolor=color,
                text=my_bin,
                x=0.95,
                y=0.85 - (i / 20),
                ax=-60,
                ay=0,
                arrowwidth=5,
                arrowhead=0,
                bgcolor="#000000",
                font=dict(color="#F4F4F8"),
            )
        )

    if "layout" in figure:
        lat = figure["layout"]["mapbox"]["center"]["lat"]
        lon = figure["layout"]["mapbox"]["center"]["lon"]
        zoom = figure["layout"]["mapbox"]["zoom"]
    else:
        lat = 38.72490
        lon = -95.61446
        zoom = 3.5

    layout = dict(
        mapbox=dict(
            layers=[],
            accesstoken=mapbox_access_token,
            style=mapbox_style,
            center=dict(lat=lat, lon=lon),
            zoom=zoom,
        ),
        hovermode="closest",
        margin=dict(r=0, l=0, t=0, b=0),
        annotations=annotations,
        dragmode="lasso",
    )

    base_url = "https://raw.githubusercontent.com/jackparmer/mapbox-counties/master/"
    for bin in BINS:
        geo_layer = dict(
            sourcetype="geojson",
            source=base_url + str(year) + "/" + bin + ".geojson",
            type="fill",
            color=cm[bin],
            opacity=DEFAULT_OPACITY,
            # CHANGE THIS
            fill=dict(outlinecolor="#D0D3D4"),
        )
        layout["mapbox"]["layers"].append(geo_layer)

    fig = dict(data=data, layout=layout)
    return fig


@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Heatmap of Covid-19 death rates by county \
				adjusted for pop. distribution".format(
        year
    )


@app.callback(
    Output("selected-data", "figure"),
    [
        Input("county-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
    ],
)
def display_selected_data(selectedData, chart_dropdown, year):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select counties",
                paper_bgcolor="#F7F9F9",
                plot_bgcolor="#F7F9F9",
                font=dict(color="#000000"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    pts = selectedData["points"]
    fips = [str(pt["text"].split("<br>")[-1]) for pt in pts]

    for i in range(len(fips)):
        if len(fips[i]) == 4:
            fips[i] = "0" + fips[i]
    dff = df_full_data[df_full_data["FIPS Code"].isin(fips)]
    df1 = dff[dff.index % 3 != 0]  # Excludes every 3rd row starting from 0
   
    
    df1['Hispanic compare'] = df1.Hispanic.shift(-1)
    df1['Hispanic %'] = df1.Hispanic / df1['Hispanic compare']
    df1['Non-Hispanic White compare'] = df1['Non-Hispanic White'].shift(-1)
    df1['Non-Hispanic White %'] = df1['Non-Hispanic White']/df1['Non-Hispanic White compare']
    df1['Non-Hispanic Black compare'] = df1['Non-Hispanic Black'].shift(-1)
    df1['Non-Hispanic Black %'] = df1['Non-Hispanic Black']/df1['Non-Hispanic Black compare']
    df1['Non-Hispanic Asian compare'] = df1['Non-Hispanic Asian'].shift(-1)
    df1['Non-Hispanic Asian %'] = df1['Non-Hispanic Asian']/df1['Non-Hispanic Asian compare']


    if chart_dropdown != "trends":
        title = "Population distribution adj. deaths per county by ethnicity"
        if "all_deaths_ethnicity" == chart_dropdown:
            title = "All Covid-19 deaths per county by ethnicity"
            AGGREGATE_BY=['Non-Hispanic White','Non-Hispanic Black','Non-Hispanic Asian','Hispanic']
                
        elif "all_deaths" == chart_dropdown:
            title = "All Covid-19 deaths per county"
            AGGREGATE_BY="COVID-19 Deaths"
       
        
        AGGREGATE_BY=['Non-Hispanic White %','Non-Hispanic Black %','Non-Hispanic Asian %','Hispanic %']

        fig = df1.iplot(
            kind="bar", x="County Name",  y=AGGREGATE_BY, title=title, asFigure=True,colors=[
            "#ABEBC6",
            "#E74C3C",
            "#EBDEF0",
            "#BDC3C7",
            "#A6ACAF",
            "#616A6B",
        ],
            )
        fig_layout = fig["layout"]
        fig_data = fig["data"]
        fig_data[0]["marker"]["color"] = "#F1C40F"
        fig_data[0]["marker"]["opacity"] = 1
        fig_data[0]["marker"]["line"]["width"] = 0
        fig_data[0]["textposition"] = "outside"
        fig_layout["paper_bgcolor"] = "#F7F9F9"
        fig_layout["plot_bgcolor"] = "#F7F9F9"
        fig_layout["font"]["color"] = "#000000"
        fig_layout["title"]["font"]["color"] = "#000000"
        fig_layout["xaxis"]["tickfont"]["color"] = "#000000"
        fig_layout["yaxis"]["tickfont"]["color"] = "#000000"
        fig_layout["xaxis"]["gridcolor"] = "#D0D3D4"
        fig_layout["yaxis"]["gridcolor"] = "#D0D3D4"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig

    fig = df1.iplot(
        kind="scatter",
        x="County Name",
        y="COVID-19 Deaths",
        categories="County Name",
        colors=[
            "#ABEBC6",
            "#F6DDCC",
            "#F1C40F",
            "#F39C12",
            "#E67E22",
            "#EBDEF0",
            "#BDC3C7",
            "#A6ACAF",
            "#616A6B",
        ],
        asFigure=True,
    )
    
 
    for i, trace in enumerate(fig["data"]):
        trace["mode"] = "lines+markers"
        trace["marker"]["size"] = 13
        trace["marker"]["line"]["width"] = 1
        trace["type"] = "scatter"
      
    # Only show first 500 lines
    fig["data"] = fig["data"][0:500]

    fig_layout = fig["layout"]

    # See plot.ly/python/reference
    fig_layout["yaxis"]["title"] = "Covid-19 death rate adjusted for pop. distribution"
    fig_layout["xaxis"]["title"] = ""
    fig_layout["yaxis"]["fixedrange"] = True
    fig_layout["xaxis"]["fixedrange"] = False
    fig_layout["hovermode"] = "closest"
    fig_layout["title"] = "<b>{0}</b> counties selected".format(len(fips))
    fig_layout["legend"] = dict(orientation="v")
    fig_layout["autosize"] = True
    fig_layout["paper_bgcolor"] = "#F7F9F9"
    fig_layout["plot_bgcolor"] = "#F7F9F9"
    fig_layout["font"]["color"] = "#000000"
    fig_layout["xaxis"]["tickfont"]["color"] = "#000000"
    fig_layout["yaxis"]["tickfont"]["color"] = "#000000"
    fig_layout["xaxis"]["gridcolor"] = "#D0D3D4"
    fig_layout["yaxis"]["gridcolor"] = "#D0D3D4"

    
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
