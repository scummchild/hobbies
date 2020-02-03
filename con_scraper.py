"""This script scrapes the galaxycon Minneapolis site and compares the result
to a saved set of guests in a Mongodb database.  New additions and cancellations
are found"""

import argparse
import sys

from requests_html import HTMLSession

from mongo_setup import mongo_init
from condb.guest import Guest
import email_helper


def parse_script_arguments() -> argparse.Namespace:
    """Using argparse on the arguments passed into this script from the command line"""
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
    """Helper function to determine how to call send_email"""

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


def main():
    # TODO: refactor into 3 pieces: get_current_guests, get_known_guests, compare_current_to_known
    script_args = parse_script_arguments()

    session = HTMLSession()
    resp = session.get("https://galaxycon.com/minneapolis-guests/")

    people = resp.html.find('div.rt-detail')

    if not people:
        print('Unable to scrape con website')
        sys.exit()
    else:
        mongo_init(alias='core', name=script_args.db_name, host=script_args.db_host,)
        known_guest_names = [g.name for g in Guest.objects().only('name')]
        web_guest_names = []

    for person in people:
        guest_name, guest_known_for = person.text.split('\n')
        guest_url = person.find('a', first=True).attrs['href']

        web_guest_names.append(guest_name)

        if guest_name not in known_guest_names:
            new_guest = Guest(
                name=guest_name,
                known_for=guest_known_for,
                url=guest_url)

            print(f'New addition! {new_guest.name}, known for {new_guest.known_for}')

            new_guest.save()

            send_alert(
                script_args=script_args,
                name=new_guest.name,
                known_for=new_guest.known_for,
                url=new_guest.url,
                is_cancellation=False)

    cancellations = [g for g in known_guest_names if g not in web_guest_names]

    for cancelled_guest in cancellations:
        send_alert(
            script_args=script_args,
            name=cancelled_guest,
            known_for=None,
            url=None,
            is_cancellation=True)

        print(f'Oh no! {cancelled_guest} cancelled!')

        Guest.objects(name=cancelled_guest).delete()


if __name__ == '__main__':
    main()
