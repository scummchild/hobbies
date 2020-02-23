import argparse
from collections import namedtuple
import pytest
from pytest_mock import mocker

from mongo_setup import mongo_init
from condb.guest import Guest
import con_scraper
import email_helper

GuestDetail = namedtuple('GuestDetail', ['known_for', 'guest_url'])


@pytest.fixture
def setup_test_db():
    mongo_init(alias='core', name='test_galaxycon', host='10.0.0.250')

    setup_name = 'Jon Pertwee'
    new_guest = {setup_name: con_scraper.GuestDetail(
        known_for='Doctor Who', guest_url='https://galaxycon.com/jon-pertwee/')}

    guest = Guest(name=setup_name,
                  known_for=new_guest[setup_name].known_for,
                  url=new_guest[setup_name].guest_url)

    guest.save()

    yield

    Guest.drop_collection()


def test_get_current_guests():
    current_guests = con_scraper.get_current_guests(
        'https://galaxycon.com/minneapolis-guests/')

    assert len(current_guests) > 0


def test_compare_current_to_known(setup_test_db):
    current_guests = {'Patrick Troughton': con_scraper.GuestDetail(
        known_for='Doctor Who', guest_url=None)}

    new_guests, cancelled_guests = con_scraper.compare_current_to_known(
        current_guests)

    assert new_guests == set(['Patrick Troughton'])
    assert cancelled_guests == set(['Jon Pertwee'])


def test_add_new_guests(setup_test_db, mocker):
    new_guest_first_name = 'patrick'
    new_guest_last_name = 'troughton'
    new_guest_full_title_name = f'{new_guest_first_name.title()} {new_guest_last_name.title()}'

    new_guests = set([new_guest_full_title_name])
    current_guests = {new_guest_full_title_name: GuestDetail(
        known_for='Doctor Who',
        guest_url=f'https://galaxycon.com/{new_guest_first_name}-{new_guest_last_name}/')}
    script_args = argparse.Namespace(smtp_server='testserver@test.com',
                                     sender_email='testsender@test.com',
                                     sender_email_password='testpass',
                                     receiver_email='testreceive@test.com')
    mocker.patch('email_helper.send_email')

    con_scraper.add_new_guests(
        new_guests=new_guests, current_guests=current_guests, script_args=script_args)

    saved_db_guest = Guest.objects.filter(name=new_guest_full_title_name).first()

    assert saved_db_guest.name == new_guest_full_title_name

    html = f"""\
        <html>
        <body>
            <p><a href="{current_guests[new_guest_full_title_name].guest_url}">\{new_guest_full_title_name}</a> is known for {current_guests[new_guest_full_title_name].known_for}</p>
        </body>
        </html>
        """

    email_helper.send_email.assert_called_once_with(smtp_server='testserver@test.com',
                                                    sender_email='testsender@test.com',
                                                    sender_email_password='testpass',
                                                    receiver_email='testreceive@test.com',
                                                    message_subject='GalaxyCon addition: Patrick Troughton',
                                                    message_plain_text='Patrick Troughton is known for Doctor Who',
                                                    message_html=html)
