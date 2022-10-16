import pandas as pd
import geopandas as gpd

import requests

import pickle

from bokeh.io import output_file, show, output_notebook, export_png
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, HoverTool, Select
from bokeh.plotting import figure
from bokeh.palettes import brewer
from bokeh.layouts import widgetbox, row, column
from bokeh.io.doc import curdoc

from bokeh.tile_providers import CARTODBPOSITRON, get_provider


def keep_forecast_only(dicty):
    """Keeping only the forecasted median price and the year it is forcasted for

    :param dicty: dictionary containing a mapping Suburb-> prediction dataframe
    :return: dictionary with mapping suburb -> [year, Median_rental_price]
    """
    for key, df in dicty.items():
        dicty[key] = df[['year', 'Median_rental_price']]
    return dicty


def read_data(DATA_DIR='../data/curated/'):
    """Reading all the forecast data in

    :param DATA_DIR: directory where the data is located, defaults to '../data/curated/'
    :return: dictionary of those forecasts
    """
    forecast_names = ['forecast_bed_1_flat_covid', 'forecast_bed_2_flat_covid', 'forecast_bed_3_flat_covid',
                      'forecast_bed_2_house_covid', 'forecast_bed_3_house_covid', 'forecast_bed_4_house_covid']
    forecasts = {}
    for name in forecast_names:
        with open(f'{DATA_DIR}{name}', 'rb') as f:
            stuff = pickle.load(f)
        forecasts[name] = keep_forecast_only(stuff)
    return forecasts


def flatten_prediction(forecasts, year=2027):
    """ Create a single dataframe from the given dictionary of dictionaries.

    current structure of forecasts:
    forecasts is a dict for each property type
    each property type is a dictionary suburb(concatenated) -> df[year, price]

    flatten the structure to have the following structure, for one year
    suburb_name, 1_bed_flat, 2_bed_flat, .., 2_bed_house, ...
    Name1, 134, 1234, 2342, 4255, 6453, ...


    :param forecasts: dictionary containing the predictions
    :param year: year to keep for plotting, defaults to 2027
    :return: flat dataframe
    """
    columns = ['suburb']  # list(forecasts.keys())
    # columns.insert(0,'suburb')
    # [x.split('forecast_bed_')[1].split('_covid')[0] for x in forecasts.keys()]
    df = pd.DataFrame(columns=columns)
    df.suburb = pd.Series(forecasts['forecast_bed_1_flat_covid'].keys())
    # display(df)

    for prop_type, suburb_dict in forecasts.items():
        temp = []  # pd.Series(dtype='float64')
        for suburb, prediction in suburb_dict.items():
            #prediction = prediction.set_index('year')
            temp.append(prediction[prediction['year'] ==
                        year].Median_rental_price.values[0])
        df[prop_type] = temp

    # Keeping only informative part for the column names: forecast_bed_1_flat_covid-> 1_flat
    df.rename(lambda x:  'suburb' if not '_' in x else '_'.join(
        x.split('_')[2:4]), axis='columns', inplace=True)
    #df.colums = [str(x) for x in range(df.shape[1])]
    return df


def load_data(year=2027):
    """Loading in the forecasts and suburb shapes

    :return: dataframe containing the predicted price for the suburbs and property types
    """
    data = read_data()
    df = flatten_prediction(data, year)

    suburb_gdf = gpd.read_file(
        "../data/raw/Suburb Shapes/vic_localities.shp")[["LOC_NAME", "geometry"]]

    # split each suburb into its own row instead of being string concatenated,
    # so that it is easy to join with the suburb gdf
    df = df.assign(temp=df['suburb'].str.split(', ')).explode('temp').drop(
        ['suburb'], axis=1).rename(columns={'temp': 'suburb'}).reset_index(drop=True)

    # there is around 85 suburbs that get lost unfortunately

    suburb_gdf = suburb_gdf.join(df.set_index('suburb'), on='LOC_NAME').dropna(
        how='any').rename(columns={'LOC_NAME': 'suburb'})
    # in case the thing is to heavy, dumb the shapes down
    # suburb_gdf['geometry'] = suburb_gdf['geometry'].simplify(0.05, preserve_topology=True) # if we want to reduce precision of each polygon to make it quicker to display, 0.05 is the reducing coeficitient or whateve

    # convert to same geometry as the plot
    suburb_gdf['geometry'] = suburb_gdf['geometry'].to_crs(epsg=3857)

    return suburb_gdf


# Set bokeh to save file
def create_map(plotted_price='1_flat', year=2027, filename="DEFAULT"):
    """Creating the visualisations

    :param gdf: Dataframe to visualise
    :param plotted_price: which property type to visualise, defaults to '1_flat'
    :param filename: path where to save the plot, defaults to "DEFAULT"
    """
    gdf = load_data(year)

    if filename == "DEFAULT":
        filename = f"../plots/{plotted_price}_plot.html"

    # todo, add year and the preproc fn call to here
    output_file(filename, title="Actual data plotting suburb")

    # convert to int, float precision not needed
    cols = ['1_flat', '2_flat', '3_flat', '2_house', '3_house', '4_house']

    for col in cols:
        gdf[col] = gdf[col].astype('int')

    geo_source = GeoJSONDataSource(geojson=gdf.to_json())

    # giving the basic view frame of the map
    tile_provider = get_provider(CARTODBPOSITRON)

    # range bounds supplied in web mercator coordinates
    x_range = (16075000.0, 16225000.0)
    y_range = (-4635000.0, -4485000.0)
    p = figure(x_range=x_range, y_range=y_range,
               x_axis_type="mercator", y_axis_type="mercator",
               plot_height=600, plot_width=600,
               match_aspect=True,)
    p.add_tile(tile_provider)
    p.title.text = f"Predicted median price per suburb for {plotted_price.split('_')[0]} bed {plotted_price.split('_')[1]} (AUD)"
    p.title.align = "center"
    p.title.text_font_size = "17px"

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(
        palette='Plasma256', low=gdf[gdf[plotted_price].gt(-1)][plotted_price].min(), high=gdf[plotted_price].max())

    #print(f"used min max is {gdf[gdf['2_house'].gt(-1)]['2_house'].min()}, {gdf['2_house'].max()}")

    color_bar = ColorBar(color_mapper=color_mapper,
                         label_standoff=8,
                         width=20, height=600,
                         border_line_color=None,
                         location=(0, 0),
                         orientation='vertical')
    # major_label_overrides = tick_labels, could be used to set custom tickers, tick_labels is a dict value->display value

    # Add patch renderer to figure.
    suburbs = p.patches('xs', 'ys', source=geo_source,
                        # here comes the transform function
                        fill_color={'field': plotted_price,
                                    'transform': color_mapper},
                        line_color='gray',
                        line_width=0.25,
                        fill_alpha=0.75)

    # add tooltips as needed for other prediction values
    tooltips = [('Suburb', '@suburb')]
    tooltips.extend([(f"{year} prediction {x.split('_')[0]} bed {x.split('_')[1]}", f'@{x}')
                    for x in filter(lambda x: '_' in x, [x for x in gdf.columns])])
    # ('2027 prediction 1flat', '@1_flat')]
    p.add_tools(HoverTool(renderers=[suburbs],
                          tooltips=tooltips))

    p.add_layout(color_bar, 'right')

    show(p)


if __name__ == "__main__":
    data = load_data()
    for col_name in data.columns:
        if "_" in col_name:
            create_map(col_name)
