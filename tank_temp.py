"""This script parses a temperature reading file
on a raspberry pi, saves to a mongo db, and
then emails if the temp is too low"""

import argparse
import smtplib
import ssl
import time
import tankdb.mongo_setup as mongo_setup
from tankdb.tempreading import TempReading


def parse_script_arguments():
    """Setting up the arguments passed into this script from the command line"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'reading_location',
        help='String of the location of the temperature sensor')

    parser.add_argument(
        'device_file',
        help='Posix path to the file the temperature sensor writes to')

    return parser.parse_args()


def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, round(temp_f, 3)


def send_alert(temp):
    port = 465  # For SSL
    smtp_server = 'smtp.gmail.com'
    sender_email = 'leahnardo.the.turtle@gmail.com'
    receiver_email = 'greesha@gmail.com'
    password = input('Type your password and press enter: ')
    message = f'Subject: Alert! Turtle Tank Temp Too Low! ({temp}F)'

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def main():
    args = parse_script_arguments()

    mongo_setup.global_init()

    min_f_temp = 70

    reading = TempReading()
    reading.temp_c, reading.temp_f = read_temp(args.device_file)
    reading.reading_location = args.reading_location
    reading.save()

    if reading.temp_f < min_f_temp:
        send_alert(reading.temp_f)


if __name__ == "__main__":
    main()
