from graphene import Field, ObjectType, String, List, Int, Float, Boolean
from graphene.types.datetime import Date, Time

class Data(object):
  eateries = {}
  operating_hours = {}
  events = {}
  menu = {}
  items = {}

class EateryType(ObjectType):
    id = Int(required=True)
    slug = String(required=True)
    name = String(required=True)
    name_short = String(required=True)
    about = String(required=True)
    aboutshort = String(required=True)
    image_url = String(required=True)
    payment_methods = PaymentMethodsType(required=True)
    events = List(EventType, required=True)
    google_calendar_id = String(required=True) # for scraping
    location = String(required=True)
    operating_hours = List(OperatingHoursType, required=True)
    coordinates = CoordinatesType(required=True)
    campus_area = CampusAreaType(required=True)

class OperatingHoursType(ObjectType):
    date = Date(required=True)
    status = String(required=True) # "EVENT"
    events = List(EventType, required=True)

class PaymentMethodsType(ObjectType):
    swipes = Boolean(required=True)
    brbs = Boolean(required=True)
    cash = Boolean(required=True)
    credit = Boolean(required=True)

class EventType(ObjectType):
    description = String(required=True)
    menu = List(FoodStationType, required=True)
    start_time = String(required=True)
    end_time = String(required=True)
    cal_summary = String(required=True)

class FoodStationType(ObjectType):
    category = String(required=True)
    sort_idx = Int(required=True)
    items = List(FoodItemType, required=True)

class FoodItemType(ObjectType):
    item = String(required=True)
    healthy = Boolean(required=True)
    sort_idx = Int(required=True)

class CoordinatesType(ObjectType):
    latitude = Int(required=True)
    longitude = Int(required=True)

class CampusAreaType(ObjectType):
    description = String(required=True)
    description_short = String(required=True)

class Query(ObjectType):
    eateries = List(EateryType,
        today=Date(),
        eatery_id=Int(name='id'),
        eatery_name=String(name='name'),
        campus_area=String(name='area'),
        coordinates=CoordinatesType(),
        open=Boolean(),
        payment_methods=PaymentMethodType(name='pay')
    )
    operating_hours = List(OperatingHoursType,
        eatery_id=String(),
        date=Date()
    )
