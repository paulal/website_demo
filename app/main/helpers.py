import sqlite3
from datetime import datetime
from operator import itemgetter
from collections import defaultdict

from wtforms import FloatField
import pandas as pd
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


omitted_food_types = ("babyftot",
                      "babmeatd",
                      "babfishd",
                      "babmilpo",
                      "babwatpo",
                      "babfrub",
                      "babvege",
                      "babmifru",
                      "babother",
                      "mmilk",
                      "infmilk",
                      "casmilk",
                      "premilk",
                      "soymilk",
                      "wheymilk",
                      "aminmilk",
                      "spectot",
                      "specsupp",
                      "mealrep",
                      "sportfoo",
                      "specfood",
                      "drinkart",
                      "drsport",
                      "drwater")

class FlexibleFloatField(FloatField):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)


def get_food_names() -> list:
    """(Not currently used) Get a list of 5 food ids and names from the db.

    Returns:
        list: list of tuples of food ids and names as in (foodid, foodname)
    """
    with sqlite3.connect('fineli.db') as conn:
        curs = conn.cursor()
        try:
            stmt = "SELECT foodid, foodname FROM food"
            #return [(x[0], x[1]) for x in curs.execute(stmt)]
            curs.execute(stmt)
            #foods = curs.fetchall()
            foods = curs.fetchmany(5)
            print(foods)
            yield foods
        except Exception as e:
            print(e)
        finally:
            if curs:
                curs.close()


def get_rda(age:str) -> pd.DataFrame:
    """Get the RDA (recommended daily allowance) values for a specific demographic from a csv file
    and put them in a Pandas DataFrame.
    
    Args:
        age: string denoting a combination of sex + age (one of the columns in the csv file)

    Returns:
        DataFrame: RDAs for a number of nutrients for the specified group of people
    """
    rda_all = pd.read_csv("././saantisuositus_2014_with_max.csv", sep=";", header=None, names=["EUFDNAME", "name", "unit", "mnuori", "maikuinen", "mkeski", "miäkäs", "mvanha", "npieni","nnuori", "naikuinen", "nkeski", "niäkäs", "nvanha", "max"])
    rda_selected = rda_all[["EUFDNAME", "name", age, "max"]]
    rda_selected["EUFDNAME"] = rda_selected["EUFDNAME"].str.lower()
    rda = rda_selected.rename(columns={age: "target"})
    return rda


def get_nutrition_values_of_foods(conn, nutrient_tuple) -> pd.DataFrame:
    """Use the given database connection to extract the nutrition values for all foods except
    for foods such as baby food, infant formulas, supplements, and weight loss preparations,
    and put them in a Pandas DataFrame with one row per food and nutrients as columns.
    
    Args:
        conn: database connection
        nutrient_tuple: tuple of the abbreviations of nutrients that we want to look at

    Returns:
        DataFrame: nutrient values for foods
    """
    # the next line prints the full sql query if uncommented
    #conn.set_trace_callback(print)
    # multiplying bestloc by 1.0 changes the decimal separator from comma to full stop, avoiding problems down the line...
    stmt = "SELECT component_value.foodid, component_value.eufdname, component_value.bestloc / 100.0 AS 'BESTLOC' " + \
           "FROM food JOIN component_value ON food.foodid=component_value.foodid " +\
            f"WHERE food.fuclass NOT IN ({(len(omitted_food_types)) * '?,'}"[:-1] + ") " +\
            f"AND component_value.eufdname IN ({(len(nutrient_tuple)) * '?,'}" + "?)" # an extra question mark for enerc
    params = omitted_food_types + nutrient_tuple + ("enerc",)
    print(f"params: {params}")
    long_table = pd.read_sql(stmt, conn, params=params)
    print(f"energy value for sugar: {long_table.loc[2]['BESTLOC'] * 2}")
    print(f"long_table.head: {long_table.head()}")
    print(long_table.shape)
    # transpose the dataframe from a form that has a single nutrient in single food per row
    # to a format with all nutrients in one food per row
    wide_table = pd.pivot(data=long_table, values='BESTLOC', index='FOODID', columns='EUFDNAME')
    print(f"wide_table.head: {wide_table.head()}")
    print(f"number of NaN values in wide_table: {wide_table.isnull().sum().sum()}")
    # change NaN values to 0
    wide_table = wide_table.fillna(0)
    print(f"number of NaN values in wide_table 2: {wide_table.isnull().sum().sum()}")

    return wide_table


