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
        ali_vcard = vcards[2]

        # Create adapter instances
        john_adapter = VCardAdapter(john_vcard)
        jane_adapter = VCardAdapter(jane_vcard)
        ali_adapter = VCardAdapter(ali_vcard)

        assert john_adapter.first_name == "John"
        assert john_adapter.middle_name == "Michael"
        assert john_adapter.last_name == "Doe"
        assert john_adapter.full_name == "John Michael Doe"
        assert john_adapter.nickname == "Johnny"
        assert john_adapter.email == "john.doe@example.com"
        assert john_adapter.emails[0]["value"] == "john.doe@example.com"
        assert john_adapter.emails[1]["value"] == "johnny@personal.com"
        assert john_adapter.primary_email == "john.doe@example.com"
        assert john_adapter.phones[0]["value"] == "0532 123 45 67"
        assert john_adapter.phones[1]["value"] == "0212 555 1234"
        assert john_adapter.phones[2]["value"] == "+90 216 444 5555"
        assert john_adapter.mobile_phone == "0532 123 45 67"
        assert john_adapter.addresses[0]["full"] == "123 Main St, Istanbul, Marmara, 34000, Turkey"
        assert john_adapter.addresses[1]["full"] == "456 Business Ave, Ankara, Central, 06000, Turkey"
        assert john_adapter.primary_address == "123 Main St, Istanbul, Marmara, 34000, Turkey"
        assert john_adapter.organization == "Example Corporation"
        assert john_adapter.job_title == "Senior Software Engineer"
        assert john_adapter.department == "Team Lead"
        assert john_adapter.birthday == datetime.date(1985, 3, 15)
        assert john_adapter.anniversary == datetime.date(2010, 6, 20)
        assert john_adapter.urls == "https://johndoe.com"
        assert john_adapter.photo_url == "https://example.com/photos/john.jpg"
        # assert john_adapter.social_profiles == {"linkedin": "https://linkedin.com/in/johndoe"}
        assert john_adapter.notes == "Experienced software engineer specializing in Python and Django. Team lead with 10+ years experience."

        # Test Jane's properties
        assert jane_adapter.first_name == "Jane"
        assert jane_adapter.middle_name == "Elizabeth"
        assert jane_adapter.last_name == "Smith"
        assert jane_adapter.full_name == "Jane Elizabeth Smith"
        assert jane_adapter.nickname == None
        assert jane_adapter.email == "jane.smith@hospital.com"
        assert jane_adapter.emails[0]["value"] == "jane.smith@hospital.com"
        assert jane_adapter.primary_email == "jane.smith@hospital.com"
        assert jane_adapter.phones[0]["value"] == "05551234567"
        assert jane_adapter.phones[1]["value"] == "0312 777 8888"
        assert jane_adapter.mobile_phone == "05551234567"
        assert jane_adapter.addresses[0]["full"] == "789 Health St, Izmir, Aegean, 35000, Turkey"
        assert jane_adapter.primary_address == "789 Health St, Izmir, Aegean, 35000, Turkey"
        assert jane_adapter.organization == "City Hospital"
        assert jane_adapter.job_title == "Chief Medical Officer"
        assert jane_adapter.department == None
        assert jane_adapter.birthday == datetime.date(1980, 7, 22)
        assert jane_adapter.anniversary == None
        assert jane_adapter.urls == []
        assert jane_adapter.photo_url == None
        # assert jane_adapter.social_profiles == {"linkedin": "https://linkedin.com/in/janesmith"}
        assert jane_adapter.notes == "Cardiologist and department head"
        
        # Test Ali's properties
        assert ali_adapter.first_name == "Ali"
        assert ali_adapter.middle_name == "Mehmet"
        assert ali_adapter.last_name == "Veli"
        assert ali_adapter.full_name == "Ali Mehmet Veli"
        assert ali_adapter.nickname is None
        assert ali_adapter.email == "ali.veli@turkish-company.com.tr"
        assert ali_adapter.emails[0]["value"] == "ali.veli@turkish-company.com.tr"
        assert ali_adapter.primary_email == "ali.veli@turkish-company.com.tr"
        assert ali_adapter.phones[0]["value"] == "532 111 22 33"
        assert ali_adapter.phones[1]["value"] == "0216 333 4444"
        assert ali_adapter.mobile_phone == "532 111 22 33"
        assert ali_adapter.addresses == []
        assert ali_adapter.primary_address == None
        assert ali_adapter.organization == "Türk Şirketi A.Ş."
        assert ali_adapter.job_title == "Genel Müdür"
        assert ali_adapter.department == None
        assert ali_adapter.birthday == datetime.date(1975, 12, 5)
        assert ali_adapter.anniversary == None
        assert ali_adapter.urls == []
        assert ali_adapter.photo_url == None
        # assert ali_adapter.social_profiles == {}
        assert ali_adapter.notes == "Turkish company executive with special characters: çığöşü"
        