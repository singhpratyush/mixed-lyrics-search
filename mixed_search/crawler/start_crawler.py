from crawler.base_crawler import CrawlerType0, CrawlerType1
from re import findall, DOTALL
from threading import Thread
from random import shuffle
from string import ascii_lowercase


class AZLyricsCrawler(CrawlerType1):
    def __init__(self, name, start_url, url_list, number_of_threads):
        super().__init__(name, start_url, url_list, number_of_threads)

    def get_artists_with_url(self, raw_html):
        refined = findall(
            r'<div class=\"col-sm-6 text-center artist-col\">(.*?)</div>  '
            r'<!-- container main-page -->',
            raw_html,
            DOTALL
        )[0]

        return findall(
            r'<a href=\"(.*?)\">(.*?)<',
            refined,
            DOTALL
        )

    def get_albums_with_songs(self, raw_html):
        data = []

        album_html = findall(
            r'iv class=\"album\">(.*?)<d',
            raw_html,
            DOTALL
        )

        for content in album_html:
            album_name = findall(
                r'<b>\"(.*?)\"',
                content,
                DOTALL
            )

            if len(album_name) == 0:
                album_name = 'other'
            else:
                album_name = album_name[0]

            songs_with_url = findall(
                r'<a href=\"\.\.(.*?)\" target=\"_blank\">(.*?)</a><br>',
                content
            )
            data.append(
                (
                    album_name,
                    songs_with_url
                )
            )

        return data

    def get_song_details(self, song_html):
        return findall(
            r'<div>.*?-->(.*?)</div>',
            song_html,
            DOTALL
        )[0].replace(
            '<br>',
            '\n'
        ).replace(
            '<i>',
            ''
        ).replace(
            '</i>',
            ''
        )


class HindilyricsCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        return findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)

    def get_songs_with_url(self, raw_html):
        return findall(r'<li>.*?\"(.*?)\">(.*?)<', raw_html)

    def get_song_details(self, raw_html):
        singers = modify_artist_hl(findall(r'Singer\(s\).*?:(.*?)<br>', raw_html))
        music_by = modify_artist_hl(findall(r'Music By.*?:(.*?)<br>', raw_html))
        lyricists = modify_artist_hl(findall(r'Lyricist.*?:(.*?)<br>', raw_html))

        lyrics = findall(
            r'<font face="verdana\">(.*?)</font',
            raw_html,
            DOTALL
        )[0]

        lyrics.replace(
            '\\\\n',
            '\n'
        ).replace(
            '\\r',
            ''
        )

        return lyrics, singers, music_by, lyricists


class LyricsMastiCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        refined = findall(
            r'<ul class="list-group list-group-flush">(.*?)</ul>',
            raw_html,
            DOTALL
        )[0]

        url_movie = findall(
            r'<a href=\"(.*?)\">\n(.*?)</a>',
            refined,
            DOTALL
        )

        return [(url, movie.strip(' \t\n\r')) for url, movie in url_movie]

    def get_songs_with_url(self, raw_html):
        refined = findall(
            r'<ol class="custom-counter">(.*?)</ol>',
            raw_html,
            DOTALL
        )[0]

        song_url = findall(
            r'<a.*?href=\"(.*?)\".*?3>(.*?)<',
            refined,
            DOTALL
        )

        return [(url, song.strip(' \t\n\r')) for url, song in song_url]

    def get_song_details(self, raw_html):
        refined = findall(
            r'<ul>(.*?)</ul>',
            raw_html,
            DOTALL
        )[0]

        singers = modify_artist_lm(
            findall(
                r'<h4>S.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        lyricists = modify_artist_lm(
            findall(
                r'<h4>L.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        directors = modify_artist_lm(
            findall(
                r'<h4>M.*?set.*?>(.*?)<',
                refined,
                DOTALL
            )
        )

        lyrics = findall(
            r'v><code.*?>(.*?)</',
            raw_html,
            DOTALL
        )[0]

        return lyrics, singers, directors, lyricists


class SmritiCrawler(CrawlerType0):
    def __init__(self, name, start_url, list_of_url, number_of_threads):
        super().__init__(name, start_url, list_of_url, number_of_threads)

    def get_movies_with_url(self, raw_html):
        main_content = findall(
            r'<a href=\"/hindi-songs/\">main index</a>(.*?)</div>',
            raw_html,
            DOTALL
        )[0]

        return findall(r'<a href=\"(.*?)\">(.*?)</a>', main_content)

    def get_songs_with_url(self, raw_html):
        return [
            (b, a.replace('.', '')) for a, b in findall(
                r'<div class="onesong">(.*?): <a href=.*?<a href="(.*?)">',
                raw_html,
                DOTALL
            )
            ]

    def get_song_details(self, raw_html):
        singers = modify_artist_sm(
            findall(
                r'<li><b>Singer\(s\):</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        directors = modify_artist_sm(
            findall(
                r'<li><b>Mu.*?:</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        lyricists = modify_artist_sm(
            findall(
                r'<li><b>L.*?:</b> <.*?>(.*?)</',
                raw_html,
                DOTALL
            )
        )

        lyrics = findall(
            r'<div class=\"son.*?>(.*?)</div>',
            raw_html,
            DOTALL
        )[0].replace(
            '<br>',
            '\n'
        ).replace(
            '<p>',
            ''
        ).replace(
            '</p>',
            '\n\n'
        ).replace(
            '<br/>',
            '\n'
        )

        return lyrics, singers, directors, lyricists


def modify_artist_sm(artist):
    if len(artist) > 0:
        return artist[0].split(', ')
    else:
        return []


def modify_artist_lm(artist):
    if len(artist) > 0:
        return artist[0].strip(' \t\n\r').replace(
            ' &amp;',
            ', '
        ).split(', ')
    else:
        return []


def modify_artist_hl(artist):
    if len(artist) > 0:
        return findall(
            r'\">(.*?)<',
            artist[0]
        )
    else:
        return []


def az_crawler():
    list_of_initials = ['19', ] + list(ascii_lowercase)

    shuffle(list_of_initials)

    crawler = AZLyricsCrawler(
        'AZ Lyrics Crawler',
        'http://azlyrics.com',
        ['/{0}.html'.format(i) for i in list_of_initials],
        1
    )

    crawler.run()


def hl_crawler():
    dict_pages = {
        '0': 1,
        'a': 6,
        'b': 4,
        'c': 3,
        'd': 4,
        'e': 1,
        'f': 1,
        'g': 2,
        'h': 3,
        'i': 2,
        'j': 3,
        'k': 4,
        'l': 2,
        'm': 4,
        'n': 2,
        'o': 1,
        'p': 3,
        'q': 1,
        'r': 2,
        's': 4,
        't': 2,
        'u': 1,
        'v': 1,
        'w': 1,
        'y': 1,
        'z': 1
    }

    list_of_initials = ['0', ] + list(ascii_lowercase[:])
    list_of_initials.remove('x')

    list_of_websites = []
    for initial in list_of_initials:
        for page in range(1, dict_pages[initial]):
            list_of_websites.append(
                '/lyrics/hindi-songs-starting-{0}-page-{1}.html'.format(
                    initial,
                    page
                )
            )

    crawler = HindilyricsCrawler(
        'hindilyrics-crawler',
        'http://www.hindilyrics.net',
        list_of_websites,
        4
    )

    crawler.run()


def lm_crawler():
    dict_pages = {
        '%23': 2,
        'a': 17,
        'b': 11,
        'c': 7,
        'd': 14,
        'e': 3,
        'f': 3,
        'g': 6,
        'h': 8,
        'i': 3,
        'j': 8,
        'k': 11,
        'l': 4,
        'm': 12,
        'n': 5,
        'o': 2,
        'p': 9,
        'q': 1,
        'r': 6,
        's': 13,
        't': 6,
        'u': 2,
        'v': 2,
        'w': 2,
        'x': 1,
        'y': 3,
        'z': 2
    }

    list_of_initials = ['%23', ] + list(ascii_lowercase[:])

    list_of_websites = []
    for initial in list_of_initials:
        for page in range(1, dict_pages[initial] + 1):
            list_of_websites.append(
                '/songs_for_movie_{0}.html?page={1}'.format(
                    initial,
                    page
                )
            )

    crawler = LyricsMastiCrawler(
        'LyricsMasti Crawler',
        'http://www.lyricsmasti.com',
        list_of_websites,
        4
    )

    crawler.run()


def sm_crawler():
    initials = [1, ] + list(ascii_lowercase)
    initials.remove('x')

    urls = []
    for element in initials:
        urls.append(
            '/hindi-songs/movies-{0}'.format(element)
        )

    crawler = SmritiCrawler(
        'Smriti',
        'http://smriti.com',
        urls,
        4
    )

    crawler.run()


def start_crawlers():

    threads = []

    t_az = Thread(target=az_crawler)
    t_az.daemon = True
    t_az.start()
    threads.append(t_az)

    t_hl = Thread(target=hl_crawler)
    t_hl.daemon = True
    t_hl.start()
    threads.append(t_hl)

    t_lm = Thread(target=lm_crawler)
    t_lm.daemon = True
    t_lm.start()
    threads.append(t_lm)

    t_sm = Thread(target=sm_crawler)
    t_sm.daemon = True
    t_sm.start()
    threads.append(t_sm)