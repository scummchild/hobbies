import pytest

from mongo_setup import mongo_init
from condb.guest import Guest
import con_scraper


@pytest.fixture
def setup_test_db():
    mongo_init(alias='core', name='test_galaxycon', host='10.0.0.250')

    new_name = 'Jon Pertwee'
    new_guest = {new_name: con_scraper.GuestDetail(
        known_for='Doctor Who', guest_url='https://galaxycon.com/jon-pertwee/')}

    guest = Guest(name=new_name,
                  known_for=new_guest[new_name].known_for,
                  url=new_guest[new_name].guest_url)

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
