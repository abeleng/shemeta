import csv

# Set for storing unique item values
unique_items = set()

# Read the CSV file
with open('data/crop_yield.csv', 'r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        item = row['Item']
        unique_items.add(item)

# Write unique items to a text file
with open('unique_items.txt', 'w', encoding='utf-8') as outfile:
    for item in sorted(unique_items):
        outfile.write(item + '\n')
