"""This script parses a temperature reading file
on a raspberry pi, saves to a mongo db, and
then emails if the temp is too low"""

import argparse
import time
import tankdb.mongo_setup as mongo_setup
from tankdb.tempreading import TempReading
import email_helper


def parse_script_arguments():
    """Setting up the arguments passed into this script from the command line"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'reading_location',
        help='String of the location of the temperature sensor')

    parser.add_argument(
        'device_file',
        help='Posix path to the file the temperature sensor writes to')

    parser.add_argument(
        'smtp_server',
        help='The server for the mail service, e.g., smtp.gmail.com',
        type=str)

    parser.add_argument(
        'sender_email',
        help='The From email address',
        type=str)

    parser.add_argument(
        'sender_email_password',
        help='Password for the From email address',
        type=str)

    parser.add_argument(
        'receiver_email',
        help='The To email address',
        type=str)

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

def main():
    script_args = parse_script_arguments()

    mongo_setup.global_init()

    min_f_temp = 70

    reading = TempReading()
    reading.temp_c, reading.temp_f = read_temp(script_args.device_file)
    reading.reading_location = script_args.reading_location
    reading.save()

    if reading.temp_f < min_f_temp:
        email_helper.send_email(
            smtp_server=script_args.smtp_server,
            sender_email=script_args.sender_email,
            sender_email_password=script_args.sender_email_password,
            receiver_email=script_args.receiver_email,
            message_subject=f'Alert! Turtle Tank Temp Too Low! ({reading.temp_f}F)')


if __name__ == "__main__":
    main()
