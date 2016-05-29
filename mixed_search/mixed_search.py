from flask import Flask, request, render_template, redirect
from crawler.start_crawler import start_crawlers
from indexer.indexer import start_indexer, full_index
from indexer.searcher import search as search_index
from urllib.parse import quote

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    param = request.args.get('search_param')
    if param is None:
        return redirect('/')
    page = request.args.get('page')
    if page is None:
        page = 0
    else:
        page = int(page)
    result = search_index(param, page=page)
    prev = page - 1
    if prev < 0:
        prev = None
    else:
        prev = str(prev)
    nxt = str(page + 1)
    param = quote(param)
    return render_template(
        'search.html',
        query=param,
        result=result,
        page=str(page),
        prev=prev,
        next=nxt
    )


if __name__ == '__main__':
    print('Starting Crawlers')
    start_crawlers()
    print('Starting indexer')
    full_index()
    start_indexer()
    print('Starting application')
    app.run()
