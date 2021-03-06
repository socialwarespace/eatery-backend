from flask import Flask
from flask_graphql import GraphQLView
from graphene import Schema

from src.data import start_update
from src.schema import Query

app = Flask(__name__)
schema = Schema(query=Query)
start_update()

app.add_url_rule(
    '/',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
