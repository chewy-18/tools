#!/usr/bin/python3

import sys
from dateutil.parser import parse
import argparse
from pytz import timezone
import pytz

def main():

    # Parse the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--tz", help = "Timezone to convert data into")
    parser.add_argument("-d", help = "Timezone of the data")
    parser.add_argument("-s", default=50, help = "Number of characters to show on screen")
    parser.add_argument("-f", help = "File of date times")
    args = parser.parse_args()

  if args.d:
        try: 
            original_tz = timezone(args.d)
        except:
            print("Error - for list of timezones please visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
            exit(0)
    else:
        original_tz = pytz.utc

    
    if args.tz:
        try: 
            translated_tz = timezone(args.tz)
            tz = args.tz
        except:
            print("Error - for list of timezones please visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones")
            exit(0)
    else:
        tz = "UTC"
        translated_tz = pytz.utc

    max_screen_size = args.s

    input_list = []
    if args.f:
        with open(args.f) as f:
            input_list = f.read().splitlines()
    else:
        if not sys.stdin.isatty():
            for line in sys.stdin:
                input_list.append(line)
        else:
            print("No data provided. Need to provide file or data from stdin")
            exit(0)

    hours_dict, weekday_dict = process_data(input_list, original_tz, translated_tz)

    print("------ Pattern of Life (" + tz + ") ------")
    print()
    hours_output(hours_dict, max_screen_size)
    print()
    print()
    weekday_output(weekday_dict, max_screen_size) 
    

def process_data(input_list, original_tz, translated_tz):

    # Create hours dictionary 
    hours_dict = {}
    for hours in range(24):
        hours_dict[hours] = 0

    # Create weekday dictionary 
    weekday_dict = {}
    for weekdays in range(7):
        weekday_dict[weekdays] = 0
        
    for date_time in input_list:
        # Convert datetime to right timezone
        temp_datetime = parse(date_time)

        if not temp_datetime.tzinfo:
            temp_datetime = original_tz.localize(temp_datetime)

        translated_datetime = temp_datetime.astimezone(translated_tz)

        temp_hour = translated_datetime.hour
        temp_weekday = translated_datetime.weekday()
        hours_dict[temp_hour] += 1
        weekday_dict[temp_weekday] += 1

    return hours_dict, weekday_dict

def hours_output(hours_dict, max_screen_size):
    max_hours_value = float(max(hours_dict.values()))
    for hours in range(24):
        if max_hours_value > max_screen_size:
            print(str(hours).zfill(2) + ":  |" + "∎"* int((hours_dict[hours]/max_hours_value)*max_screen_size) + " " + str(hours_dict[hours]))
        else:
            print(str(hours).zfill(2) + ":  |" + "∎"*hours_dict[hours] + " " + str(hours_dict[hours]))

def weekday_output(weekday_dict, max_screen_size):
    weekday_number_mapping = {0: "Monday:    ", 1: "Tuesday:   ", 2: "Wednesday: ", 3: "Thursday:  ", 4: "Friday:    ", 5: "Saturday:  ", 6: "Sunday:    "}
    max_weekday_value = float(max(weekday_dict.values()))
    for weekdays in range(7):
        if max_weekday_value > max_screen_size:
            print(weekday_number_mapping[weekdays] + "|" + "∎"* int((weekday_dict[weekdays]/max_weekday_value)*max_screen_size) + " " + str(weekday_dict[weekdays]))
        else:
            print(weekday_number_mapping[weekdays] + "|" + "∎"*weekday_dict[weekdays] + " " + str(weekday_dict[weekdays]))

main()
