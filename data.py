from constants import (
    CORNELL_DINING_URL,
    IMAGES_URL,
    NUM_DAYS_STORED_IN_DB,
    STATIC_EATERIES_URL,
    PAY_METHODS,
    UPDATE_DELAY,
    WEEKDAYS
)
from datetime import date, datetime, timedelta
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
    Timer(UPDATE_DELAY, start_update).start()

def parse(data_json):
  global eateries
  for eatery in data_json['data']['eateries']:
    eatery_id = eatery.get('id', resolve_id(eatery))
    new_eatery = schema.EateryType(
        about=eatery.get('about', ''),
        about_short=eatery.get('aboutshort', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        dining_items=parse_dining_items(eatery, eatery_id),
        eatery_type=parse_eatery_type(eatery),
        id=eatery_id,
        image_url=get_image_url(eatery.get('slug')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_operating_hours(eatery, eatery_id),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=eatery.get('contactPhone', 'N/A'),
        slug=eatery.get('slug')
    )
    eateries[new_eatery.id] = new_eatery

def get_image_url(slug):
  return IMAGES_URL + slug + '.jpg'

def parse_payment_methods(methods):
  payment_methods = schema.PaymentMethodsType()
  payment_methods.brbs = any(pay['descrshort'] == PAY_METHODS['brbs'] for pay in methods)
  payment_methods.cash = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.credit = any(pay['descrshort'] == PAY_METHODS['credit'] for pay in methods)
  payment_methods.cornell_card = any(pay['descrshort'] == PAY_METHODS['c-card'] for pay in methods)
  payment_methods.mobile = any(pay['descrshort'] == PAY_METHODS['mobile'] for pay in methods)
  payment_methods.swipes = any(pay['descrshort'] == PAY_METHODS['swipes'] for pay in methods)
  return payment_methods

def parse_operating_hours(eatery, eatery_id):
  global operating_hours
  new_operating_hours = []
  hours_list = eatery['operatingHours']
  for hours in hours_list:
    new_date = hours.get('date', '')
    new_operating_hour = schema.OperatingHoursType(
        date=new_date,
        events=parse_events(hours['events'], eatery_id, new_date),
        status=hours.get('status', '')
    )
    new_operating_hours.append(new_operating_hour)
  operating_hours[eatery_id] = new_operating_hours
  return new_operating_hours

def parse_events(event_list, eatery_id, date):
  global events
  new_events = []
  for event in event_list:
    [start, end] = format_time(event.get('start', ''), event.get('end', ''), date)
    stations = parse_food_stations(event['menu'], eatery_id)
    new_event = schema.EventType(
        cal_summary=event.get('calSummary', ''),
        description=event.get('descr', ''),
        end_time=end,
        menu=stations,
        start_time=start,
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
        category=station.get('category', ''),
        items=station_items,
        item_count=len(station_items),
        sort_idx=station.get('sortIdx', '')
    )
    new_stations.append(new_station)
  menus[eatery_id] = new_stations
  return new_stations

def parse_food_items(item_list, eatery_id):
  global items
  new_food_items = []
  for item in item_list:
    new_food_item = schema.FoodItemType(
        healthy=item.get('healthy', False),
        item=item.get('item', ''),
        sort_idx=item.get('sortIdx', '')
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
          category=item.get('category', ''),
          description=item.get('descr', ''),
          healthy=item.get('healthy', False),
          item=item.get('item', ''),
          show_category=item.get('showCategory', '')
      )
      new_dining_items.append(new_dining_item)
    dining_items[eatery_id] = new_dining_items
    return new_dining_items
  except Exception:
    return []

def parse_coordinates(eatery):
  if 'coordinates' in eatery:
    new_coordinates = schema.CoordinatesType(
        latitude=eatery['coordinates']['latitude'],
        longitude=eatery['coordinates']['longitude']
    )
  else:
    new_coordinates = schema.CoordinatesType(
        latitude=0.0,
        longitude=0.0
    )
  return new_coordinates

def parse_campus_area(eatery):
  if 'campusArea' in eatery:
    new_campus_area = schema.CampusAreaType(
        description=eatery['campusArea']['descr'],
        description_short=eatery['campusArea']['descrshort']
    )
  else:
    new_campus_area = schema.CampusAreaType(
        description='',
        description_short=''
    )
  return new_campus_area

def parse_static_eateries(statics_json):
  global eateries
  for eatery in statics_json['eateries']:
    new_id = eatery.get('id', resolve_id(eatery))
    new_eatery = schema.EateryType(
        about=eatery.get('about', ''),
        about_short=eatery.get('aboutshort', ''),
        campus_area=parse_campus_area(eatery),
        coordinates=parse_coordinates(eatery),
        dining_items=parse_dining_items(eatery, new_id),
        eatery_type=parse_eatery_type(eatery),
        id=new_id,
        image_url=get_image_url(eatery.get('slug')),
        location=eatery.get('location', ''),
        name=eatery.get('name', ''),
        name_short=eatery.get('nameshort', ''),
        operating_hours=parse_static_op_hours(eatery['operatingHours'], new_id),
        payment_methods=parse_payment_methods(eatery['payMethods']),
        phone=eatery.get('contactPhone', 'N/A'),
        slug=eatery.get('slug', '')
    )
    eateries[new_eatery.id] = new_eatery

def resolve_id(eatery):
  """Returns a new id (int) for an external eatery
  If the eatery does not have a provided id, we need to make one for it.
  Simply gets the maximum id currently in our eateries and makes new id +1
  """
  if 'id' in eatery:
    return eatery['id']

  global eateries
  max_id = max(eateries)
  return max_id + 1

def parse_eatery_type(eatery):
  try:
    return eatery['eateryTypes'][0]['descr']
  except Exception:
    return 'Unknown'

def parse_static_op_hours(hours_list, eatery_id):
  weekdays = {}
  for hours in hours_list:
    if hours['weekday'] not in WEEKDAYS:
      print('weekday key: %s not in constants WEEKDAYS!' % hours['weekday'])
      continue
    for weekday in WEEKDAYS[hours['weekday']]:
      if weekday not in weekdays:
        weekdays[weekday] = hours['events']

  global operating_hours
  global today
  new_operating_hours = []
  for i in range(NUM_DAYS_STORED_IN_DB):
    new_date = today + timedelta(days=i)
    weekday = new_date.weekday()
    new_events = weekdays.get(weekday, [])
    new_operating_hour = schema.OperatingHoursType(
        date=new_date.isoformat(),
        events=parse_events(new_events, eatery_id, new_date.isoformat()),
        status='EVENTS'
    )
    new_operating_hours.append(new_operating_hour)
  operating_hours[eatery_id] = new_operating_hours
  return new_operating_hours

def format_time(start_time, end_time, start_date):
  [start_hour, start_minute] = start_time.split(':')
  [end_hour, end_minute] = end_time.split(':')
  start_hour = '0' + start_hour if len(start_hour) < 2 else start_hour
  end_hour = '0' + end_hour if len(end_hour) < 2 else end_hour
  end_date = start_date
  if (int(end_hour) < int(start_hour) or end_hour == '12') and end_minute[-2:] == 'am':
    [year, month, day] = start_date.split('-')
    next_day = date(int(year), int(month), int(day)) + timedelta(days=1)
    end_date = next_day.isoformat()
  new_start = start_date + ':' + start_hour + ':' + start_minute
  new_end = end_date + ':' + end_hour + ':' + end_minute
  return [new_start, new_end]


start_update()
