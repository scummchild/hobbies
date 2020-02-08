"""This script scrapes the galaxycon Minneapolis site and compares the result
to a saved set of guests in a MongoDB database.  New additions and cancellations
modify the database and send an email"""

import argparse
from collections import namedtuple

from requests_html import HTMLSession

from mongo_setup import mongo_init
from condb.guest import Guest
import email_helper


GuestDetail = namedtuple('GuestDetail', ['known_for', 'guest_url'])


def parse_script_arguments() -> argparse.Namespace:
    """Use argparse on the arguments passed into this script from the command line"""
    parser = argparse.ArgumentParser(
        description='This script scrapes the galaxycon Minneapolis site and compares \
            the result to a saved set of guests in a Mongodb database. \
            New additions and cancellations are found',
        fromfile_prefix_chars='@')

    parser.add_argument(
        'db_host',
        help='The host name / ip address for the con database server',
        type=str)

    parser.add_argument(
        'db_name',
        help='The name of the con database',
        type=str)

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


def send_alert(
        script_args: argparse.Namespace,
        name: str,
        known_for: str,
        url: str,
        is_cancellation: bool):
    """Call send_email one way for new guests, another way for cancellations"""

    if not is_cancellation:
        subject = f'GalaxyCon addition: {name}'
        text = f'{name} is known for {known_for}'
        html = f"""\
        <html>
        <body>
            <p><a href="{url}">{name}</a> is known for {known_for}</p>
        </body>
        </html>
        """

    else:
        subject = f'GalaxyCon cancellation: {name}'
        text = None
        html = None

    email_helper.send_email(
        smtp_server=script_args.smtp_server,
        sender_email=script_args.sender_email,
        sender_email_password=script_args.sender_email_password,
        receiver_email=script_args.receiver_email,
        message_subject=subject,
        message_plain_text=text,
        message_html=html)


def get_current_guests(con_url: str) -> dict:
    """Parse con url and return dict of guests currently on the site"""
    current_guests = {}

    session = HTMLSession()
    resp = session.get(con_url)
    guest_details = resp.html.find('div.rt-detail')

    for guest_detail in guest_details:
        name, known_for = guest_detail.text.split('\n')
        guest_url = guest_detail.find('a', first=True).attrs['href']

        current_guests[name] = GuestDetail(
            known_for=known_for, guest_url=guest_url)

    return current_guests


def compare_current_to_known(current_guests: dict) -> tuple:
    """Helper function to determine how to call send_email"""

    known_guests = set(g.name for g in Guest.objects().only('name'))

    new_guests = set(current_guests.keys()).difference(known_guests)

    cancelled_guests = known_guests.difference(current_guests.keys())

    return (new_guests, cancelled_guests)


def add_new_guests(new_guests: set, current_guests: dict, script_args: argparse.Namespace):
    """Save new guests to the database and call send_alert appropriately"""
    for new_guest in new_guests:
        guest = Guest(
            name=new_guest,
            known_for=current_guests[new_guest].known_for,
            url=current_guests[new_guest].guest_url)

        guest.save()

        print(f'New addition! {guest.name}, known for {guest.known_for}')

        send_alert(
            script_args=script_args,
            name=guest.name,
            known_for=guest.known_for,
            url=guest.url,
            is_cancellation=False)


def delete_cancelled_guests(cancelled_guests: set, script_args: argparse.Namespace):
    """Delete cancelled guests from the database and call send_alert appropriately"""
    for cancelled_guest in cancelled_guests:
        Guest.objects(name=cancelled_guest).delete()

        print(f'Oh no! {cancelled_guest} cancelled!')

        send_alert(
            script_args=script_args,
            name=cancelled_guest,
            known_for=None,
            url=None,
            is_cancellation=True)


def main():
    """Driving function when called from command line"""
    script_args = parse_script_arguments()

    current_guests = get_current_guests(
        con_url='https://galaxycon.com/minneapolis-guests/')

    assert current_guests

    mongo_init(alias='core', name=script_args.db_name, host=script_args.db_host)

    new_guests, cancelled_guests = compare_current_to_known(
        current_guests)

    add_new_guests(new_guests, current_guests, script_args)

    delete_cancelled_guests(cancelled_guests, script_args)


if __name__ == '__main__':
    main()
