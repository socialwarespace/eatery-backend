from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import Date, Time
import requests
from datetime import datetime

ACCOUNT_NAMES = {
    'brbs': 'BRB Big Red Bucks',
    'citybucks': 'CB1 City Bucks',
    'laundry':  'LAU Sem Laundry',
    'cornell_card': 'CC1 Cornell Card'
    # 'swipes': ''
}

class Data(object):
  eateries = {}
  operating_hours = {}
  events = {}
  menus = {}
  items = {}

  @staticmethod
  def update_data(**kwargs):
    Data.eateries = kwargs.get('eateries')
    Data.operating_hours = kwargs.get('operating_hours')
    Data.events = kwargs.get('events')
    Data.menus = kwargs.get('menus')
    Data.items = kwargs.get('items')

class CoordinatesType(ObjectType):
  latitude = Int(required=True)
  longitude = Int(required=True)

  def __init__(self, **kwargs):
    self.latitude = kwargs.get('latitude')
    self.longitude = kwargs.get('longitude')

class CampusAreaType(ObjectType):
  description = String(required=True)
  description_short = String(required=True)

  def __init__(self, **kwargs):
    self.description = kwargs.get('description')
    self.description_short = kwargs.get('description_short')


class PaymentMethodsType(ObjectType):
  swipes = Boolean(required=True)
  brbs = Boolean(required=True)
  cash = Boolean(required=True)
  credit = Boolean(required=True)
  cornell_card = Boolean(required=True)
  mobile = Boolean(required=True)

class FoodItemType(ObjectType):
  item = String(required=True)
  healthy = Boolean(required=True)
  sort_idx = Int(required=True)

  def __init__(self, **kwargs):
    self.item = kwargs.get('item')
    self.healthy = kwargs.get('healthy')
    self.sort_idx = kwargs.get('sort_idx')

class FoodStationType(ObjectType):
  category = String(required=True)
  sort_idx = Int(required=True)
  items = List(FoodItemType, required=True)

  def __init__(self, **kwargs):
    self.category = kwargs.get('category')
    self.sort_idx = kwargs.get('sort_idx')
    self.items = kwargs.get('items')

class EventType(ObjectType):
  description = String(required=True)
  menu = List(FoodStationType, required=True)
  start_time = String(required=True)
  end_time = String(required=True)
  cal_summary = String(required=True)

  def __init__(self, **kwargs):
    self.description = kwargs.get('description')
    self.menu = kwargs.get('menu')
    self.start_time = kwargs.get('start_time')
    self.end_time = kwargs.get('end_time')
    self.cal_summary = kwargs.get('cal_summary')

class OperatingHoursType(ObjectType):
  date = String(required=True)
  status = String(required=True) # so far, we've only seen status = 'EVENT'
  events = List(EventType, required=True)

  def __init__(self, **kwargs):
    self.date = kwargs.get('date')
    self.status = kwargs.get('status')
    self.events = kwargs.get('events')

class EateryType(ObjectType):
  id = Int(required=True)
  slug = String(required=True)
  name = String(required=True)
  name_short = String(required=True)
  about = String(required=True)
  about_short = String(required=True)
  image_url = String(required=True)
  payment_methods = Field(PaymentMethodsType)
  # calendar_id = String(required=True) # for scraping
  location = String(required=True)
  operating_hours = List(OperatingHoursType, required=True)
  coordinates = Field(CoordinatesType, required=True)
  campus_area = Field(CampusAreaType, required=True)

  def __init__(self, **kwargs):
    self.id = kwargs.get('id')
    self.slug = kwargs.get('slug')
    self.name = kwargs.get('name')
    self.name_short = kwargs.get('name_short')
    self.about = kwargs.get('about')
    self.about_short = kwargs.get('about_short')
    self.image_url = kwargs.get('image_url')
    self.payment_methods = kwargs.get('payment_methods')
    self.calender_id = kwargs.get('calender_id')
    self.location = kwargs.get('location')
    self.operating_hours = kwargs.get('operating_hours')
    self.coordinates = kwargs.get('coordinates')
    self.campus_area = kwargs.get('campus_area')

class TransactionType(ObjectType):
  name = String(required=True)
  timestamp = String(required=True)

class AccountInfoType(ObjectType):
  cityBucks = String(required=True)
  laundry = String(required=True)
  brbs = String(required=True)
  swipes = String(required=True)
  history = List(TransactionType, required=True)

class Query(ObjectType):
  eateries = List(EateryType,
      eatery_id=Int(name='id'),
      date=Date(),
      eatery_name=String(name='name'),
      campus_area=String(name='area'),
      # coordinates= Argument(CoordinatesType),
      is_open=Boolean(),
      # payment_methods= Argument(PaymentMethodsType)
  )
  operating_hours = List(OperatingHoursType,
      eatery_id=Int(name='id'),
      date=Date()
  )
  account_info = Field(AccountInfoType,
      session_id=String(name='id'),
      date=Date()
  )

  def resolve_eateries(self, info, eatery_id=None):
    if eatery_id is None:
      return [eatery for eatery in Data.eateries.values()]
    eatery = Data.eateries.get(eatery_id)
    return [eatery] if eatery is not None else []

  def resolve_operating_hours(self, info, eatery_id=None):
    print(list(Data.operating_hours.values())[0][0].date)

  def resolve_account_info(self, info, session_id=None):
    if session_id is None:
      return "Provide a valid session ID!"

    account_info = {}

    # URLs to send requests to
    user_url = 'https://services.get.cbord.com/GETServices/services/json/user'
    commerce_url = 'https://services.get.cbord.com/GETServices/services/json/commerce'

    # Query 1: Get user id
    user_id = requests.post(
        user_url,
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
        commerce_url,
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
      if acct['accountDisplayName'] == ACCOUNT_NAMES['laundry']:
        account_info['laundry'] = str("{0:.2f}".format(round(acct['balance'],2)))
      if acct['accountDisplayName'] == ACCOUNT_NAMES['brbs']:
        account_info['brbs'] = str(acct['balance'])
      # Need more research to implement swipes:
      # Each plan has a different accountDisplayName
      account_info['swipes'] = ''

    # Query 3: Get list of transactions
    CORNELL_INSTITUTION_ID = '73116ae4-22ad-4c71-8ffd-11ba015407b1'
    transactions = requests.post(commerce_url,
        json={
            'method': 'retrieveTransactionHistory',
            'params': {
                'paymentSystemType': 0,
                'queryCriteria': {
                    'accountId': None,
                    'endDate': datetime.now().isoformat()[:10],
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
      date = t['actualDate'][:10]
      time = t['actualDate'][11:16]
      time = datetime.strptime(time, "%H:%M").strftime("%I:%M %p")
      new_transaction = {
          'name': t['locationName'],
          'timestamp': date + ' at ' + time
      }
      account_info['history'].append(TransactionType(**new_transaction))

    return AccountInfoType(**account_info)
