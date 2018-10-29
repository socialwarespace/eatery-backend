from bs4 import BeautifulSoup
import constants
from datetime import datetime
from requests import get
import schema
from threading import Timer

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
dining_items = {}

def start_update():
  try:
    print('[{0}] Updating data'.format(datetime.now()))
    result = get(URL)
    data_json = result.json()
    parse(data_json)
    schema.Data.update_data(
        eateries=eateries,
        operating_hours=operating_hours,
        events=events,
        menus=menus,
        items=items,
        dining_items=dining_items
    )
  except Exception as e:
    print('Data update failed:', e)
  finally:
    Timer(constants.UPDATE_DELAY, start_update).start()

def parse(data_json):
  global eateries
  for eatery in data_json['data']['eateries']:
    new_eatery = schema.EateryType(
        about=eatery['about'],
        about_short=eatery['aboutshort'],
        campus_area=parse_campus_area(eatery['campusArea']),
        coordinates=parse_coordinates(eatery['coordinates']),
        dining_items=parse_dining_items(eatery['diningItems'], eatery['id']),
        eatery_type=eatery['eateryTypes'][0]['descr'],
        id=eatery['id'],
        image_url=get_image_url(eatery['slug']),
        location=eatery['location'],
        name=eatery['name'],
        name_short=eatery['nameshort'],
        operating_hours=parse_operating_hours(eatery['operatingHours'], eatery['id']),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=parse_phone(eatery['contactPhone'], eatery['name']),
        slug=eatery['slug']
        # calender_id=eatery['googleCalenderId'],
    )
    eateries[new_eatery.id] = new_eatery

def get_image_url(slug):
  return constants.ASSET_BASE_URL + 'eatery-images/' + slug + '.jpg'

def parse_phone(string, name):
  if string is None:
    print(name+' missing phone number')
    return 'PHONE NUMBER NOT FOUND'
  return string
def parse_payment_methods(payment_methods):
  new_payment_methods = schema.PaymentMethodsType()
  new_payment_methods.swipes = any(method['descrshort'] == PAYMENT_METHODS['swipes'] for method in payment_methods)
  new_payment_methods.brbs = any(method['descrshort'] == PAYMENT_METHODS['brbs'] for method in payment_methods)
  new_payment_methods.credit = any(method['descrshort'] == PAYMENT_METHODS['credit'] for method in payment_methods)
  new_payment_methods.cash = any(method['descrshort'] == PAYMENT_METHODS['credit'] for method in payment_methods)
  new_payment_methods.cornell_card = any(method['descrshort'] == PAYMENT_METHODS['cornell_card'] for method in payment_methods)
  new_payment_methods.mobile = any(method['descrshort'] == PAYMENT_METHODS['mobile'] for method in payment_methods)
  return new_payment_methods

def parse_operating_hours(hours_list, eatery_id):
  global operating_hours
  new_operating_hours = []
  for hours in hours_list:
    new_operating_hour = schema.OperatingHoursType(
        date=hours['date'],
        status=hours['status'],
        events=parse_events(hours['events'], eatery_id)
    )
    new_operating_hours.append(new_operating_hour)
  operating_hours[eatery_id] = new_operating_hours
  return new_operating_hours

def parse_events(event_list, eatery_id):
  global events
  new_events = []
  for event in event_list:
    stations = parse_food_stations(event['menu'], eatery_id)
    new_event = schema.EventType(
        start_time=event['start'],
        end_time=event['end'],
        cal_summary=event['calSummary'],
        description=event['descr'],
        menu=stations,
        station_count=len(stations)
    )
    new_events.append(new_event)
  events[eatery_id] = new_events
  return new_events

def parse_food_stations(station_list, eatery_id):
  global menus
  new_stations = []
  for station in station_list:
    station_items = parse_food_items(station['items'], eatery_id)
    new_station = schema.FoodStationType(
        category=station['category'],
        sort_idx=station['sortIdx'],
        items=station_items,
        item_count=len(station_items)
    )
    new_stations.append(new_station)
  menus[eatery_id] = new_stations
  return new_stations

def parse_food_items(item_list, eatery_id):
  global items
  new_food_items = []
  for item in item_list:
    new_food_item = schema.FoodItemType(
        item=item['item'],
        healthy=item['healthy'],
        sort_idx=item['sortIdx']
    )
    new_food_items.append(new_food_item)
  items[eatery_id] = new_food_items
  return new_food_items

def parse_dining_items(item_list, eatery_id):
  global dining_items
  new_dining_items = []
  for item in item_list:
    new_dining_item = schema.DiningItemType(
        description=item['descr'],
        category=item['category'],
        item=item['item'],
        healthy=item['healthy'],
        show_category=item['showCategory']
    )
    new_dining_items.append(new_dining_item)
  dining_items[eatery_id] = new_dining_items
  return new_dining_items

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

start_update()
