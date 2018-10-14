from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import Date, Time

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
    status = String(required=True) # "EVENT"
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
    coordinates = Field(CoordinatesType)
    campus_area = Field(CampusAreaType)

    def __init__(self, **kwargs):
      self.id = kwargs.get('id')
      self.slud = kwargs.get('slug')
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


class Query(ObjectType):
    eateries = List(EateryType,
        today=Date(),
        eatery_id=Int(name='id'),
        eatery_name=String(name='name'),
        campus_area=String(name='area'),
        # coordinates= Argument(CoordinatesType),
        is_open=Boolean(),
        # payment_methods= Argument(PaymentMethodsType)
    )
    operating_hours = List(
        OperatingHoursType,
        eatery_id=String(),
        date=Date()
    )

    def resolve_eateries(self, info, eatery_id=None):
      if eatery_id is None:
        return [eatery for eatery in Data.eateries.values()]
      eatery = Data.eateries.get(eatery_id)
      return [eatery] if eatery is not None else []



#Add Resolvers (will do over weekend)
