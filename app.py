from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/purchase_order', methods=['POST'])
def purchase_order():
    print('order placed')
    return 'order'


if __name__ == '__main__':
    app.run()
