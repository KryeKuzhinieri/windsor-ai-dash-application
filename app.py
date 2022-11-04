import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
from pywindsorai.client import Client
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("API_KEY")

def fetch_ad_dataset(API_KEY):
    client = Client(API_KEY)
    DATE = "last_7d"
    FIELDS = ["campaign", "clicks", "datasource", "source", "spend"]
    dataset = pd.DataFrame(client.connectors(date_preset=DATE, fields=FIELDS)["data"])
    return dataset

dataset = fetch_ad_dataset(API_KEY)

app = dash.Dash(__name__)
server = app.server
app.title = "Windsor.ai"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Img(src="assets/windsor_logo.webp", className="header-emoji"),
                html.H1(
                    children="Windsor.ai Dashboard", className="header-title"
                ),
                html.P(
                    children="Analyzing ad data using Windsor.ai' services."
                    " Integration of Google and Facebook Ads using the API",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Data Source", className="menu-title"),
                        dcc.Dropdown(
                            id="source-filter",
                            options=[
                                {"label": " ".join(source.split("_")).title(), "value": source}
                                for source in np.sort(dataset.datasource.unique())
                            ],
                            value="google_ads",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                )
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="clicks-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="spent-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("clicks-chart", "figure"), Output("spent-chart", "figure")],
    [
        Input("source-filter", "value"),
    ],
)
def update_charts(source):
    mask = (dataset.datasource == source)
    filtered_data = dataset.loc[mask, :]
    clicks_chart_figure = {
        "data": [
            {
                "x": filtered_data["campaign"],
                "y": filtered_data["clicks"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Number of Clicks Per Campaign",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    spent_chart_figure = {
        "data": [
            {
                "x": filtered_data["campaign"],
                "y": filtered_data["spend"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Amount of Money Spent Per Campaign", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return clicks_chart_figure, spent_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)

