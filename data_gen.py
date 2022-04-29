import csv
import random

with open('testdata.csv', mode='w') as file:
    fieldnames = ['Job ID', 'Crop Type', 'Price', 'Quantity', 'Location']
    writer = csv.writer(file, delimiter=',')
    crops = ['Wheat', 'Cocoa', 'Grain', 'Corn']
    locs = ['Ghana', 'Ivory Coast', 'Guatemala', 'Panema']
    for i in range(1000):
        ind = random.randint(0, len(crops)-1)
        price = random.randint(5, 30)
        quantity = random.randint(10, 500)
        writer.writerow([i, crops[ind], price, quantity, locs[ind]])
