from statsmodels.formula.api import ols, glm
import statsmodels.api as sm
import re
def back_ward_elim(dataframe):
    """
    Performs backward elimination, by recursively omitting the feature with the highest p-value
    :param dataframe: Pandas dataframe containing the data you want to evaluate
    return: final model after feature selection and it's anova
    """
    P_VALUE = 0.05
    stats_query = "price~ave_dist_3_schools+Suburb+closest_school+ClosestDstToShoppingCentre+DstToCBD+ClosestDstToStation+ClosestDstToUni+age0To19+age20To39+age40To59+age60Plus+longTermResident+owner+renter+family+single"
    model = ols(stats_query, data = dataframe).fit()
    anova = sm.stats.anova_lm(model,typ=2)
    while len(anova[anova["PR(>F)"] >= P_VALUE]) > 0:
        #Obtain the highest p-value and omit it from the query until there is no features with p-value > 0.05
        max_p = max(anova["PR(>F)"])
        eliminated_param = anova[anova["PR(>F)"] == max_p].index[0]
        stats_query = re.sub(eliminated_param, "", stats_query)
        stats_query = re.sub("\+\+", "+", stats_query)
        stats_query = re.sub("\+$", "", stats_query)
        model = ols(stats_query, data = dataframe).fit()
        anova = sm.stats.anova_lm(model,typ=2)
    return anova, model
