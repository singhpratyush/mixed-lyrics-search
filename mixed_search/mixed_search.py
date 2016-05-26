from flask import Flask, request, render_template
from crawler.start_crawler import start_crawlers
from indexer.indexer import start_indexer, full_index
from indexer.searcher import search as search_index

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/search', methods=['GET'])
def search():
    param = request.args.get('search_param')
    result = search_index(param)
    return render_template('search.html', query=param, result=result)


if __name__ == '__main__':
    print('Starting Crawlers')
    start_crawlers()
    print('Starting indexer')
    full_index()
    start_indexer()
    print('Starting application')
    app.run()
