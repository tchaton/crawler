import csv
data = ['thomas']
with open('names.csv', "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        for line in data:
            writer.writerow(line)