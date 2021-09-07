import sqlite3

from wtforms import FloatField
import pandas as pd


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
    Get a few rows from a csv file and put them in a Pandas DataFrame.
    
    Args:
        age: string denoting an age group (one of the columns in the csv file)

    Returns:
        DataFrame: RDAs for a number of nutrients for the specified age group
    """
    rda_all = pd.read_csv("././saantisuositus_2014.csv", sep=";", header=None, names=["EUFDNAME", "name", "unit", "mnuori", "maikuinen", "mkeski", "miäkäs", "mvanha", "npieni","nnuori", "naikuinen", "nkeski", "niäkäs", "nvanha"])
    rda_selected = rda_all[["EUFDNAME", "name", age]]
    rda_selected["EUFDNAME"] = rda_selected["EUFDNAME"].str.lower()
    # for the time being, remove sugar and salt, which have max values instead of min
    rda_selected = rda_selected[rda_selected["EUFDNAME"] != "sugar"]
    rda_selected = rda_selected[rda_selected["EUFDNAME"] != "nacl"]
    rda = rda_selected.rename(columns={age: "target"})
    return rda