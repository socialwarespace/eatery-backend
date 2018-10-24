from os import environ
from pprint import pprint
from yelpapi import YelpAPI

API_KEY = environ.get('YELP_API_KEY')
[LATITUDE, LONGITUDE] = [42.447419, -76.470862]

yelp_api = YelpAPI(API_KEY)

def yelp_search(text, latitude=LATITUDE, longitude=LONGITUDE):
  try:
    print 'searching..'
    search = yelp_api.search_query(term=text, longitude=longitude, latitude=latitude, limit=5)
    eatery = search['businesses'][0]
    eatery_id = eatery['id']
    id_query = yelp_api.business_query(id=eatery_id)
    pprint(id_query)
  except Exception as e:
    print 'something went wrong: ', e

# yelp_search('collegetown bagels')
# yelp_search('plum tree')
# yelp_search('miyake')
# yelp_search('alladins')
