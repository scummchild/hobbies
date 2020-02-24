import argparse
import random
import pytest

from mongo_setup import mongo_init
from condb.guest import Guest
import con_scraper
import email_helper

KNOWN_FOR = 'Doctor Who'

SCRIPT_EMAIL_ARGS = argparse.Namespace(smtp_server='testserver@test.com',
                                       sender_email='testsender@test.com',
                                       sender_email_password='testpass',
                                       receiver_email='testreceive@test.com')


class GuestName():
    def __init__(self, first_name: str, last_name: str):
        self.first_name = first_name.lower()
        self.last_name = last_name.lower
        self.full_name = f'{first_name.title()} {last_name.title()}'
        self.url = f'https://galaxycon.com/{self.first_name}-{self.last_name}/'


@pytest.fixture
def setup_test_db():
    mongo_init(alias='core', name='test_galaxycon', host='10.0.0.250')

    known_guest_name = GuestName(first_name='Jon', last_name='Pertwee')
    known_guest = Guest(name=known_guest_name.full_name,
                        known_for=KNOWN_FOR,
                        url=known_guest_name.url)
    known_guest.save()

    new_guest_name = GuestName(first_name='Patrick', last_name='Troughton')

    yield (known_guest_name, new_guest_name)

    Guest.drop_collection()


def test_get_current_guests():
    current_guests = con_scraper.get_current_guests(
        'https://galaxycon.com/minneapolis-guests/')

    random_key_to_test = random.choices(list(current_guests.keys()))[0]

    assert random_key_to_test
    assert current_guests[random_key_to_test].known_for
    assert current_guests[random_key_to_test].guest_url


def test_compare_current_to_known(setup_test_db):
    known_guest, new_guest = setup_test_db

    new_guests, cancelled_guests = con_scraper.compare_current_to_known(
        {new_guest.full_name: None})

    assert new_guests == set([new_guest.full_name])
    assert cancelled_guests == set([known_guest.full_name])


def test_add_new_guests(setup_test_db, mocker):
    _, new_guest = setup_test_db

    mocker.patch('email_helper.send_email')

    con_scraper.add_new_guests(
        new_guests=set([new_guest.full_name]),
        current_guests={new_guest.full_name: con_scraper.GuestDetail(
            known_for=KNOWN_FOR, guest_url=new_guest.url)}, script_args=SCRIPT_EMAIL_ARGS)

    saved_db_guest = Guest.objects.filter(name=new_guest.full_name).first()

    assert saved_db_guest.name == new_guest.full_name

    html = f"""\
        <html>
        <body>
            <p><a href="{new_guest.url}">{new_guest.full_name}</a> is known for {KNOWN_FOR}</p>
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


def test_delete_cancelled_guests(setup_test_db, mocker):
    known_guest, _ = setup_test_db

    mocker.patch('email_helper.send_email')

    con_scraper.delete_cancelled_guests(
        cancelled_guests=set([known_guest.full_name]),
        script_args=SCRIPT_EMAIL_ARGS)

    deleted_db_guest = Guest.objects.filter(name=known_guest.full_name).first()

    assert not deleted_db_guest

    email_helper.send_email.assert_called_once_with(smtp_server='testserver@test.com',
                                                    sender_email='testsender@test.com',
                                                    sender_email_password='testpass',
                                                    receiver_email='testreceive@test.com',
                                                    message_subject='GalaxyCon cancellation: Jon Pertwee',
                                                    message_plain_text=None,
                                                    message_html=None)
