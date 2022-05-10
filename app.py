from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
import os
import urllib.request
import ssl
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
app = Flask(__name__)

post_message = ''
orders = {}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/driver')
def driver():
    return render_template('driver.html')


@app.route('/fetch_orders', methods=['POST'])
def fetch_orders():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create the container
    container_client = blob_service_client.get_container_client('user-info')

    # Create new Container
    # container_client.create_container()

    # print("\nListing blobs...")

    # List the blobs in the container
    # blob_list = container_client.list_blobs()
    # for blob in blob_list:
    #     print("\t" + blob.name)

    blob_client = blob_service_client.get_blob_client(
        container='user-info', blob='data.json')

    # Download the blob to a local file
    # Add 'DOWNLOAD' before the .txt extension so you can see both files in the data directory
    download_file_path = os.path.join('./static', str.replace(
        'data.json', '.json', 'DOWNLOAD.json'))
    # print("\nDownloading blob to \n\t" + download_file_path)

    # store in mem? on init? update on text msg, and then write to blob?
    global orders
    res = blob_client.download_blob().readall()
    with open(download_file_path, 'wb') as download_file:
        download_file.write(res)
    orders = json.loads(res)
    return json.dumps(orders)


def add_order():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create the container
    container_client = blob_service_client.get_container_client('user-info')

    blob_client = blob_service_client.get_blob_client(
        container='user-info', blob='data.json')

    # Download the blob to a local file
    # Add 'DOWNLOAD' before the .txt extension so you can see both files in the data directory
    download_file_path = os.path.join('./static', 'dataDOWNLOAD.json')

    with open(download_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


@ app.route('/purchase_order', methods=['POST'])
def purchase_order():
    account_sid = os.environ.get('TWILIO_ACCOUNT')
    auth_token = os.environ.get('TWILIO_AUTH')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to='+12155898696',
        from_='+16094453791',
        body='Order placed. Driver will pickup the product tomorrow at 3:00pm.'
    )
    return message.sid


@ app.route('/sms/reply', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        body = request.values.get('Body', None)
        resp = MessagingResponse()

        global post_message
        global orders
        post_message = body
        val = body.split()

        if val == []:
            return json.dumps({'update': False, 'data': {}})
        crop = val[0]
        price = val[1]
        quantity = val[2]
        parsed = {"id": len(orders['rows']), "crop": crop,
                  "price": price, "quantity": quantity}
        orders['rows'] += [parsed]

        with open(download_file_path, 'w') as download_file:
            download_file.write(json.dumps(orders, indent=4))

        add_order()

        resp.message(
            f'Message received by GoFarm. Product {val[0]} placed on market.')

        return str(resp)


# deprecated
@ app.route('/add_row', methods=['POST'])
def post_order():
    # format of post_message = 'Cocoa 5 5'
    global post_message
    global orders
    val = post_message.split()
    if val == []:
        return json.dumps({'update': False, 'data': {}})
    cocoa = val[0]
    price = val[1]
    quantity = val[2]
    parsed = {"id": len(orders['rows']), "crop": cocoa,
              "price": price, "quantity": quantity}
    orders['rows'] += [parsed]
    return json.dumps({'update': True, 'data': parsed})


# for testing
@ app.route('/call_mel', methods=['POST'])
def call_mel():
    data = {
        "Inputs": {
            "WebServiceInput0": [
                {
                    "Job ID": 0,
                    "Crop Type": "Wheat",
                    "Price": 0.45,
                    "Quantity": 33,
                    "Location": "Ghana"
                },
                {
                    "Job ID": 1,
                    "Crop Type": "Cocoa",
                    "Price": 1.86,
                    "Quantity": 497,
                    "Location": "Ivory Coast"
                },
                {
                    "Job ID": 2,
                    "Crop Type": "Corn",
                    "Price": 0.33,
                    "Quantity": 459,
                    "Location": "Panema"
                },
                {
                    "Job ID": 3,
                    "Crop Type": "Cocoa",
                    "Price": 1.92,
                    "Quantity": 401,
                    "Location": "Ivory Coast"
                },
                {
                    "Job ID": 4,
                    "Crop Type": "Cocoa",
                    "Price": 1.95,
                    "Quantity": 489,
                    "Location": "Ivory Coast"
                }
            ]
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    url = 'http://20.85.207.77:80/api/v1/service/modelpredict/score'
    # Replace this with the API key for the web service
    api_key = 'X6Up7Q4LSDhUqUv0lOH2dIpHb0jLh5tG'
    headers = {'Content-Type': 'application/json',
               'Authorization': ('Bearer ' + api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        print(result)
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
