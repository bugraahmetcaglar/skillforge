# tests/integration/contact/test_vcard_import_service.py
import pytest
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from apps.contact.models import Contact
from apps.contact.vcard.services import VCardImportService
from apps.user.models import User


@pytest.mark.integration
@pytest.mark.django_db
class TestVCardImportServiceIntegration:

    def test_import_from_file_vcard_sample_creates_all_contacts(
        self, user: User, vcard_sample: str, vcard_file_factory
    ):
        """Test importing comprehensive vCard creates all contacts with correct data"""

        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        breakpoint()
        assert result["imported_count"] == 5
        assert result["failed_count"] == 0
        assert result["total_processed"] == 5
        assert result["errors"] == []

        # Verify contacts in database
        contacts = Contact.objects.filter(user=user, is_active=True)
        assert contacts.count() == 5

        # Check John's contact (most complete)
        john = contacts.filter(first_name="John", last_name="Doe").first()
        assert john.first_name == "John"
        assert john.middle_name == "Michael"
        assert john.last_name == "Doe"
        assert john.full_name == "John Michael Doe"
        assert john.nickname == "Johnny"
        assert john.email == "john.doe@example.com"
        assert john.emails == []
        assert john.phones == []
        assert john.mobile_phone == "+905321234567"
        assert john.home_phone == "+902123456789"
        assert john.work_phone == "+905321234567"
        assert john.second_phone == "+905321234567"
        assert john.third_phone == "+905321234567"
        assert john.addresses == [
            {"label": "Home", "address": "123 Main St, City, Country"},
            {"label": "Work", "address": "456 Work Ave, City, Country"},
        ]
        assert john.organization == "Example Corporation"
        assert john.job_title == "Senior Software Engineer"
        assert john.department == "Engineering"
        assert john.birthday == "1985-03-15"
        assert john.anniversary == "2010-06-20"
        assert john.websites == ["https://johndoe.com", "https://linkedin.com/in/johndoe"]
        assert john.social_profiles == {
            "linkedin": "https://linkedin.com/in/johndoe",
            "twitter": "https://twitter.com/johndoe",
        }
        assert john.notes == "Python and Django enthusiast\nTeam lead for project X"
        assert john.import_source == "vcard"
        assert john.external_id.startswith("vcard_sf_")
        assert "Python and Django" in john.notes

        # Check Jane's contact
        jane = contacts.filter(first_name="Jane", last_name="Smith").first()
        assert jane.first_name == "Jane"
        assert jane.middle_name == "Elizabeth"
        assert jane.last_name == "Smith"
        assert jane.email == "jane.smith@hospital.com"
        assert jane.organization == "City Hospital"
        assert jane.job_title == "Chief Medical Officer"
        assert jane.birthday == "1980-07-22"
        assert jane.mobile_phone == "+905551234567"
        assert jane.work_phone == "+903127778888"
        assert jane.addresses == [{"label": "Work", "address": "789 Health St, Izmir, Aegean, 35000, Turkey"}]
        assert jane.notes == "Cardiologist and department head"

        assert jane.email == "jane.smith@hospital.com"
        assert jane.emails == ["jane.smith@hospital.com"]
        assert jane.phones == ["+905551234567"]
        assert jane.mobile_phone == "+905551234567"
        assert jane.home_phone == "+902123456789"
        assert jane.work_phone == "+905551234567"
        assert jane.second_phone == "+905551234567"
        assert jane.third_phone == "+905551234567"
        assert jane.addresses == [
            {"label": "Home", "address": "123 Main St, City, Country"},
            {"label": "Work", "address": "456 Work Ave, City, Country"},
        ]
        assert jane.organization == "City Hospital"
        assert jane.job_title == "Chief Medical Officer"
        assert jane.department == "Cardiology"
        assert jane.birthday == "1980-07-22"
        assert jane.anniversary == "2010-06-20"
        assert jane.websites == ["https://janesmith.com", "https://linkedin.com/in/janesmith"]
        assert jane.social_profiles == {
            "linkedin": "https://linkedin.com/in/janesmith",
            "twitter": "https://twitter.com/janesmith",
        }
        assert jane.notes == "Cardiologist and department head"
        assert jane.import_source == "vcard"
        assert jane.external_id.startswith("vcard_sf_")
        assert "Cardiologist" in jane.notes

        # Check Ali's contact
        ali = contacts.filter(first_name="Ali", last_name="Veli").first()
        assert ali.first_name == "Ali"
        assert ali.middle_name == "Mehmet"
        assert ali.last_name == "Veli"
        assert ali.email == "ali.veli@company.com"
        assert ali.organization == "Tech Corp"
        assert ali.job_title == "Software Engineer"
        assert ali.birthday == "1990-01-01"
        assert ali.mobile_phone == "+905551234567"
        assert ali.work_phone == "+903127778888"
        assert ali.addresses == [{"label": "Work", "address": "123 Tech St, Istanbul, Marmara, 34000, Turkey"}]
        assert ali.notes == "Software Engineer at Tech Corp with special characters: çığöşü"

        assert ali.email == "ali.veli@company.com"
        assert ali.emails == ["ali.veli@company.com"]
        assert ali.phones == ["+905551234567"]
        assert ali.mobile_phone == "+905551234567"
        assert ali.home_phone == "+902123456789"
        assert ali.work_phone == "+905551234567"
        assert ali.second_phone == "+905551234567"
        assert ali.third_phone == "+905551234567"
        assert ali.addresses == [
            {"label": "Home", "address": "123 Main St, City, Country"},
            {"label": "Work", "address": "456 Work Ave, City, Country"},
        ]
        assert ali.organization == "Tech Corp"
        assert ali.job_title == "Software Engineer"
        assert ali.department == "Engineering"
        assert ali.birthday == "1990-01-01"
        assert ali.anniversary == "2015-05-15"
        assert ali.websites == ["https://aliveli.com", "https://linkedin.com/in/aliveli"]
        assert ali.social_profiles == {
            "linkedin": "https://linkedin.com/in/aliveli",
            "twitter": "https://twitter.com/aliveli",
        }
        assert ali.notes == "Software Engineer at Tech Corp with special characters: çığöşü"
        assert ali.import_source == "vcard"
        assert ali.external_id.startswith("vcard_sf_")
        assert "Software Engineer" in ali.notes

    def test_import_phone_number_normalization(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test phone number normalization during import"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        contacts = Contact.objects.filter(user=user, is_active=True)

        # All phone numbers should be normalized to +90 format
        for contact in contacts:
            if contact.mobile_phone:
                assert contact.mobile_phone.startswith("+90"), f"Phone not normalized: {contact.mobile_phone}"

    def test_import_creates_external_ids(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test that external IDs are generated for all imported contacts"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        contacts = Contact.objects.filter(user=user, is_active=True)
        for contact in contacts:
            assert contact.external_id is not None
            assert contact.external_id.startswith("vcard_sf_")
            assert len(contact.external_id) == 41  # "vcard_sf_" + 32 char MD5

    def test_import_duplicate_prevention(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test that importing same vCard twice doesn't create duplicates"""
        # Arrange
        vcard_file1 = vcard_file_factory(vcard_sample)
        vcard_file2 = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act - Import twice
        result1 = service.import_from_file(vcard_file1)
        result2 = service.import_from_file(vcard_file2)

        # Assert - Second import should fail due to unique constraint
        assert result1["imported_count"] >= 3
        assert result2["imported_count"] == 0  # All should fail due to duplicates
        assert result2["failed_count"] >= 3

        # Verify only original contacts exist
        contacts_count = Contact.objects.filter(user=user, is_active=True).count()
        assert contacts_count == result1["imported_count"]

    def test_import_empty_contacts_handling(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test that empty contacts are handled gracefully"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert - Empty contacts should be counted as failed
        total_contacts_in_file = vcard_sample.count("BEGIN:VCARD")
        assert result["total_processed"] == total_contacts_in_file
        assert result["imported_count"] + result["failed_count"] == total_contacts_in_file

    def test_import_user_isolation(self, user: User, user_factory, vcard_sample: str, vcard_file_factory):
        """Test that contacts are properly isolated by user"""
        # Arrange
        other_user = user_factory()
        vcard_file1 = vcard_file_factory(vcard_sample)
        vcard_file2 = vcard_file_factory(vcard_sample)

        service1 = VCardImportService(user=user)
        service2 = VCardImportService(user=other_user)

        # Act
        result1 = service1.import_from_file(vcard_file1)
        result2 = service2.import_from_file(vcard_file2)

        # Assert
        assert result1["imported_count"] >= 3
        assert result2["imported_count"] >= 3

        # Verify user isolation
        user1_contacts = Contact.objects.filter(user=user, is_active=True)
        user2_contacts = Contact.objects.filter(user=other_user, is_active=True)

        assert user1_contacts.count() == result1["imported_count"]
        assert user2_contacts.count() == result2["imported_count"]
        assert not user1_contacts.filter(user=other_user).exists()
        assert not user2_contacts.filter(user=user).exists()

    def test_import_birthday_parsing(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test birthday field parsing and storage"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        john = Contact.objects.filter(user=user, first_name="John", last_name="Doe").first()
        jane = Contact.objects.filter(user=user, first_name="Jane", last_name="Smith").first()
        ali = Contact.objects.filter(user=user, first_name="Ali", last_name="Veli").first()

        assert john.birthday is not None
        assert str(john.birthday) == "1985-03-15"

        assert jane.birthday is not None
        assert str(jane.birthday) == "1980-07-22"

        assert ali.birthday is not None
        assert str(ali.birthday) == "1975-12-05"

    def test_import_notes_and_special_characters(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test notes field and Turkish character handling"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        john = Contact.objects.filter(user=user, first_name="John").first()
        ali = Contact.objects.filter(user=user, first_name="Ali").first()

        # Check notes content
        assert "Python and Django" in john.notes
        assert "Team lead" in john.notes

        # Check Turkish characters preserved
        assert "çığöşü" in ali.notes
        assert "Türk Şirketi" in ali.organization

    def test_import_multiple_emails_and_phones(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test handling of multiple emails and phone numbers"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        john = Contact.objects.filter(user=user, first_name="John").first()

        # Should have primary email and phone
        assert john.email == "john.doe@example.com"  # Work email should be primary
        assert john.mobile_phone == "+905321234567"

    def test_import_encoding_handling(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test UTF-8 encoding handling for Turkish content"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert - Should not fail on Turkish characters
        assert result["imported_count"] >= 3

        ali = Contact.objects.filter(user=user, first_name="Ali").first()
        assert "Türk" in ali.organization
        assert "Müdür" in ali.job_title

    def test_import_invalid_file_encoding_error(self, user: User, vcard_file_factory):
        """Test handling of invalid file encoding"""
        # Arrange - Create invalid encoding file
        invalid_content = b"\xff\xfe\x00\x00"  # Invalid UTF-8
        vcard_file = SimpleUploadedFile("invalid.vcf", invalid_content, content_type="text/vcard")
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert - Should handle encoding error gracefully
        assert result == {} or result.get("imported_count", 0) == 0

    def test_import_service_with_invalid_user(self, vcard_sample: str, vcard_file_factory):
        """Test service behavior with invalid user"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=None)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert - Should handle gracefully but fail to save
        assert result.get("imported_count", 0) == 0
        assert result.get("failed_count", 0) >= 0

    def test_import_fallback_to_manual_parsing(self, user: User, vcard_file_factory):
        """Test fallback to manual parsing when vobject fails"""
        # Arrange - Create vCard that might cause vobject to fail
        problematic_vcard = """BEGIN:VCARD
FN:Test Contact
N:Contact;Test;;;
TEL:+905321234567
EMAIL:test@example.com
ORG:Test Company
END:VCARD"""

        vcard_file = vcard_file_factory(problematic_vcard)
        service = VCardImportService(user=user)

        # Act - Mock vobject to fail
        with patch("vobject.base.readOne", side_effect=Exception("Parse error")):
            result = service.import_from_file(vcard_file)

        # Assert - Should still import via manual parsing
        assert result["imported_count"] == 1

        contact = Contact.objects.filter(user=user, is_active=True).first()
        assert contact.full_name == "Test Contact"
        assert contact.first_name == "Test"
        assert contact.last_name == "Contact"
        assert contact.mobile_phone == "+905321234567"
        assert contact.email == "test@example.com"

    def test_import_result_structure(self, user: User, vcard_sample: str, vcard_file_factory):
        """Test that import result has correct structure"""
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert - Result structure
        assert "imported_count" in result
        assert "failed_count" in result
        assert "total_processed" in result
        assert "errors" in result

        assert isinstance(result["imported_count"], int)
        assert isinstance(result["failed_count"], int)
        assert isinstance(result["total_processed"], int)
        assert isinstance(result["errors"], list)

        # Counts should add up
        assert result["imported_count"] + result["failed_count"] == result["total_processed"]
