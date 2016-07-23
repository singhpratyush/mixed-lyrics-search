from threading import Thread

from crawler import azlyrics_crawler, hindilyrics_crawler, lyricsmasti_crawler, metrolyrics_crawler, smriti_crawler


def worker(name):
    if name == 'azlyrics':
        azlyrics_crawler.main()
    if name == 'hindilyrics':
        hindilyrics_crawler.main()
    if name == 'lyricsmasri':
        lyricsmasti_crawler.main()
    if name == 'metrolyrics':
        metrolyrics_crawler.main()
    if name == 'smriti':
        smriti_crawler.main()


def start():
    crawler_names = [
        'azlyrics',
        'hindilyrics',
        'lyricsmasti',
        'metrolyrics',
        'smriti'
    ]

    for crawler_name in crawler_names:
        thread = Thread(target=worker, args=(crawler_name,))
        thread.daemon = True
        thread.start()
