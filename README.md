# eatery-backend
An open-sourced backend for the Eatery application, available on Android and iOS.

Technologies involved include:
1. Flask
2. GraphQL

## Virtualenv

Virtualenv setup!

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables
It's recommended to use [`autoenv`](https://github.com/kennethreitz/autoenv).
The required environment variables for this API are the following:

````bash
export FLASK_ENV=development
````

To use `autoenv` with this repository, run the following and set the variables appropriately.

````bash
cp env.template .env
````

## Running the App

````bash
flask run
````

## GraphQL Interface

The flask app runs on your ['localhost'](http://localhost:5000/) via port 5000.
