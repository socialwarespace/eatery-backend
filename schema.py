from constants import *
from datetime import datetime
from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import Date, Time
import requests

class Data(object):
  dining_items = {}
  eateries = {}
  events = {}
  items = {}
  menus = {}
  operating_hours = {}
  ammended_hours = {}

  @staticmethod
  def update_data(**kwargs):
    Data.dining_items = kwargs.get('dining_items')
    Data.eateries = kwargs.get('eateries')
    Data.events = kwargs.get('events')
    Data.items = kwargs.get('items')
    Data.menus = kwargs.get('menus')
    Data.operating_hours = kwargs.get('operating_hours')

  def update_hours(new_hours, eatery_id):
    Data.ammended_hours[eatery_id] = new_hours

  def get_ammended_hours():
    return ammended_hours

class CoordinatesType(ObjectType):
  latitude = Float(required=True)
  longitude = Float(required=True)

class CampusAreaType(ObjectType):
  description = String(required=True)
  description_short = String(required=True)

class PaymentMethodsType(ObjectType):
  brbs = Boolean(required=True)
  cash = Boolean(required=True)
  cornell_card = Boolean(required=True)
  credit = Boolean(required=True)
  mobile = Boolean(required=True)
  swipes = Boolean(required=True)

class DiningItemType(ObjectType):
  category = String(required=True)
  description = String(required=True)
  healthy = Boolean(required=True)
  item = String(required=True)
  show_category = Boolean(required=True)

class FoodItemType(ObjectType):
  item = String(required=True)
  healthy = Boolean(required=True)
  sort_idx = Int(required=True)

class FoodStationType(ObjectType):
  category = String(required=True)
  items = List(FoodItemType, required=True)
  item_count = Int(required=True)
  sort_idx = Int(required=True)

class EventType(ObjectType):
  cal_summary = String(required=True)
  description = String(required=True)
  end_time = String(required=True)
  menu = List(FoodStationType, required=True)
  start_time = String(required=True)
  station_count = Int(required=True)

class OperatingHoursType(ObjectType):
  date = String(required=True)
  events = List(EventType, required=True)
  status = String(required=True)  # so far, we've only seen status = 'EVENT'

class EateryType(ObjectType):
  about = String(required=True)
  about_short = String(required=True)
  campus_area = Field(CampusAreaType, required=True)
  coordinates = Field(CoordinatesType, required=True)
  dining_items = List(DiningItemType, required=True)
  eatery_type = String(required=True)
  id = Int(required=True)
  image_url = String(required=True)
  location = String(required=True)
  name = String(required=True)
  name_short = String(required=True)
  operating_hours = List(OperatingHoursType, required=True)
  payment_methods = Field(PaymentMethodsType, required=True)
  phone = String(required=True)
  slug = String(required=True)

class TransactionType(ObjectType):
  name = String(required=True)
  timestamp = String(required=True)

class AccountInfoType(ObjectType):
  brbs = String(required=True)
  cityBucks = String(required=True)
  history = List(TransactionType, required=True)
  laundry = String(required=True)
  swipes = String(required=True)

class Query(ObjectType):
  eateries = List(EateryType,
      eatery_id=Int(name='id'),
      date=Date(),
      eatery_name=String(name='name'),
      campus_area=String(name='area'),
      is_open=Boolean()
  )
  account_info = Field(AccountInfoType,
      date=Date(),
      session_id=String(name='id')
  )

  def resolve_eateries(self, info, eatery_id=None):
    if eatery_id is None:
      return [eatery for eatery in Data.eateries.values()]
    eatery = Data.eateries.get(eatery_id)
    return [eatery] if eatery is not None else []

  def resolve_account_info(self, info, session_id=None):
    if session_id is None:
      return "Provide a valid session ID!"

    account_info = {}

    # Query 1: Get user id
    user_id = requests.post(
        GET_URL + '/user',
        json={
            'version': '1',
            'method': 'retrieve',
            'params': {
                'sessionId': session_id
            }
        }
    ).json()['response']['id']

    # Query 2: Get finance info
    accounts = requests.post(
        GET_URL + '/commerce',
        json={
            'version': '1',
            'method': 'retrieveAccountsByUser',
            'params': {
                'sessionId': session_id,
                'userId': user_id
            }
        }
    ).json()['response']['accounts']

    for acct in accounts:
      if acct['accountDisplayName'] == ACCOUNT_NAMES['citybucks']:
        account_info['cityBucks'] = str(acct['balance'])
      elif acct['accountDisplayName'] == ACCOUNT_NAMES['laundry']:
        account_info['laundry'] = str("{0:.2f}".format(round(acct['balance'],2)))
      elif acct['accountDisplayName'] == ACCOUNT_NAMES['brbs']:
        account_info['brbs'] = str(acct['balance'])
      # Need more research to implement swipes:
      # Each plan has a different accountDisplayName
      account_info['swipes'] = ''

    # Query 3: Get list of transactions
    CORNELL_INSTITUTION_ID = '73116ae4-22ad-4c71-8ffd-11ba015407b1'
    transactions = requests.post(
        GET_URL + '/commerce',
        json={
            'method': 'retrieveTransactionHistory',
            'params': {
                'paymentSystemType': 0,
                'queryCriteria': {
                    'accountId': None,
                    'endDate': str(datetime.now().date()),
                    'institutionId': CORNELL_INSTITUTION_ID,
                    'maxReturn': 100,
                    'startingReturnRow': None,
                    'userId': user_id
                },
                'sessionId': session_id
            },
            'version': '1'
        }
    ).json()['response']['transactions']

    account_info['history'] = []

    for t in transactions:
      date = t['actualDate'][:10]  # YYYY-MM-DD
      time = t['actualDate'][11:16]  # HH:MM in 24-hr format
      time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")  # HH:MM in 12-hr format
      new_transaction = {
          'name': t['locationName'],
          'timestamp': date + ' at ' + time
      }
      account_info['history'].append(TransactionType(**new_transaction))

    return AccountInfoType(**account_info)

    def ammend_eatery_hours(self, info, eatery_id, new_hours):
      """
      Input format is a dict with keys as dates and values as a nested list of 2 item lists
      {
        date: [[start, end]]
      }
      Return: new operating hours (AmmendHoursType)
      """
      new_events = {}

      for date, new_times in dict.iteritems():
        new_events[date] = []
        for new_time in new_times:
          new_event = EventType(
              cal_summary='',
              description='',
              end_time=new_time[1],
              menu=[],
              start_time=new_time[0],
              station_count=0
          )
          new_events[date].append(new_event)

      new_ammended_hours = []
      for date in new_events.keys():
        new_operating_hour = OperatingHoursType(
            date=date,
            events=new_events[date],
            status='AMMEND'
        )
        new_ammended_hours.append(new_operating_hour)

      Data.update_hours(new_ammended_hours)

      return new_ammended_hours
