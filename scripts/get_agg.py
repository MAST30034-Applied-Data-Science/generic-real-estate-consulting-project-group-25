import pandas as pd
from pandasql import sqldf
import statistics
from tqdm import tqdm


def pysqldf(q):
    return sqldf(q, globals())


prop = pd.read_csv('../data/curated/cleaned_property_listing_data.csv')


def get_agg(write=False):
    """Returns property listing data aggregated base on type of rental property in each suburb""

    :param write: save file to ../data/curated/2022_aggregated/agg_bed_avgPrice_sub.csv, defaults to False
    :return: pandas dataframe 
    """
    query = """SELECT beds, avg(price) as avg_price, count(beds) as count, propertyType, suburb
            FROM prop 
            GROUP BY beds, propertyType, suburb"""
    agg_bed_avgPrice_sub = pysqldf(query)

    # Calculate median
    median = []
    for j in tqdm(range(0, len(agg_bed_avgPrice_sub['beds']))):
        all_values = []
        for i in range(0, len(prop['beds'])):
            if (prop['beds'][i] == agg_bed_avgPrice_sub['beds'][j] and prop['propertyType'][i] == agg_bed_avgPrice_sub['propertyType'][j] and prop['suburb'][i] == agg_bed_avgPrice_sub['suburb'][j]):
                all_values.append(float(prop['price'][i]))
        median.append(statistics.median(all_values))

    agg_bed_avgPrice_sub['median'] = median
    if write == True:
        agg_bed_avgPrice_sub.to_csv(
            '../data/curated/2022_aggregated/agg_bed_avgPrice_sub.csv', index=False)

    return agg_bed_avgPrice_sub
