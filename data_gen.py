import csv
import random

with open('dataSupDem3.csv', mode='w') as file:
    fieldnames = ['Job ID', 'Crop Type', 'Price', 'Quantity', 'Location', 'Supply', 'Demand']
    writer = csv.writer(file, delimiter=',')
    crops = ['Wheat', 'Cacao', 'Coffee', 'Corn']
    locs = ['Ghana', 'Ivory Coast', 'Guatemala', 'Panema']
    writer.writerow(['Job ID', 'Crop Type', 'Price', 'Quantity', 'Location', 'Supply', 'Demand'])
    for i in range(200):
        cr = random.randint(0, len(crops)-1)
        loc = random.randint(0, len(locs)-1)
        quantity = random.randint(10, 500)
        if crops[cr] == 'Cacao':
            price = round(random.uniform(1.68, 1.71), 4)
        elif crops[cr] == 'Wheat':
            price = round(random.uniform(0.3979, 0.415), 4)
        elif crops[cr] == 'Coffee':
            price = round(random.uniform(4.68, 4.715), 2)
        else:
            price = round(random.uniform(0.315, 0.34), 3)
        
        sup = random.randint(50, 150)
        dem = random.randint(90, 170)

        if dem >= sup:
            ratio = round(dem/sup, 2)
            price = price + round(ratio * 0.05, 2)
        else:
            ratio = round(sup/dem, 2)
            price = price - round(ratio * 0.03, 2)
        
        if crops[cr] == 'Cacao':
            price = round(price, 4)
        elif crops[cr] == 'Wheat':
            price = round(price, 4)
        elif crops[cr] == 'Coffee':
            price = round(price, 2)
        else:
            price = round(price, 3)

        

        writer.writerow([i, crops[cr], price, quantity, locs[loc], sup, dem])

        #Cacao and wheat are by ton (multiply by 1000), Corn by the bushel (multiply by 25.4), Coffee in kg
