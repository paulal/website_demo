import sqlite3

from wtforms import FloatField
import pandas as pd
from pulp import LpMinimize, LpProblem, LpStatus, lpSum, LpVariable



omitted_food_types = ('BABYFTOT', 
                      'BABMEATD',
                      'BABFISHD',
                      'BABMILPO',
                      'BABWATPO',
                      'BABFRUB',
                      'BABVEGE',
                      'BABMIFRU',
                      'BABOTHER',
                      'MMILK',
                      'INFMILK',
                      'CASMILK',
                      'PREMILK',
                      'SOYMILK',
                      'WHEYMILK',
                      'AMINMILK',
                      'SPECTOT',
                      'SPECSUPP',
                      'MEALREP',
                      'SPORTFOO',
                      'SPECFOOD',
                      'DRINKART',
                      'DRSPORT',
                      'DRWATER')

class FlexibleFloatField(FloatField):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)


def get_food_names() -> list:
    """
    Get a list of all the food ids and names in the db.

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
    """
    Get the RDA (recommended daily allowance) values for a specific demographic from a csv file
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
    """
    Use the given database connection to extract the nutrition values for all foods except
    for foods such as baby food, infant formulas, supplements, and weight loss preparations,
    and put them in a Pandas DataFrame with one row per food and nutrients as columns.
    
    Args:
        conn: database connection
        nutrient_tuple: tuple of the abbreviations of nutrients that we want to look at

    Returns:
        DataFrame: nutrient values for foods
    """
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
    # to a format with all nutrients in one food in one row
    wide_table = pd.pivot(data=long_table, values='BESTLOC', index='FOODID', columns='EUFDNAME')
    print(f"wide_table.head: {wide_table.head()}")
    print(f"number of NaN values in wide_table: {wide_table.isnull().sum().sum()}")
    # change NaN values to 0
    wide_table = wide_table.fillna(0)
    print(f"number of NaN values in wide_table 2: {wide_table.isnull().sum().sum()}")

    return wide_table


def solve_for_optimal_foods(remainder_df, comp_values):
    """
    Given the input dataframes, return the PuLP result that optimises the foods
    to be eaten to meet daily nutrients while minimising calorie intake
    
    Args:
        remainder_df: Pandas dataframe with the information for the case we want to solve:
                      the target nutrient amounts and maximum amounts
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
    print("aaa")
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
    print("ddd")

    # Set the objective
    model += lpSum(energy[f] * x[f] for f in foods)
    print("eeee")

    # Solve the optimization problem
    print("where are we?")
    status = model.solve()
    print("where are we now?")
    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"total calories: {model.objective.value()}")
    for var in model.variables():
        if var.value() != 0.0:
            print(f"{var.name}: {var.value()}")
    print("all done")
    return status
