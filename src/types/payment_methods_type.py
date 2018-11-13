from graphene import Boolean, ObjectType

class PaymentMethodsType(ObjectType):
  brbs = Boolean(required=True)
  cash = Boolean(required=True)
  cornell_card = Boolean(required=True)
  credit = Boolean(required=True)
  mobile = Boolean(required=True)
  swipes = Boolean(required=True)
