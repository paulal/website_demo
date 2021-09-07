from datetime import datetime
import re
from io import BytesIO
import random
import sqlite3

from flask import render_template, make_response, request, redirect, flash, url_for, jsonify
import xml.etree.ElementTree as ET
import json
from finna_client import *
import wikipedia
from matplotlib.figure import Figure
import numpy as np
import base64
import pandas as pd

from app.main import bp
from app.main.forms import FinnaForm, PlottingForm, NutrientForm
from app.main.helpers import get_rda


# define routes
@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/<page_name>')
def other_page(page_name):
    response = make_response('The page named %s does not exist.' % page_name, 404)
    return response

@bp.route('/wikipedia_page')
def wikipedia_page():
    topics = ['Helsinki', 'Kuopio', 'Turku', 'Maakunta-_ja_soteuudistus',
    'Tiikeri', 'Sademetsäkäpinkäinen', 'Lineaarinen_regressioanalyysi',
    'Derivaatta', 'Urho_Kekkosen_kansallispuisto', 'Laama', 
    'Septimus_Heap']
    topic = topics[random.randint(0, len(topics)-1)]

    heading = topic.replace('_', ' ')
    wikipedia.set_lang('fi')
    page = wikipedia.page(topic)

    summary = wikipedia.summary(topic)
    images = page.images
    #print(images)
    image = images[random.randint(0, len(images)-1)]
    
    return render_template('wikipedia.html', title='Wikipedia',
    topic=topic, heading=heading, summary=summary, image=image)


@bp.route('/finna', methods=['GET', 'POST'])
def finna():
    if request.method == 'GET':
        form = FinnaForm()
        finna = FinnaClient()

        return render_template('finna.html', title='Finna-haku',
                               form=form)
    elif request.method == 'POST':
        form = FinnaForm()
        finna = FinnaClient()
        
        if form.validate_on_submit():
            # send query to Finna based on the selected field
            if form.target.data == 'author':
                result = finna.search(form.search_term.data,
                              search_type=FinnaSearchType.Author,
                              fields=['fullRecord'],
                              filters=['format:0/Book/'], 
                              limit=50)
                #print(f'result: {result}')
            else:
                result = finna.search(form.search_term.data,
                              search_type=FinnaSearchType.Title,
                              fields=['fullRecord'],
                              filters=['format:0/Book/'], 
                              limit=50)
            if result['resultCount'] == 0:
                flash('Mitään ei löytynyt. Yritä uudelleen.')
                return redirect(url_for('finna'))
            
            # save the data for individual books in a set to remove duplicates
            records_set = set()
            #print(result)

            # parse book data
            for rec in result['records']:
                #print('rec = ', rec)
                tree = ET.fromstring(rec['fullRecord'])
                record = {}
                
                for datafield in tree.iter('{http://www.loc.gov/MARC21/slim}datafield'):
                    #print('datafield.attrib =', datafield.attrib)
                    if datafield.attrib['tag'] == '041':
                        lang = datafield[0].text
                        #print(f'lang = {lang}')
                        record['lang'] = lang
                        if len(datafield) > 1:
                            source_lang = datafield[1].text
                            #print('source lang=', source_lang)
                            record['source_lang'] = source_lang
                    elif datafield.attrib['tag'] == '100':
                        #print('author=', datafield[0].text)
                        #author_spl = datafield[0].text.rstrip('.').rstrip(',').split(', ')
                        #author = author_spl[1] + ' ' + author_spl[0]
                        #print('author =', author)
                        #record['author'] = author
                        author = datafield[0].text.rstrip('.,')
                        record['author'] = author
                    elif datafield.attrib['tag'] == '245':
                        #print(datafield[0].text)
                        title = datafield[0].text.rstrip(' /:.')
                        #print('title =', title)
                        record['title'] = title
                
                # check the language before adding the book in the set
                # not all books have a language code, drop those
                try:
                    if record['lang'] == form.language.data or form.language.data == 'all':
                        json_record = json.dumps(record)
                        #print(json_record)
                        records_set.add(json_record)
                except KeyError:
                    pass

                
            records = [json.loads(x) for x in records_set]
            #print(f'records: {records}')
            
            return render_template('finna.html', title='Finna-haku',
                               form=form, result=result, records=records)
        
        return render_template('finna.html', title='Finna-haku', form=form)


