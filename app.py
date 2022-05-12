from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
import urllib.request
import requests
import ssl
import difflib
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
app = Flask(__name__)

post_message = ''
orders = {}
routes = {}


@app.route('/fetch_orders', methods=['POST'])
def fetch_orders():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create the container
    container_client = blob_service_client.get_container_client('user-info')

    blob_client = blob_service_client.get_blob_client(
        container='user-info', blob='data.json')

    download_file_path = os.path.join('./static', str.replace(
        'data.json', '.json', 'DOWNLOAD.json'))

    global orders
    res = blob_client.download_blob().readall()
    with open(download_file_path, 'wb') as download_file:
        download_file.write(res)
    orders = json.loads(res)
    return json.dumps(orders)


@app.route('/fetch_routes', methods=['POST'])
def fetch_routes():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create the container
    container_client = blob_service_client.get_container_client('user-info')

    blob_client = blob_service_client.get_blob_client(
        container='user-info', blob='routes.json')

    download_file_path = os.path.join('./static', 'routes.json')
    backing_path = os.path.join('./static', str.replace(
        'routes.json', '.json', 'Purchased.json'))

    global routes
    global orders
    fetch_orders()

    res = blob_client.download_blob().readall()
    with open(download_file_path, 'wb') as download_file:
        download_file.write(res)
    routes = json.loads(res)
    purchased = {"total": 800, "totalNotFiltered": 800, "rows": []}
    for row in orders['rows']:
        if row['status'] == 'Purchased':
            purchased['rows'] += [routes['rows'][row['id']]]
    with open(backing_path, 'w') as download_file:
        download_file.write(json.dumps(purchased, indent=4))
    return json.dumps(routes)


@ app.route('/')
def index():
    fetch_orders()
    return render_template('index.html')


@ app.route('/home')
def home():
    return render_template('home.html')


@ app.route('/driver')
def driver():
    fetch_routes()
    return render_template('driver.html')


def upload_orders(file='dataDOWNLOAD'):
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create the container
    container_client = blob_service_client.get_container_client('user-info')

    b = 'routes' if file == 'routes' else 'data'
    blob_client = blob_service_client.get_blob_client(
        container='user-info', blob=f'{b}.json')

    # Download the blob to a local file
    # Add 'DOWNLOAD' before the .txt extension so you can see both files in the data directory
    download_file_path = os.path.join('./static', f'{file}.json')

    with open(download_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


def get_dist(lat, lon):
    start = [-117.251829, 32.954890]  # TODO dynamic?
    key = "uKaIQorGSXWUpjBLXiN8buhKZ2wcUKnZ8hcQuLHD5OM"
    response = requests.get(
        f'https://atlas.microsoft.com/route/directions/json?subscription-key={key}&api-version=1.0&query={start[1]},{start[0]}:{lon},{lat}&travelMode=car&traffic=true&computeTravelTimeFor=all')
    dist = response.json(
    )['routes'][0]['summary']['lengthInMeters']/1000
    routes['rows'][i]['distance'] = round(dist, 3)
    routes['rows'][i]['price'] = round(round(dist, 3) * 1.75 + 2.5, 2)
    return round(dist, 3)


def init_routes():
    global routes
    fetch_routes()
    start = [-117.251829, 32.954890]  # TODO dynamic?
    key = "uKaIQorGSXWUpjBLXiN8buhKZ2wcUKnZ8hcQuLHD5OM"
    for i in range(len(routes['rows'])):
        route = routes['rows'][i]
        lat = route['coords'][0]
        lon = route['coords'][1]
        response = requests.get(
            f'https://atlas.microsoft.com/route/directions/json?subscription-key={key}&api-version=1.0&query={start[1]},{start[0]}:{lon},{lat}&travelMode=car&traffic=true&computeTravelTimeFor=all')
        dist = response.json(
        )['routes'][0]['summary']['lengthInMeters']/1000
        routes['rows'][i]['distance'] = round(dist, 3)
        routes['rows'][i]['price'] = round(round(dist, 3) * 1.75 + 2.5, 2)
    download_file_path = os.path.join('./static', 'routes.json')
    with open(download_file_path, 'w') as download_file:
        download_file.write(json.dumps(routes, indent=4))
    upload_orders('routes')
    return json.dumps({})


@ app.route('/purchase_order/<num>', methods=['POST'])
def purchase_order(num):
    account_sid = os.environ.get('TWILIO_ACCOUNT')
    auth_token = os.environ.get('TWILIO_AUTH')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to='+12155898696',
        from_='+16094453791',
        body='Your product has been purchased by a vendor. You will be notified of your pickup time when a driver is available.'
    )

    global orders
    fetch_orders()
    # order_id = request.args.get('id')
    orders['rows'][int(num)]['status'] = 'Purchased'
    download_file_path = os.path.join('./static', 'dataDOWNLOAD.json')
    with open(download_file_path, 'w') as download_file:
        download_file.write(json.dumps(orders, indent=4))
    upload_orders()
    return message.sid


