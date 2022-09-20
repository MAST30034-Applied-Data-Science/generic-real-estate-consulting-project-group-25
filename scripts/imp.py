import pandas as pd
import seaborn as sns
from tqdm import tqdm
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

COL = ['Median_age_persons', 'Median_mortgage_repay_monthly', 'Median_tot_prsnl_inc_weekly', 'Median_rent_weekly', 'Median_tot_fam_inc_weekly',
      'Average_num_psns_per_bedroom', 'Average_household_size']


def linear_imp(cleaned_monetary_data, write = False):
    final_rows = pd.DataFrame()
    yrs = [2012,2013,2014,2015,2017,2018,2019,2020]
    for i in range(0, len(cleaned_monetary_data.loc[:,'Median_age_persons_2011'])):
        curr = cleaned_monetary_data.iloc[i,:]
        X_df = {}
        for feature in COL:
            f = []
            for t in curr.iteritems():
                if feature in t[0]:
                    f.append(t[1])
            X_df[feature] = f

        X_df = pd.DataFrame.from_dict(X_df)
        X_df.loc[:,'year'] = [2011,2016,2021]+yrs
        # print(X_df)
        # Prediction Step
        for feature in COL:
            # Fitting regression to the current feature
            reg = LinearRegression().fit(X_df.loc[0:2, 'year'].values.reshape((-1,1)), X_df.loc[0:2, feature].values.reshape((-1,1)))

            # Predicting new values for missing fields
            years = {2012:-1,2013:-1,2014:-1,2015:-1,2017:-1,2018:-1,2019:-1,2020:-1}
            for yr in years.keys():
                years[yr] = reg.predict(np.array([[yr]]))[0][0]

            new_df = []
            for i in range(0, 11):
                row = X_df.iloc[i,:]
                for k in years.keys():
                    if k == row['year']:
                        row[feature] = years[k]
                    
                new_df.append(row)
                
                
            new_df = pd.DataFrame(new_df)
            X_df = new_df

        all_yrs = {2011:0,2012:3,2013:4,2014:5,2015:6,2016:1,2017:7,2018:8,2019:9,2020:10,2021:2}
        new_row = []
        field = {}
        for c in COL:
            for yr in all_yrs.keys():
                field[c+'_'+str(yr)] = new_df[c][all_yrs[yr]]

        s = pd.Series(field)
        new_row.append(s)
        row_df = pd.DataFrame(new_row)
        # row_df['Suburb'] = cleaned_monetary_data['Suburb'][i]
        final_rows = pd.concat([final_rows, row_df])

    # final_rows['Suburb'] = sub

    final_rows['Suburb'] = cleaned_monetary_data.loc[:,'Suburb'].tolist()
    if (write == True):
        final_rows.to_csv('../data/curated/all_imputed_monetary_data.csv', index=False)
    return final_rows



# cleaned_monetary_data = pd.read_csv('../data/curated/cleaned_monetary_data.csv')
# # print(cleaned_monetary_data.loc[:,'Suburb'])
# final = linear_imp(cleaned_monetary_data)
# final['Suburb'] = cleaned_monetary_data.loc[:,'Suburb'].tolist()
# final.to_csv('../data/curated/all_imputed_monetary_data.csv', index=False)