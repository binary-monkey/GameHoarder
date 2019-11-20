import csv

from GameHoarder.settings import BASE_DIR


def read_csv(file):
    file_url = BASE_DIR + file

    csv_file = open(file_url)

    return list(csv.reader(csv_file, delimiter=','))
