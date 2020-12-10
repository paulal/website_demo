from flask import Flask, render_template, make_response, request, redirect, flash, url_for
from config import Config
from flask_bootstrap import Bootstrap
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from finna_client import *
from forms import FinnaForm
import re


# create a flask object
app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

# define a route
@app.route('/')
def welcome():
    return '<h1>Welcome to my app!</h1>'

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/<page_name>')
def other_page(page_name):
    response = make_response('The page named %s does not exist.' % page_name, 404)
    return response

#pass the variables to the page
@app.route('/index')
def index():
    #title = 'Homepage'
    user = {'username': 'Elisa'} # dict
    cities = ['Helsinki', 'Espoo'] # list
    favorite_movies = ['Inception', 'Shutter Island'] # list
    band = 'Hurriganes' #str
    user_birth_date = datetime(2000, 3, 20) #datetime
    books = [{'author': 'J. R. R. Tolkien', 'title': 'The Lord of the Rings'}, 
    {'author': 'Christopher Paolini', 'title': 'Eragon'}, {'author': 'Timo Parvela', 'title': 'Ella ja kaverit metsässä'}]
    return render_template('index.html', 
    #title=title, 
    user=user, cities=cities, favorite_movies=favorite_movies,
    band=band, user_birth_date=user_birth_date, books=books)

@app.route('/index2')
def index2():
    user = {'username': 'Miguel'}
    posts = [
        {'author': {'username': 'John'}, 
        'body': 'Beautiful day in Portland!'},
        {'author': {'username': 'Susan'},
        'body': 'The Avengers movie was so cool!'}
    ]
    return render_template('index2.html', title='Home', user=user, posts=posts)

# adding links between pages
@app.route('/base')
def basepage():
    return render_template('base.html')

@app.route('/about')
def aboutpage():
    return render_template('about.html')

@app.route('/finna', methods=['GET', 'POST'])
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
            if form.target.data == 'all':
                result = finna.search(form.search_term.data,
                              search_type=FinnaSearchType.AllFields,
                              fields=['fullRecord'],
                              filters=['format:0/Book/'], 
                              limit=40)
            elif form.target.data == 'author':
                result = finna.search(form.search_term.data,
                              search_type=FinnaSearchType.Author,
                              fields=['fullRecord'],
                              filters=['format:0/Book/'], 
                              limit=50)
                print(f'result: {result}')
            else:
                result = finna.search(form.search_term.data,
                              search_type=FinnaSearchType.Title,
                              fields=['fullRecord'],
                              filters=['format:0/Book/'], 
                              limit=50)
            if result['resultCount'] == 0:
                flash('Mitään ei löytynyt. Yritä uudelleen.')
                return redirect(url_for('finna'))
            
            records_set = set()
            print(result)
            for rec in result['records']:
                print('rec = ', rec)
                tree = ET.fromstring(rec['fullRecord'])
                record = {}
                
                for datafield in tree.iter('{http://www.loc.gov/MARC21/slim}datafield'):
                    #print('datafield.attrib =', datafield.attrib)
                    if datafield.attrib['tag'] == '041':
                        lang = datafield[0].text
                        print(f'lang = {lang}')
                        record['lang'] = lang
                        if len(datafield) > 1:
                            source_lang = datafield[1].text
                            print('source lang=', source_lang)
                            record['source_lang'] = source_lang
                    elif datafield.attrib['tag'] == '100':
                        print('author=', datafield[0].text)
                        #author_spl = datafield[0].text.rstrip('.').rstrip(',').split(', ')
                        #author = author_spl[1] + ' ' + author_spl[0]
                        #print('author =', author)
                        #record['author'] = author
                        author = datafield[0].text.rstrip('.').rstrip(',')
                        record['author'] = author
                    elif datafield.attrib['tag'] == '245':
                        #print(datafield[0].text)
                        title = datafield[0].text.rstrip(' /')
                        #author = datafield[1].text.split(' ;')[0]
                        #print('author =', author)
                        print('title =', title)
                        #record['author'] = author
                        record['title'] = title
                try:
                    if record['lang'] == form.language.data or form.language.data == 'all':
                        json_record = json.dumps(record)
                        print(json_record)
                        records_set.add(json_record)
                except KeyError:
                    pass

                
                '''
                for key in rec['authors']['primary']:
                    record['author_lastfirst'] = key
                    author_spl = key.split(', ')
                    author = author_spl[1] + " " + author_spl[0]
                    print('author_spl =', author_spl)
                    print('author =', author)
                    record['author'] = author
                    '''
                #record['title'] = rec['title']
                #record['lang'] = rec['languages'][0]
            records = [json.loads(x) for x in records_set]
            print(f'records: {records}')
            
            return render_template('finna.html', title='Finna-haku',
                               form=form, result=result, records=records)
        
        return render_template('finna.html', title='Finna-haku', form=form)


if __name__=='__main__':
    app.run(debug=True)