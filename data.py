from constants import *
from datetime import date, datetime
from requests import get
import schema
from threading import Timer

dining_items = {}
eateries = {}
events = {}
items = {}
menus = {}
operating_hours = {}
today = date.today()

def start_update():
  try:
    print('[{0}] Updating data'.format(datetime.now()))
    dining_query = get(CORNELL_DINING_URL)
    data_json = dining_query.json()
    parse(data_json)
    statics_json = get(STATIC_EATERIES_URL).json()
    parse_static_eateries(statics_json)
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
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        dining_items=parse_dining_items(eatery, eatery['id']),
        eatery_type=parse_eatery_type(eatery),
        id=safe_parse(eatery, 'id'),
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
  return ASSET_BASE_URL + 'eatery-images/' + slug + '.jpg'

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
        cal_summary=safe_parse(event, 'calSummary'),
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

def parse_dining_items(eatery, eatery_id):
  try:
    global dining_items
    new_dining_items = []
    item_list = eatery['diningItems']
    for item in item_list:
      new_dining_item = schema.DiningItemType(
          category=safe_parse(item, 'category'),
          description=safe_parse(item, 'descr'),
          healthy=safe_parse(item, 'healthy', False),
          item=safe_parse(item, 'item'),
          show_category=safe_parse(item, 'showCategory')
      )
      new_dining_items.append(new_dining_item)
    dining_items[eatery_id] = new_dining_items
    return new_dining_items
  except Exception:
    return []

def parse_coordinates(eatery):
  try:
    new_coordinates = schema.CoordinatesType(
        latitude=eatery['coordinates']['latitude'],
        longitude=eatery['coordinates']['longitude']
    )
    return new_coordinates
  except Exception:
    new_coordinates = schema.CoordinatesType(
        latitude=0.0,
        longitude=0.0
    )
    return new_coordinates

def parse_campus_area(eatery):
  if 'campusArea' in eatery.keys():
    new_campus_area = schema.CampusAreaType(
        description=eatery['campusArea']['descr'],
        description_short=eatery['campusArea']['descrshort']
    )
    return new_campus_area
  else:
    new_campus_area = schema.CampusAreaType(
        description='',
        description_short=''
    )
    return new_campus_area

def parse_static_eateries(statics_json):
  global eateries
  for eatery in statics_json['eateries']:
    new_id = resolve_id(eatery)
    new_eatery = schema.EateryType(
        about=safe_parse(eatery, 'about'),
        about_short=safe_parse(eatery, 'aboutshort'),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        dining_items=parse_dining_items(eatery, new_id),
        eatery_type=parse_eatery_type(eatery),
        id=new_id,
        image_url=get_image_url(eatery['slug']),
        location=safe_parse(eatery, 'location'),
        name=safe_parse(eatery, 'name'),
        name_short=safe_parse(eatery, 'nameshort'),
        operating_hours=parse_static_op_hours(eatery['operatingHours'], new_id),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=parse_phone(eatery['contactPhone'], eatery['name']),
        slug=safe_parse(eatery, 'slug')
    )
    eateries[new_eatery.id] = new_eatery

def safe_parse(obj, key, default=''):
  try:
    value = obj[key]
    if value is None:
      return default
    return value
  except Exception:
    return default

def resolve_id(obj):
  try:
    id = obj['id']
    return id

  except Exception:
    global eateries
    for i in range(100):
      test_id = 100 - i
      if test_id not in eateries:
        return test_id

def parse_eatery_type(eatery):
  try:
    return eatery['eateryTypes'][0]['descr']
  except Exception:
    return 'unknown'

def parse_static_op_hours(hours_list, eatery_id):
  weekdays = {}
  for hours in hours_list:
    if hours['weekday'] not in WEEKDAYS.keys():
      print 'weekday key: ' + hours['weekday'] + ' not in constants WEEKDAYS!'
      continue
    for weekday in WEEKDAYS[hours['weekday']]:
      if weekday not in weekdays:
        weekdays[weekday] = hours['events']

  global operating_hours
  global today
  new_operating_hours = []
  for i in range(8):
    new_date = date(today.year, today.month, today.day + i)
    weekday = new_date.weekday()
    new_events = weekdays[weekday] if weekday in weekdays.keys() else []
    new_operating_hour = schema.OperatingHoursType(
        date=new_date,
        events=parse_events(new_events, eatery_id),
        status='EVENTS'
    )
    new_operating_hours.append(new_operating_hour)
  operating_hours[eatery_id] = new_operating_hours
  return new_operating_hours


start_update()
