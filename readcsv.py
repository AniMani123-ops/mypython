import csv
with open('C:/Users/anirv/mypython/test1.csv', mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        print(lines)