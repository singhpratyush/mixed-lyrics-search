from json import dumps
from urllib.parse import quote

from flask import Flask, request, render_template, redirect
from threading import Lock

from indexer.indexer import start_indexer, full_index
from indexer.searcher import search as search_index
from crawler import start_crawler

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


def j2s(json_dict, beautify=False):
    try:
        if beautify:
            return dumps(
                json_dict,
                indent=10,
                sort_keys=True
            )
        else:
            return dumps(json_dict)
    except Exception as e:
        print('{0}'.format(e))
        return ''


@app.route('/api', methods=['GET'])
def api():
    json_dict = {}

    search_parameter = request.args.get('search_param')
    if search_parameter is None:
        return j2s(json_dict)
    json_dict['search_parameter'] = search_parameter

    page = request.args.get('page')
    if page is None:
        page = 0
    else:
        try:
            page = int(page)
        except ValueError:
            json_dict['status'] = 1
            json_dict['error_message'] = 'Invalid page number'
            return j2s(json_dict)
    json_dict['page'] = page

    number = request.args.get('number')
    if number is None:
        number = 10
    else:
        try:
            number = int(number)
        except ValueError:
            json_dict['status'] = 1
            json_dict['error_message'] = 'Invalid number of search results'
            return j2s(json_dict)
    json_dict['number'] = number

    result = search_index(
        parameter=search_parameter,
        page=page,
        number=number
    )

    json_dict['search_results'] = result
    json_dict['status'] = 0

    return j2s(json_dict)


@app.route('/search', methods=['GET'])
def search():
    param = request.args.get('search_param')
    artist = request.args.get('artist')
    album = request.args.get('album')

    page = request.args.get('page')
    if page is None:
        page = 0
    else:
        page = int(page)

    if not (artist or album) is None:
        if len(param + artist + album) == 0:
            return redirect('/')

        query = ''
        if len(param) > 0:
            query = param + ' '
        if len(album) > 0:
            query += 'movie:"' + album + '" '
        if len(artist) > 0:
            query += 'singers:"' + artist + '"'
    else:
        query = param

    result = search_index(query, page=page, number=10)

    ids_presented = ''
    for x in result[:-1]:
        ids_presented += x['id'] + ','
    ids_presented += result[-1]['id']

    prev = page - 1
    if prev < 0:
        prev = None
    else:
        prev = str(prev)
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
    )


@app.route('/redir', methods=['GET'])
def redir():
    redirect_url = request.args.get('redirect_url')

    id = request.args.get('id')
    param = request.args.get('param')
    ids_presented = request.args.get('ids_presented')
    page = request.args.get('page')

    log_statement = '{0}::::{1}::::{2}::::{3}\n'.format(
        param,
        id,
        ids_presented,
        page
    )

    with lock:
        q_logger.write(log_statement)

    return render_template(
        'redirect.html',
        url=redirect_url
    )


if __name__ == '__main__':
    print('Starting Crawlers')
    # start_crawler()
    print('Starting indexer')
    # full_index()
    start_indexer()
    print('Starting application')
    global q_logger, lock
    q_logger = open('responses.txt', 'a')
    lock = Lock()
    try:
        app.run()
    except KeyboardInterrupt:
        print('User interrupted')
