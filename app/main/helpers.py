from wtforms import FloatField
import sqlite3


class FlexibleFloatField(FloatField):

    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(",", ".")
        return super(FlexibleFloatField, self).process_formdata(valuelist)


def get_food_names() -> list:
    """
    Gets a list of all the food ids and names in the db.

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

