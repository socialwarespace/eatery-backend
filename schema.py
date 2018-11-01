from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import Date, Time

class Data(object):
  dining_items = {}
  eateries = {}
  events = {}
  items = {}
  menus = {}
  operating_hours = {}

  @staticmethod
  def update_data(**kwargs):
    Data.dining_items = kwargs.get('dining_items')
    Data.eateries = kwargs.get('eateries')
    Data.events = kwargs.get('events')
    Data.items = kwargs.get('items')
    Data.menus = kwargs.get('menus')
    Data.operating_hours = kwargs.get('operating_hours')

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

class Query(ObjectType):
  eateries = List(EateryType,
      eatery_id=Int(name='id'),
      date=Date(),
      eatery_name=String(name='name'),
      campus_area=String(name='area'),
      is_open=Boolean()
  )

  def resolve_eateries(self, info, eatery_id=None):
    if eatery_id is None:
      return [eatery for eatery in Data.eateries.values()]
    eatery = Data.eateries.get(eatery_id)
    return [eatery] if eatery is not None else []
