import constants
from datetime import datetime
from requests import get
import schema
from threading import Timer

URL = 'https://now.dining.cornell.edu/api/1.0/dining/eateries.json'
PAY_METHODS = {
    'brbs': 'Meal Plan - Debit',
    'c-card': 'Cornell Card',
    'credit': 'Major Credit Cards',
    'mobile': 'Mobile Payments',
    'swipes': 'Meal Plan - Swipe'
}

dining_items = {}
eateries = {}
events = {}
items = {}
menus = {}
operating_hours = {}

def start_update():
  try:
    print('[{0}] Updating data'.format(datetime.now()))
    result = get(URL)
    data_json = result.json()
    parse(data_json)
    schema.Data.update_data(
        dining_items=dining_items,
        eateries=eateries,
        events=events,
        items=items,
        menus=menus,
        operating_hours=operating_hours
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
    )
    eateries[new_eatery.id] = new_eatery

def get_image_url(slug):
  return constants.ASSET_BASE_URL + 'eatery-images/' + slug + '.jpg'

def parse_phone(string, name):
  if string is None:
    return 'N/A'
  return string

def parse_payment_methods(methods):
  payment_methods = schema.PaymentMethodsType()
  payment_methods.brbs = any(pay['descrshort'] == PAY_METHODS['brbs'] for pay in methods)
  payment_methods.cash = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.credit = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.cornell_card = any(pay['descrshort'] == PAY_METHODS['c-card'] for pay in methods)
  payment_methods.mobile = any(pay['descrshort'] == PAY_METHODS['mobile'] for pay in methods)
  payment_methods.swipes = any(pay['descrshort'] == PAY_METHODS['swipes'] for pay in methods)
  return payment_methods

def parse_operating_hours(hours_list, eatery_id):
  global operating_hours
  new_operating_hours = []
  for hours in hours_list:
    new_operating_hour = schema.OperatingHoursType(
        date=hours['date'],
        events=parse_events(hours['events'], eatery_id),
        status=hours['status']
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
        cal_summary=event['calSummary'],
        description=event['descr'],
        end_time=event['end'],
        menu=stations,
        start_time=event['start'],
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
        items=station_items,
        item_count=len(station_items),
        sort_idx=station['sortIdx']
    )
    new_stations.append(new_station)
  menus[eatery_id] = new_stations
  return new_stations

def parse_food_items(item_list, eatery_id):
  global items
  new_food_items = []
  for item in item_list:
    new_food_item = schema.FoodItemType(
        healthy=item['healthy'],
        item=item['item'],
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
        category=item['category'],
        description=item['descr'],
        healthy=item['healthy'],
        item=item['item'],
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
