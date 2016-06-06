from json import dumps
from urllib.parse import quote

from flask import Flask, request, render_template, redirect

from indexer.indexer import start_indexer, full_index
from indexer.searcher import search as search_index

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

    if len(param + artist + album) == 0:
        return redirect('/')

    query = ''
    if len(param) > 0:
        query = param + ' '
    if len(album) > 0:
        query += 'movie:"' + album + '" '
    if len(artist) > 0:
        query += 'singers:"' + artist + '"'

    page = request.args.get('page')
    if page is None:
        page = 0
    else:
        page = int(page)

    search_type = request.args.get('type')
    if search_type != 'all':
        param = """{0}:\"{1}\"""".format(
            search_type,
            param
        )

    print(query)
    result = search_index(query, page=page, number=10)

    prev = page - 1
    if prev < 0:
        prev = None
    else:
        prev = str(prev)
    nxt = str(page + 1)

    return render_template(
        'search.html',
        title=param,
        query=quote(param),
        result=result,
        page=str(page),
        prev=prev,
        next=nxt
    )


@app.route('/redir', methods=['GET'])
def redir():
    redirect_url = request.args.get('redirect_url')
    return render_template(
        'redirect.html',
        url=redirect_url
    )


if __name__ == '__main__':
    print('Starting Crawlers')
    # start_crawlers()
    print('Starting indexer')
    # full_index()
    start_indexer()
    print('Starting application')
    app.run()