def solve_for_optimal_foods(remainder_df, comp_values):
    """Given the input dataframes, return the PuLP result that optimises the foods
    to be eaten to meet daily nutrients while minimising calorie intake
    
    Args:
        remainder_df: Pandas dataframe with the information for the case we want to solve:
                      the target (minimum) nutrient amounts and maximum amounts
        comp_values: Pandas dataframe with the nutrient compositions of various foods

    Returns:
        PuLP optimization result
    """
    # create a list of food index numbers
    foods = comp_values.index.tolist()
    print(foods[:3])
    # create a separate dictionary of the energy contents of foods
    energy = {f: comp_values.loc[f]["enerc"] for f in foods}
    print(f"energy, sugar: {energy[1]}")
    # create a nutrient composition table without the energy values
    nutrient_values = comp_values.drop(columns="enerc")
    print(f"nutrient_values after dropping enerc:\n {nutrient_values.head()}")
    # create a list of nutrient name abbreviations
    nutrients = nutrient_values.columns.tolist()
    print("nutrients", nutrients[:3])
    print(f"test:\n {comp_values[['enerc', 'ca']]}")
    
    # Define the model
    model = LpProblem(name="nutrient_optimisation", sense=LpMinimize)
    print("model defined")

    # Define the decision variables
    x = {f: LpVariable(name=f"x{f}", lowBound=0, cat="Integer") for f in foods}
    print("decision variables defined")

    # Add constraints
    model += (lpSum(x.values()) <= 4000, "total_mass_of_food")
    for f in x:
        model += (x[f] <= 800, f"mass_of_food_{f}")
        #print("bbb")
    for n in nutrients:
        print(f"nutrient: {n}")
        #print(f'remainder value: {remainder_df.loc[n]["remainder"]}')
        #print(f'nutrient_values.loc[f][n]: {nutrient_values.loc[f][n]}')
        #print(f'lpSum: {lpSum([nutrient_values.loc[f][n] * x[f] for f in foods])}')
        #print(f'x[f]: {x[f]}')
        model += (lpSum([nutrient_values.loc[f][n] * x[f] for f in foods]) >= remainder_df.loc[n]["remainder"], f"min_of_{n}")
        model += (lpSum([nutrient_values.loc[f][n] * x[f] for f in foods]) <= remainder_df.loc[n]["max"] - remainder_df.loc[n]["remainder"], f"max_of_{n}")
        #print("cccc")
    #model += (sum([1 for w in x.values() if w > 0]) <= 50, "max_number_of_foods")

    # Set the objective
    model += lpSum(energy[f] * x[f] for f in foods)

    # Solve the optimization problem
    #status = model.solve()
    model.solve()
    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"total calories: {model.objective.value()}")
    for var in model.variables():
        if var.value() != 0.0:
            print(f"{var.name}: {var.value()}")
    print("all done")
    return model


def create_dfs_from_solution(conn, variables, eaten_df):
    """Create pandas dataframes from PuLP solution variables
    Args:
        conn: database connection
        variables: the variables of a PuLP solution
        eaten_df: Pandas df with the amounts of nutrients already eaten

    Returns:
        two DataFrames: df with foodid, foodname, amount
                        df with eufdname, nutrient name, amount
    """
    #TODO
    pass


def get_api_response(url:str, payload:dict) -> dict:
    """Download the content from an API and return a dictionary.

    Args:
        url (str): API endpoint
        payload (dict): parameters for the API call

    Returns:
        content (dict): the contents of API response (or {} if something went wrong)
    """
    # retry functionality to avoid timeout errors
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        response = session.get(url, params=payload)
        if response.status_code == 200:
            content = response.json()
            print(f'content: {content}')
            return content
        else:
            print('Something went wrong.')
            return {}
    except MaxRetryError:
        print('Max retries')
        return {}


def get_daily_values(data:list) -> list:
    """Filter the price/volume data to only keep one value per day.

    Args:
        data (list): all price/volume data received from the API as a list of lists

    Returns:
        daily_values (list): filtered list of lists with only one entry per day
    """
    daily_values = []
    # I assume the prices returned by the API are in chronological order
    # and only take the first price for each day.
    # The timestamps include microseconds -> divide by 1000 to get the correct dates.
    # First, get the very first item in the list
    daily_values.append([datetime.utcfromtimestamp(data[0][0] / 1000).date(), data[0][1]])
    print(f'daily_values list with the first item: {daily_values}')
    # Then, append the first value for each new day
    for item in data[1:]:
        day = datetime.utcfromtimestamp(item[0] / 1000).date()
        print(f'the next item: {day} {item[1]}')
        if day > daily_values[-1][0]:
            print(f'day added: {day}')
            daily_values.append([day, item[1]])
    print(f'daily values to return: {daily_values}')
    return daily_values


def get_bear_length(prices:list) -> int:
    """Get the length of the longest streak of diminishing prices.

    Args:
        prices (list): list of daily values

    Returns:
        max (int): the longest streak of diminishing prices
    """
    counter = 0
    max = 0
    for i in range(len(prices) - 1):
        print(f'i: {i}')
        if prices[i + 1][1] < prices[i][1]:
            counter += 1
            print(f'counter = {counter}')
            if counter > max:
                max = counter
                print(f'new max = {max}')
        else:
            counter = 0
    return max


def get_highest_volume(volumes:list) -> list:
    """Get the date with the highest trading volume and the volume in euros.

    Args:
        volumes (list): dates and their associated trading volumes as a list of lists;
                        the volumes are pre-filtered to include only the first value
                        per day, similar to the prices.

    Returns:
        max (list): the date with highest volume and the volume in euros
    """
    print(f'volumes: {volumes}')
    # set the first day as the starting point
    max = volumes[0]
    for day in volumes[1:]:
        if day[1] > max[1]:
            print(f'new max: {day}')
            max = day
    print(f'max: {max}')
    
    return max


def get_buy_and_sell_dates(prices:list) -> tuple:
    """Get the buy and sell dates for maximum profit.

    Args:
        prices (list): dates and associated prices as a list of lists

    Returns:
        buy and sell dates (tuple): the dates on which to buy and sell
    """
    # set the first day as a starting point
    start = prices[0]
    end = prices[0]
    max_so_far = [start, end, 0]
    # find the best days to buy and sell
    for sublist in prices[1:]:
        # update the end if price rises above current endpoint
        if sublist[1] > end[1]:
            end = sublist
            diff = end[1] - start[1]
            # if diff is bigger than the current max diff, update the max
            if diff > max_so_far[2]:
                max_so_far[0] = start
                max_so_far[1] = end
                max_so_far[2] = diff
        # start over if price goes below start value
        elif sublist[1] < start[1]:
            start = sublist
            end = sublist
    print(f'max_so_far to return: {max_so_far}')
    return max_so_far[0][0], max_so_far[1][0]
            
            