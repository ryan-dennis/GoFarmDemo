import csv
import random

with open('testdata.csv', mode='w') as file:
    fieldnames = ['Job ID', 'Crop Type', 'Price', 'Quantity', 'Location']
    writer = csv.writer(file, delimiter=',')
    crops = ['Wheat', 'Cocoa', 'Coffee', 'Corn']
    locs = ['Ghana', 'Ivory Coast', 'Guatemala', 'Panema']
    writer.writerow(['Job ID', 'Crop Type', 'Price', 'Quantity', 'Location'])
    for i in range(200):
        ind = random.randint(0, len(crops)-1)
        quantity = random.randint(10, 500)
        if crops[ind] == 'Cocoa':
            price = round(random.uniform(1.8, 1.98), 2)
        elif crops[ind] == 'Wheat':
            price = round(random.uniform(0.40, 0.50), 2)
        elif crops[ind] == 'Cofee':
            price = round(random.uniform(4.50, 4.97), 2)
        else:
            price = round(random.uniform(0.28, 0.39), 2)

        writer.writerow([i, crops[ind], price, quantity, locs[ind]])
