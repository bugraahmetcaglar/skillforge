import pytest
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.contact.models import Contact
from apps.contact.services import VCardImportService
from apps.user.models import User


# @pytest.mark.current
@pytest.mark.integration
@pytest.mark.django_db
class TestVCardImportServiceIntegration:
    def test_import_valid_vcard_creates_contacts(self, user: User, valid_vcard_content: str, vcard_file_factory):
        """Test importing valid vCard creates contacts in database"""
        # Arrange
        vcard_file = vcard_file_factory(valid_vcard_content)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        assert result["imported_count"] == 3
        assert result["failed_count"] == 0
        assert result["total_processed"] == 3
        assert len(result["errors"]) == 0

        # Verify contacts in database
        contacts = Contact.objects.filter(user=user)
        assert contacts.count() == 3

        # Check specific contact data
        john = contacts.filter(first_name="John").first()
        assert john is not None
        assert john.last_name == "Doe"
        assert john.mobile_phone == "+905321234567"
        assert john.email == "john.doe@example.com"
        assert john.organization == "Example Corp"  # Now should work correctly
        assert john.job_title == "Software Engineer"
        assert john.import_source == "vcard"

        # Check other contacts
        jane = contacts.filter(first_name="Jane").first()
        assert jane is not None
        assert jane.last_name == "Smith"
        assert jane.mobile_phone == "+905329876543"
        assert jane.email == "jane.smith@example.com"

        ali = contacts.filter(first_name="Ali").first()
        assert ali is not None
        assert ali.last_name == "Veli"
        assert ali.mobile_phone == "+905321112233"
        assert ali.organization == "Turkish Company"

    def test_import_with_phone_normalization(self, user: User, turkish_phone_vcard: str, vcard_file_factory):
        """Test phone number normalization during import"""
        # Arrange
        vcard_file = vcard_file_factory(turkish_phone_vcard)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        assert result["imported_count"] == 1

        contact = Contact.objects.filter(user=user).first()
        assert contact.mobile_phone == "+905321234567"  # Normalized format

    def test_import_creates_external_ids(self, user: User, valid_vcard_content: str, vcard_file_factory):
        """Test that external IDs are generated for imported contacts"""
        # Arrange
        vcard_file = vcard_file_factory(valid_vcard_content)
        service = VCardImportService(user=user)

        # Act
        service.import_from_file(vcard_file)

        # Assert
        contacts = Contact.objects.filter(user=user)
        for contact in contacts:
            assert contact.external_id is not None
            assert contact.external_id.startswith("vcard_sf_")
            assert len(contact.external_id) == 41  # "vcard_sf_" + 32 char MD5

    def test_import_duplicate_prevention(self, user: User, valid_vcard_content: str, vcard_file_factory):
        """Test that importing same vCard twice doesn't create duplicates"""
        # Arrange
        vcard_file1 = vcard_file_factory(valid_vcard_content)
        vcard_file2 = vcard_file_factory(valid_vcard_content)
        service = VCardImportService(user=user)

        # Act - Import twice
        result1 = service.import_from_file(vcard_file1)
        result2 = service.import_from_file(vcard_file2)

        # Assert - Second import should fail due to unique constraint
        assert result1["imported_count"] == 3
        assert result2["imported_count"] == 0  # All should fail due to duplicates
        assert result2["failed_count"] == 3

        # Verify only original contacts exist
        assert Contact.objects.filter(user=user).count() == 3

    def test_import_empty_contacts_skipped(self, user: User, empty_vcard_content: str, vcard_file_factory):
        """Test that empty contacts are skipped during import"""
        # Arrange
        vcard_file = vcard_file_factory(empty_vcard_content)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        assert result["imported_count"] == 0
        assert result["failed_count"] == 1  # Empty contact skipped
        assert result["total_processed"] == 1
        assert Contact.objects.filter(user=user).count() == 0

    def test_import_invalid_vcard_format(self, user: User, invalid_vcard_content: str, vcard_file_factory):
        """Test handling of invalid vCard format"""
        # Arrange
        vcard_file = vcard_file_factory(invalid_vcard_content)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        assert result["imported_count"] == 0
        assert result["failed_count"] > 0
        assert Contact.objects.filter(user=user).count() == 0

    def test_import_user_isolation(self, user: User, user_factory, valid_vcard_content: str, vcard_file_factory):
        """Test that contacts are properly isolated by user"""
        # Arrange
        other_user = user_factory()
        vcard_file1 = vcard_file_factory(valid_vcard_content)
        vcard_file2 = vcard_file_factory(valid_vcard_content)

        service1 = VCardImportService(user=user)
        service2 = VCardImportService(user=other_user)

        # Act
        result1 = service1.import_from_file(vcard_file1)
        result2 = service2.import_from_file(vcard_file2)

        # Assert
        assert result1["imported_count"] == 3
        assert result2["imported_count"] == 3

        # Verify user isolation
        user1_contacts = Contact.objects.filter(user=user)
        user2_contacts = Contact.objects.filter(user=other_user)

        assert user1_contacts.count() == 3
        assert user2_contacts.count() == 3
        assert not user1_contacts.filter(user=other_user).exists()
        assert not user2_contacts.filter(user=user).exists()

    def test_import_with_encoding_issues(self, user: User, vcard_file_factory):
        """Test handling of encoding issues in vCard files"""
        # Arrange - vCard with Turkish characters
        turkish_vcard = """BEGIN:VCARD
VERSION:3.0
FN:Ahmet Öztürk
N:Öztürk;Ahmet;;;
EMAIL:ahmet@example.com
ORG:İşletme A.Ş.
END:VCARD"""

        vcard_file = vcard_file_factory(turkish_vcard)
        service = VCardImportService(user=user)

        # Act
        result = service.import_from_file(vcard_file)

        # Assert
        assert result["imported_count"] == 1

        contact = Contact.objects.filter(user=user).first()
        assert contact.first_name == "Ahmet"
        assert contact.last_name == "Öztürk"
        assert contact.organization == "İşletme A.Ş."
