"""This script scrapes the galaxycon Minneapolis site and compares the result
to a saved set of guests in a Mongodb database.  New additions and cancellations
are found"""

import smtplib
import ssl
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from requests_html import HTMLSession

import condb.mongo_setup as mongo_setup
from condb.guest import Guest


def send_alert(name, known_for, url, is_cancellation):
    """Helper function to send email"""
    port = 465  # For SSL
    smtp_server = 'smtp.gmail.com'
    sender_email = 'leahnardo.the.turtle@gmail.com'
    receiver_email = 'greesha@gmail.com'
    password = input('Type your password and press enter: ')

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email

    if not is_cancellation:
        message["Subject"] = f'GalaxyCon addition: {name}'
        text = f'{name} is known for {known_for}'

        html = f"""\
        <html>
        <body>
            <p><a href="{url}">{name}</a> is known for {known_for}</p>
        </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)
    else:
        message["Subject"] = f'GalaxyCon cancellation: {name}'

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def main():
    session = HTMLSession()
    resp = session.get("https://galaxycon.com/minneapolis-guests/")

    people = resp.html.find('div.rt-detail')

    if not people:
        print('Unable to scrape con website')
        sys.exit()
    else:
        mongo_setup.global_init()
        known_guest_names = [g.name for g in Guest.objects().only('name')]
        web_guest_names = []

    for person in people:
        guest_name, guest_known_for = person.text.split('\n')
        guest_url = person.find('a', first=True).attrs['href']

        web_guest_names.append(guest_name)

        if guest_name not in known_guest_names:
            new_guest = Guest()
            new_guest.name = guest_name
            new_guest.known_for = guest_known_for
            new_guest.url = guest_url

            print(f'New addition! {new_guest.name}, known for {new_guest.known_for}')

            new_guest.save()

            send_alert(name=new_guest.name, known_for=new_guest.known_for,
                    url=new_guest.url, is_cancellation=False)

    cancellations = [g for g in known_guest_names if g not in web_guest_names]

    for cancelled_guest in cancellations:
        send_alert(name=cancelled_guest, known_for=None,
                url=None, is_cancellation=True)

        print(f'Oh no! {cancelled_guest} cancelled!')

        Guest.objects(name=cancelled_guest).delete()

if __name__ == '__main__':
    main()