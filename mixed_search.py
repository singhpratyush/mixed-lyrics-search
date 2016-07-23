from json import dumps
from threading import Lock
from urllib.parse import quote

from flask import Flask, request, render_template, redirect

from indexer.indexer import start_indexer
from indexer.searcher import search as search_index

app = Flask(__name__)


# Index page
@app.route('/')
def home():
    # Render and show
    return render_template('home.html')


# Method to convert JSON to string
def j2s(json_dict, beautify=False):
    try:
        if beautify:
            # Dump to string with beautification
            return dumps(
                json_dict,
                indent=10,
                sort_keys=True
            )
        else:
            # Convert normally to string
            return dumps(json_dict)
    except Exception as e:  # Some problem in JSON
        print('{0}'.format(e))
        return ''


# API root
@app.route('/api', methods=['GET'])
def api():
    # Main dictionary object that will be converted to JSON
    json_dict = {}

    # Get search parameter
    search_parameter = request.args.get('search_param')
    if search_parameter is None:  # No parameter
        return j2s(json_dict)
    # Add to dictionary
    json_dict['search_parameter'] = search_parameter

    page = request.args.get('page')  # Page number
    if page is None:
        page = 0  # Default is 0
    else:
        try:
            page = int(page)  # Try to convert to integer
        except ValueError:
            json_dict['status'] = 1  # Error status
            json_dict['error_message'] = 'Invalid page number'
            return j2s(json_dict)  # Return with error
    json_dict['page'] = page  # Add to dict

    number = request.args.get('number')  # Number of results
    if number is None:
        number = 10  # Default is 10
    else:  # Get number to int or return error
        try:
            number = int(number)
        except ValueError:
            json_dict['status'] = 1
            json_dict['error_message'] = 'Invalid number of search results'
            return j2s(json_dict)
    json_dict['number'] = number  # Add to dict

    result = search_index(
        parameter=search_parameter,
        page=page,
        number=number
    )  # Perform search

    json_dict['search_results'] = result  # Add results to dict
    json_dict['status'] = 0  # Error status is zero

    return j2s(json_dict)  # Return response as raw string


# Route for Search Application
@app.route('/search', methods=['GET'])
def search():
    # Get parameters
    param = request.args.get('search_param')
    artist = request.args.get('artist')
    album = request.args.get('album')

    page = request.args.get('page')
    if page is None:
        page = 0
    else:
        page = int(page)

    if not (artist or album) is None:  # Either was given
        if len(param + artist + album) == 0:  # Overall length was 0
            return redirect('/')  # Redirect to home

        # Get query
        query = ''
        if len(param) > 0:
            query = param + ' '
        if len(album) > 0:
            query += 'movie:"' + album + '" '
        if len(artist) > 0:
            query += 'singers:"' + artist + '"'
    else:
        query = param  # Search query same as parameter

    # Perform search
    result = search_index(query, page=page, number=10)

    ids_presented = ''
    for x in result[:-1]:  # All but last result
        ids_presented += x['id'] + ','  # Seperate by comma
    if len(result) > 0:
        ids_presented += result[-1]['id']

    # Set previous page number
    prev = page - 1
    if prev < 0:
        prev = None
    else:
        prev = str(prev)
    # Set next page nummber
    nxt = str(page + 1)

    return render_template(
        'search.html',
        title=param,
        query=quote(query),
        result=result,
        page=str(page),
        prev=prev,
        next=nxt,
        ids_presented=ids_presented
    )  # Render and return template with appropriate parameters


# Route for redirect
@app.route('/redir', methods=['GET'])
def redir():
    # Get the url to redirect
    redirect_url = request.args.get('redirect_url')

    # Get the parameters
    id = request.args.get('id')
    param = request.args.get('param')
    ids_presented = request.args.get('ids_presented')
    page = request.args.get('page')

    # Prepare log statement
    log_statement = '{0}::::{1}::::{2}::::{3}\n'.format(
        param,
        id,
        ids_presented,
        page
    )

    # Acquire lock and write
    with lock:
        q_logger.write(log_statement)

    return render_template(
        'redirect.html',
        url=redirect_url
    )  # Render template and return


# Run application
if __name__ == '__main__':
    global q_logger, lock
    q_logger = open('responses.txt', 'a')
    lock = Lock()

    try:
        app.run(host='0.0.0.0', port='5000')  # Start application
    except KeyboardInterrupt:
        print('User interrupted')
