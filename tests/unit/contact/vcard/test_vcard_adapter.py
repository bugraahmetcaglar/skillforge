import pytest
import datetime

from vobject import base as vobject

from apps.contact.vcard.adapter import VCardAdapter


@pytest.mark.unit
class TestVCardAdapter:
    """Test cases for VCardAdapter"""

    def test_multiple_contacts(self, vcard_sample):
        vcards = list(vobject.readComponents(vcard_sample))
        john_vcard = vcards[0]
        jane_vcard = vcards[1]
        bugra_vcard = vcards[2]

        # Create adapter instances
        john_adapter = VCardAdapter(john_vcard)
        jane_adapter = VCardAdapter(jane_vcard)
        bugra_adapter = VCardAdapter(bugra_vcard)

        assert john_adapter.first_name == "John"
        assert john_adapter.middle_name == "Michael"
        assert john_adapter.last_name == "Doe"
        assert john_adapter.full_name == "John Michael Doe"

        assert john_adapter.emails[0]["value"] == "john.doe@example.com"
        assert john_adapter.emails[1]["value"] == "johnny@personal.com"
        assert john_adapter.primary_email == "john.doe@example.com"

        assert john_adapter.phones[0]["value"] == "0532 123 45 67"
        assert john_adapter.phones[1]["value"] == "0212 555 1234"
        assert john_adapter.phones[2]["value"] == "+90 216 444 5555"

        assert john_adapter.addresses[0]["full"] == "123 Main St, Istanbul, Marmara, 34000, Turkey"
        assert john_adapter.addresses[1]["full"] == "456 Business Ave, Ankara, Central, 06000, Turkey"
        assert john_adapter.primary_address == "123 Main St, Istanbul, Marmara, 34000, Turkey"

        assert john_adapter.organization == "Example Corporation"
        assert john_adapter.job_title == "Software Engineer"
        assert john_adapter.department == "Team Lead"

        assert john_adapter.birthday == datetime.date(1985, 3, 15)

        assert john_adapter.websites == [
            "https://johndoe.com",
            "https://linkedin.com/in/johndoe",
            "https://github.com/johndoe",
        ]
        assert john_adapter.notes == "Python"

        assert john_adapter.photo_url is None
        assert john_adapter.vcard_photo_base64 is None
        assert john_adapter.vcard_mime_type is None

        # Test Jane's properties
        assert jane_adapter.first_name == "Jane"
        assert jane_adapter.middle_name == "Elizabeth"
        assert jane_adapter.last_name == "Smith"
        assert jane_adapter.full_name == "Jane Elizabeth Smith"

        assert jane_adapter.emails[0]["value"] == "jane.smith@hospital.com"
        assert jane_adapter.primary_email == "jane.smith@hospital.com"

        assert jane_adapter.phones[0]["value"] == "05551234567"
        assert jane_adapter.phones[1]["value"] == "0312 777 8888"

        assert jane_adapter.addresses[0]["full"] == "789 Health St, Izmir, Aegean, 35000, Turkey"
        assert jane_adapter.primary_address == "789 Health St, Izmir, Aegean, 35000, Turkey"

        assert jane_adapter.organization == "City Hospital"
        assert jane_adapter.job_title == "Chief Medical Officer"
        assert jane_adapter.department == None

        assert jane_adapter.birthday == datetime.date(1980, 7, 22)

        assert jane_adapter.websites == []
        assert jane_adapter.notes == "Cardiologist and department head"

        assert jane_adapter.photo_url == None
        assert jane_adapter.vcard_photo_base64 == None
        assert jane_adapter.vcard_mime_type == None

        # Test Bugra's properties
        assert bugra_adapter.first_name == "Bugra Ahmet"
        assert bugra_adapter.middle_name == ""
        assert bugra_adapter.last_name == "Caglar"
        assert bugra_adapter.full_name == "Bugra Ahmet Caglar"

        assert bugra_adapter.emails[0]["value"] == "bugraahmetcaglar@gmail.com"
        assert bugra_adapter.primary_email == "bugraahmetcaglar@gmail.com"

        assert bugra_adapter.phones[0]["value"] == "+905323543683"

        assert bugra_adapter.addresses[0]["full"] == "Bahcelievler Mahallesi, Ankara, 06490, Turkey"
        assert bugra_adapter.primary_address == "Bahcelievler Mahallesi, Ankara, 06490, Turkey"

        assert bugra_adapter.organization == "B"
        assert bugra_adapter.job_title == "Software Engineer"
        assert bugra_adapter.department == None

        assert bugra_adapter.birthday == datetime.date(1995, 7, 4)

        assert bugra_adapter.websites == [
            "https://linkedin.com/in/bugraahmetcaglar",
            "https://github.com/bugraahmetcaglar",
        ]
        assert bugra_adapter.notes is None

        assert bugra_adapter.photo_url is None
