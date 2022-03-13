from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json
app = Flask(__name__)

post_message = ''


def parser(input_text):
    input_text = input_text.replace(",", " ")
    input_text = input_text.replace(";", " ")
    input_text = " ".join(input_text.split())

    sp = input_text.split()

    cocoa = sp[0]
    price = sp[1]
    quantity = sp[2]
    parsed = {"crop_type": cocoa, "price": price, "quantity": quantity}
    return json.dumps(parsed)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/purchase_order', methods=['POST'])
def purchase_order():
    account_sid = 'AC5f94bf43c9ecb15fbd7adad814de65d9'
    auth_token = '63922a3a8a6186056c6d5e46322c686f'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to='+12155898696',
        from_='+16094453791',
        body='Order placed. Driver will pickup the product tomorrow at 3:00pm.'
    )
    return message.sid


@app.route('/sms/reply', methods=['GET', 'POST'])
def create_order():
    if request.method == 'POST':
        body = request.values.get('Body', None)
        resp = MessagingResponse()

        global post_message
        post_message = body
        msg = body.split(' ')

        resp.message(
            f'Message received by GoFarm. Product {msg[0]} placed on market.')

        return str(resp)


@app.route('/add_row', methods=['POST'])
def post_order():
    print('here')
    # post_message = 'Cocoa 5 5'
    global post_message
    val = post_message.split()
    cocoa = val[0]
    price = val[1]
    quantity = val[2]
    parsed = {"crop_type": cocoa, "price": price, "quantity": quantity}
    return json.dumps(parsed)

    # if request.method == 'GET':
    #     cocoa = sp[0]
    #     price = sp[1]
    #     quantity = sp[2]
    #     parsed = {"crop_type": cocoa, "price": price, "quantity": quantity}
    #     return json.dumps(parsed)


if __name__ == '__main__':
    app.run()
