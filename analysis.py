import pandas as pd
import sys

DATEKEY = "Datum"

def count_nice_hours(rows, threshold, time_interval):
    """
    Calculate the amount of hours that have a solar temperature over a specific threshold
    It is assumed that all rows correspond with a single day and each row is measured
    in equal time differences specified by the time_interval parameter

    :rows: the data that is extracted from the UVR-1611 csv file for one day
    :threshold: a temperature threshold that tells if the solar panel is receiving energy from the sun
    :time_interval: the time between each measurement in seconds
    :return: the amount of sunny hours a day had
    """
    c = 0
    for r in rows:
        if r > threshold:
            c=c+1
    return c * time_interval / 3600


def convert_data(csv, solar_temp_key, threshold, time_interval):
    """
    Iterates through a dataframe and aggregates the rows for each day.
    The return is the amount of sunny hours for each day in a dict containing a value for each day in the dataframe

    :csv: the dataframe containing all data that should be analysed
    :solar_temp_key: the column name in the dataframe containing the relevant temperature data
    :return: a dict containing the amount of sunny hours for each day in the input data as key
    """
    ret = {}

    rowsforday = []
    currentday = ""
    for index, row in csv.iterrows():
        datum = row[DATEKEY]
        if datum != currentday:
            ret[datum] = count_nice_hours(rowsforday, threshold, time_interval)
            currentday = datum
            rowsforday = []

        rowsforday.append(float(row[solar_temp_key]))
    return ret


def write_output_csv(file, data):
    """
    Writes the sunny hours dict into a csv file
    :file: filename of the file that should be written. If the file already exists it will be overwritten
    :data: the sunny hours dict that should be written out
    """
    with open(file, "w") as f:
        f.write("Datum;Sunny Hours;\n")
        for key, value in data.items():
            f.write(key + ";" + "{:f}".format(value) + ";\n")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python3 %s <weather-data> <column-key> <output.csv> <threshold> <time-interval>" % (__file__,))
        print("- wheater-data: the csv exported by a UVR1611 control unit")
        print("- column-key: the column name of the weather data that should be used for analysis")
        print("- output.csv: a filename where the output should be written to (this file will be overwritten if it exists!)")
        print("- threshold: a temperature threshold that can be considered as the solar panel is providing energy")
        print("- time-interval: the recording interval of the UVR1611 control unit in seconds")
        sys.exit(1)

    file = sys.argv[1]
    datakey = sys.argv[2]
    outputfile = sys.argv[3]
    threshold = float(sys.argv[4])
    time_interval = int(sys.argv[5])

    csv = pd.read_csv(file, sep=";", decimal=",")
    nicehourscount = convert_data(csv, datakey, threshold, time_interval)
    write_output_csv(outputfile, nicehourscount)
