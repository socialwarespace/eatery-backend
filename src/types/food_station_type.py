from graphene import Boolean, Int, List, ObjectType, String

class FoodItemType(ObjectType):
  item = String(required=True)
  healthy = Boolean(required=True)
  sort_idx = Int(required=True)

class FoodStationType(ObjectType):
  category = String(required=True)
  items = List(FoodItemType, required=True)
  item_count = Int(required=True)
  sort_idx = Int(required=True)
