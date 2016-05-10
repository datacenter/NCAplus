
cars = [{ "name": 'porsche'}, {"name": 'ferrari'}, {"name": 'lambo'}, {"name": 'tesla'}]



ignored_cars = ['porsche', 'tesla']


for car in [cars if car in cars]:
    print car