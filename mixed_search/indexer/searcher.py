import xapian
from crawler.db_operations import get_song_by_id


def search(parameter, page=0):
    db = xapian.Database('db')

    qp = xapian.QueryParser()
    qp.add_prefix('id', 'Q')
    qp.add_prefix('song_name', 'XS')
    qp.add_prefix('movie', 'XM')
    qp.add_prefix('lyrics', 'XL')
    qp.add_prefix('singers', 'XI')
    qp.add_prefix('directors', 'XD')
    qp.add_prefix('lyricists', 'XY')

    qry = qp.parse_query(parameter)

    enquire = xapian.Enquire(db)
    enquire.set_query(qry)

    offset = 10 * page
    results = enquire.get_mset(page*0, 10)

    result_set = []

    for result in results:
        result_set.append(
            get_song_by_id(
                str(result.document.get_data())[2:-1]
            )
        )

    return result_set
