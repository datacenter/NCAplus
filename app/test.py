
cars = [{"name": 'porsche'}, {"name": 'ferrari'}, {"name": 'lambo'}, {"name": 'tesla'}]
ignored_cars = ['porsche', 'tesla']



for car in cars:
    if car['name'] != 'porsche' and car['name'] != 'tesla':
        print car['name']


for car in [elem for elem in cars if elem['name'] not in ignored_cars]:
    print car


new_list = [elem for elem in cars if elem['name'] not in ignored_cars]
print new_list