@bp.route('/plotting', methods=['GET', 'POST'])
def plotting():
    if request.method == 'GET':
        form = PlottingForm()

        return render_template('plotting.html', title='Kuvaaja',
                               form=form)
    elif request.method == 'POST':
        form = PlottingForm()
        print('POST')

        if form.validate_on_submit():
            print('form validated')            

            # get the coefficients
            if form.const.data:
                const = form.const.data
            else:
                const = 0
            if form.x1.data:
                x1 = form.x1.data
            else:
                x1 = 0
            if form.x2.data:
                x2 = form.x2.data
            else:
                x2 = 0
            if form.x3.data:
                x3 = form.x3.data
            else:
                x3 = 0
            if form.x4.data:
                x4 = form.x4.data
            else:
                x4 = 0
            if form.x_start.data:
                x_start = form.x_start.data
            else:
                x_start = -5
            if form.x_end.data:
                x_end = form.x_end.data
            else:
                x_end = 5
            
            # form the figure title
            otsikko = ''
            for coeff, nome in zip([x4, x3, x2, x1, const], 
            ['x^4', 'x^3', 'x^2', 'x', '']):
                if coeff != 0:
                    if coeff > 0:
                        otsikko = otsikko + str(coeff) + nome + " + "
                    else:
                        otsikko = otsikko[:-2] + "- " + str(coeff).lstrip('-') + nome + " + "
            otsikko = f"y = {otsikko.rstrip(' +*')} x:n arvoilla {x_start} ≤ x ≤ {x_end}".replace('.', ',')
            print('otsikko: ', otsikko)

            # create the data to plot
            x = np.linspace(x_start, x_end, 100)
            y = const + x1 * x + x2 * x **2 + x3 * x ** 3 + x4 * x ** 4
            
            # generate the figure
            fig = Figure()

            ax = fig.subplots()
            ax.plot(x, y)
            ax.set_title(otsikko)
            ax.axhline(y=0, color='k')
            ax.axvline(x=0, color='k')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.grid()

            # save it to a temporary buffer
            buf = BytesIO()
            fig.savefig(buf, format='png')

            # prepare the data for html output
            data = base64.b64encode(buf.getbuffer()).decode("ascii")

            return render_template('plotting.html', title='Kuvaaja',
                               form=form, data=data)

        flash('Tarkista syöttämäsi arvot.')
        return render_template('plotting.html', title='Kuvaaja',
                               form=form)


@bp.route('/nutrients', methods=['GET', 'POST'])
def nutrients():
    if request.method == 'GET':
        form = NutrientForm()
        return render_template('nutrients.html', title='Ravintoaineet',
                               form=form)
    elif request.method == 'POST':
        form = NutrientForm()
        
        if form.validate_on_submit():
            print('form validated')
            rda = get_rda("nkeski")
            print(rda.head())
            
            # get data from the db
            with sqlite3.connect('fineli.db') as conn:
                # the next line prints the full sql query if uncommented
                #conn.set_trace_callback(print)
                curs = conn.cursor()
                try:
                    # get the food id using sqlite3 cursor
                    stmt = "SELECT foodid FROM food WHERE foodname = ?"
                    args = (form.food.data,)
                    curs.execute(stmt, args)
                    food = curs.fetchone()
                    if food:
                        food_id = food[0]
                        amount = form.amount.data
                        # get the nutrient content of the given food using pandas
                        stmt2 = "SELECT eufdname, bestloc / 100.0 * ? AS eaten_total FROM component_value WHERE foodid = ?"
                        args2 = (amount, food_id)
                        eaten_df = pd.read_sql(stmt2, conn, params=args2)
                        print(eaten_df.head())
                        # get the remaining portion of rda to be covered by other foods
                        remainder_df = pd.merge(rda, eaten_df, on='EUFDNAME')
                        remainder_df["remainder"] = remainder_df["target"] - remainder_df["eaten_total"]
                        print(remainder_df.head())
                    else:
                        flash('Valitse ruoka listasta.')
                        return render_template('nutrients.html', title='Ravintoaineet',
                               form=form)
                    
                    
                except Exception as e:
                    print(e)
                finally:
                    if curs:
                        curs.close()
            
            
            return render_template('nutrients.html', title='Ravintoaineet',
                                   form=form, data_given=(food_id, amount),
                                   tables=[remainder_df[['name', 'target', 'eaten_total', 'remainder']].to_html(classes='data', index = False)],
                                   header=True)
        
        flash('Tarkista syöttämäsi arvot.')
        return render_template('nutrients.html', title='Ravintoaineet',
                               form=form)

@bp.route('/autocomplete_food', methods=['GET'])
def autocomplete_food():
    search = request.args.get('q')
    arg = "%" + str(search) + "%"  # note: no manually added quotes around the argument
    print("arg:", arg)
    with sqlite3.connect('fineli.db') as conn:
        # the next line prints the full sql query if uncommented
        #conn.set_trace_callback(print)
        curs = conn.cursor()
        try:
            stmt = "SELECT foodname FROM food WHERE foodname LIKE ?"
            args = (arg,)
            print(stmt)
            #return [(x[0], x[1]) for x in curs.execute(stmt)]
            curs.execute(stmt, args)
            #foods = curs.fetchall()
            results = [food[0] for food in curs.fetchall()]
            #print(results)
            return jsonify(matching_results=results)
        except Exception as e:
            print(e)
        finally:
            if curs:
                curs.close()