@ app.route('/sms/reply', methods=['GET', 'POST'])
def create_order():
    valid_crops = ['Coffee', 'Corn', 'Wheat', 'Cacao']
    if request.method == 'POST':
        body = request.values.get('Body', None)
        resp = MessagingResponse()

        global post_message
        global orders
        global routes

        fetch_orders()
        fetch_routes()

        post_message = body
        val = body.split()

        if val == []:
            return json.dumps({'update': False, 'data': {}})
        crop = val[0].capitalize()
        if crop not in valid_crops:
            if crop == 'Cocoa':
                crop = 'Cacao'
            else:
                recommended = difflib.get_close_matches(
                    crop, valid_crops, n=1, cutoff=0.4)
                if recommended == []:
                    resp.message(
                        f'Your product {crop} could not be recognized. Please re-send your product and quantity with a valid crop name from the list: {valid_crops}')
                    return str(resp)
                else:
                    crop = recommended[0]
        price = 0
        quantity = val[1]
        jobId = len(orders['rows'])
        parsed = {"id": jobId, "crop": crop,
                  "price": price, "quantity": quantity, "status": 'Available'}
        orders['rows'] += [parsed]

        download_file_path = os.path.join('./static', 'dataDOWNLOAD.json')
        with open(download_file_path, 'w') as download_file:
            download_file.write(json.dumps(orders, indent=4))

        coords = [-106.66494, 34.11379]  # TODO dynamic
        route_dist = get_dist(coords[0], coords[1])
        new_route = {"id": jobId,
                     "destination": "Ghana",  # TODO dynamic
                     "distance": route_dist,
                     "price": round(round(route_dist, 3) * 1.75 + 2.5, 2),
                     "coords": coords}

        routes['rows'] += [new_route]

        download_file_path = os.path.join('./static', 'routes.json')
        with open(download_file_path, 'w') as download_file:
            download_file.write(json.dumps(routes, indent=4))

        upload_orders()
        upload_orders('routes')

        resp.message(
            f'Message received by GoFarm. Product {val[0]} placed on market.')

        sup = 0
        for row in orders['rows']:
            sup += int(row['quantity']) if row['crop'] == crop else 0

        dem = 2 * sup  # TODO too hard
        print(f"Sup: {sup}, Dem: {dem}")

        row = {"Job ID": jobId, "Crop Type": crop, "Price": price,
               "Quantity": quantity, "Location": "Ghana", "Supply": sup, "Demand": dem}
        call_mel(row)

        return str(resp)


# for testing
@ app.route('/call_mel', methods=['POST'])
def call_mel(row):
    data = {
        "Inputs": {
            "WebServiceInput0": [row]
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    url = 'http://20.85.207.77:80/api/v1/service/supdemmodel/score'
    # Replace this with the API key for the web service
    api_key = 'Bj3NtV5EO9NySJlmzPhQJ5kwVzyKUcd4'
    headers = {'Content-Type': 'application/json',
               'Authorization': ('Bearer ' + api_key)}

    req = urllib.request.Request(url, body, headers)
    jobId = row['Job ID']
    global orders

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        price_suggestion = json.loads(
            result)['Results']['WebServiceOutput0'][0]['Scored Labels']
        fetch_orders()
        print(price_suggestion)
        orders['rows'][jobId]['price'] = max(round(price_suggestion, 2), 0.1)
        download_file_path = os.path.join('./static', 'dataDOWNLOAD.json')
        with open(download_file_path, 'w') as download_file:
            download_file.write(json.dumps(orders, indent=4))
        upload_orders()
        return json.dumps({'success': True})
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
        return json.dumps({'success': False})


# unused
def allowSelfSignedHttps(allowed):
    # bypass the server certificate verification on client side
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context


if __name__ == '__main__':
    app.run()
    fetch_orders()
    fetch_routes()
