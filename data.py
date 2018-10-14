# Will update the graphQL db by calling scraper.py every defined time interval
import requests
import schema
from bs4 import BeautifulSoup

URL = 'https://now.dining.cornell.edu/api/1.0/dining/eateries.json'
PAYMENT_METHODS = {
  'swipes': 'Meal Plan - Swipe',
  'brbs': 'Meal Plan - Debit',
  'cornell_card': 'Cornell Card',
  'credit': 'Major Credit Cards',
  'mobile': 'Mobile Payments'
}

eateries = {}
operating_hours = {}
events = {}
menus = {}
items = {}

def start_update():
  try:
    result = requests.get(URL)
    data_json = result.json()
    parse(data_json)
    schema.Data.update_data(
      eateries=eateries,
      operating_hours=operating_hours,
      events=events,
      menus=menus,
      items=items)
  except as e:
    print(e)


def parse(data_json):
  global eateries
  for eatery in data_json['data']['eateries']:
    new_eatery = schema.EateryType(
      id=eatery['id'],
      slug=eatery['slug'],
      name=eatery['name'],
      name_short=eatery['nameshort'],
      about=eatery['about'],
      about_short=eatery['aboutshort'],
      image_url=parse_image_url(eatery['about']),
      payment_methods=parse_payment_methods(eatery['payMethods']),
      calender_id=eatery['googleCalenderId'],
      location=eatery['location'],
      operating_hours=parse_operating_hours(eatery['operatingHours']),
      coordinates=parse_coordinates(eatery['coordinates']),
      campus_area=parse_campus_area(eatery['campusArea'])
      )
    eateries[new_eatery.id] = new_eatery
    operating_hours[new_eatery.id] = new_operating_hours


def parse_image_url(string):
  soup = BeautifulSoup(string, 'lxml')
  image_url = soup.find('img')['src']
  return image_url

def parse_payment_methods(payment_methods):
  new_payment_methods = schema.PaymentMethodsType()

  if any(method['descrshort'] == PAYMENT_METHODS['swipes'] for method in payment_methods):
    new_payment_methods.swipes = True
  else:
    new_payment_methods.swipes = False
  if any(method['descrshort'] == PAYMENT_METHODS['brbs'] for method in payment_methods):
    new_payment_methods.brbs = True
  else:
    new_payment_methods.brbs = False
  if any(method['descrshort'] == PAYMENT_METHODS['credit'] for method in payment_methods):
    new_payment_methods.credit = True
    new_payment_methods.cash = True
  else:
    new_payment_methods.credit = False
    new_payment_methods.cash = False
  if any(method['descrshort'] == PAYMENT_METHODS['cornell_card'] for method in payment_methods):
    new_payment_methods.cornell_card = True
  else:
    new_payment_methods.cornell_card = False
  if any(method['descrshort'] == PAYMENT_METHODS['mobile'] for method in payment_methods):
    new_payment_methods.mobile = True
  else:
    new_payment_methods.mobile = False

  return new_payment_methods

def parse_operating_hours(dict, eatery_id):
  new_operating_hours = schema.OperatingHoursType(
    date=dict['date'],
    status=dict['status']
    events=parse_events(dict['events'])
    )
  global operating_hours[eatery_id] = new_operating_hours
  return new_operating_hours

def parse_events(events, eatery_id):
  new_events = []
  for event in events:
    new_event = schema.EventType(
      description=event['descr'],
      menu=parse_food_stations(event['menu']),
      start_time=event['start'],
      end_time=event['end'],
      cal_summary=event['calSummary']
      )
    new_events.append(new_event)
  global events[eatery_id] = new_events
  return new_events

def parse_food_stations(stations, eatery_id):
  new_stations = []
  for station in stations:
    new_station = schema.FoodStationType(
      category=station['category'],
      sort_idx=station['sortIdx'],
      items=parse_food_items(station['items'])
      )
    new_stations.append(new_station)
  global menus[eatery_id] = new_stations
  return new_stations

def parse_food_items(items, eatery_id):
    new_food_items = []
    for item in items:
      new_food_item = schema.FoodItemType(
        item=item['item'],
        healthy=item['healthy'],
        sort_idx=item['sortIdx']
        )
      new_food_items.append(new_food_item)
    global items[eatery_id] = new_food_items
    return new_food_items

def parse_coordinates(dict):
  new_coordinates = schema.CoordinatesType(
    latitude=dict['latitude'],
    longitude=dict['longitude']
    )

  return new_coordinates

def parse_campus_area(dict):
  new_campus_area = schema.CampusAreaType(
    description=dict['descr'],
    description_short=dict['descrshort']
    )

  return new_campus_area
