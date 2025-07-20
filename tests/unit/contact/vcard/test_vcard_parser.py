from __future__ import annotations

import pytest
from unittest.mock import patch


@pytest.mark.unit
class TestVCardParser:
    def test_split_blocks(self, parser, vcard_sample):
        """Test splitting vCard content into individual blocks"""
        blocks = parser._split_blocks(vcard_sample)

        assert len(blocks) == 5  # 5 contacts in comprehensive fixture
        assert all(block.startswith("BEGIN:VCARD") for block in blocks)
        assert all(block.endswith("END:VCARD") for block in blocks)
        assert "John Michael Doe" in blocks[0]
        assert "Jane Elizabeth Smith" in blocks[1]
        assert "Ali Mehmet Veli" in blocks[2]

    def test_extract_full_name(self, parser, vcard_sample):
        """Test extracting full name from vCard content"""
        contacts = parser.parse(vcard_sample)

        assert contacts[0]["full_name"] == "John Michael Doe"
        assert contacts[1]["full_name"] == "Jane Elizabeth Smith"
        assert contacts[2]["full_name"] == "Ali Mehmet Veli"

    def test_extract_name_components(self, parser, vcard_sample):
        """Test extracting name components from vCard"""
        contacts = parser.parse(vcard_sample)

        # Test first contact with all name components
        john = contacts[0]
        assert john["first_name"] == "John"
        assert john["last_name"] == "Doe"
        assert john["middle_name"] == "Michael"
        assert john["full_name"] == "John Michael Doe"

    def test_extract_phone_numbers(self, parser, vcard_sample):
        """Test extracting and normalizing phone numbers"""
        contacts = parser.parse(vcard_sample)

        # Test Turkish phone normalization
        john = contacts[0]
        assert john["mobile_phone"] == "+905321234567"

        # Test different formats
        ali = contacts[2]
        assert ali["mobile_phone"] == "+905321112233"

    def test_extract_email(self, parser, vcard_sample):
        """Test extracting email addresses"""
        contacts = parser.parse(vcard_sample)

        # Test email normalization (should be lowercase)
        john = contacts[0]
        assert john["email"] == "john.doe@example.com"

        jane = contacts[1]
        assert jane["email"] == "jane.smith@hospital.com"

        # Test Turkish domain
        ali = contacts[2]
        assert ali["email"] == "ali.veli@turkish-company.com.tr"

    def test_extract_organization_info(self, parser, vcard_sample):
        """Test extracting organization and job information"""
        contacts = parser.parse(vcard_sample)

        john = contacts[0]
        assert john["organization"] == "Example Corporation"
        assert john["job_title"] == "Senior Software Engineer"

        jane = contacts[1]
        assert jane["organization"] == "City Hospital"
        assert jane["job_title"] == "Chief Medical Officer"

        # Test Turkish organization
        ali = contacts[2]
        assert ali["organization"] == "Türk Şirketi A.Ş."
        assert ali["job_title"] == "Genel Müdür"

    def test_extract_birthday(self, parser, vcard_sample):
        """Test extracting birthday information"""
        contacts = parser.parse(vcard_sample)

        john = contacts[0]
        assert "birthday" in john
        assert str(john["birthday"]) == "1985-03-15"

        jane = contacts[1]
        assert str(jane["birthday"]) == "1980-07-22"

    def test_extract_notes(self, parser, vcard_sample):
        """Test extracting notes field"""
        contacts = parser.parse(vcard_sample)

        john = contacts[0]
        expected_note = (
            "Experienced software engineer specializing in Python and Django. Team lead with 10+ years experience."
        )
        assert john["notes"] == expected_note

        # Test Turkish characters in notes
        ali = contacts[2]
        assert "çığöşü" in ali["notes"]

    def test_parse_multiple_contacts(self, parser, vcard_sample):
        """Test parsing multiple contacts from single vCard file"""
        contacts = parser.parse(vcard_sample)

        # Should parse all contacts including empty ones
        assert len(contacts) >= 3  # At least 3 valid contacts

        # Verify specific contacts
        john = next(c for c in contacts if c.get("full_name") == "John Michael Doe")
        jane = next(c for c in contacts if c.get("full_name") == "Jane Elizabeth Smith")
        ali = next(c for c in contacts if c.get("full_name") == "Ali Mehmet Veli")

        assert john["email"] == "john.doe@example.com"
        assert jane["email"] == "jane.smith@hospital.com"
        assert ali["email"] == "ali.veli@turkish-company.com.tr"

    def test_parse_empty_and_minimal_contacts(self, parser, vcard_sample):
        """Test handling of empty and minimal contacts"""
        contacts = parser.parse(vcard_sample)

        # Find minimal contact
        minimal = next((c for c in contacts if c.get("full_name") == "Minimal Contact"), None)
        if minimal:
            assert minimal["email"] == "minimal@test.com"
            assert minimal.get("mobile_phone") is None or minimal.get("mobile_phone") == ""

    def test_phone_normalization_various_formats(self, parser, vcard_sample):
        """Test phone number normalization with various formats"""
        contacts = parser.parse(vcard_sample)

        # Test different phone formats in the same vCard
        john = next(c for c in contacts if c.get("full_name") == "John Michael Doe")
        ali = next(c for c in contacts if c.get("full_name") == "Ali Mehmet Veli")

        # All should be normalized to +90 format
        assert john["mobile_phone"].startswith("+90")
        assert ali["mobile_phone"].startswith("+90")

    def test_turkish_character_handling(self, parser, vcard_sample):
        """Test handling of Turkish characters"""
        contacts = parser.parse(vcard_sample)

        # Find Ali's contact with Turkish characters
        ali = next(c for c in contacts if c.get("full_name") == "Ali Mehmet Veli")

        # Should preserve Turkish characters
        assert "Türk Şirketi" in ali["organization"]
        assert "çığöşü" in ali["notes"]

    def test_parse_invalid_vcard_fallback(self, parser, invalid_vcard_sample):
        """Test manual parsing fallback for invalid vCard"""

        # Mock vobject to fail and test manual parsing
        with patch("vobject.base.readOne", side_effect=Exception("Parse error")):
            contacts = parser.parse(invalid_vcard_sample)

            assert len(contacts) == 1
            contact = contacts[0]
            assert contact["full_name"] == "Test Contact"
            assert contact["first_name"] == "Test"
            assert contact["last_name"] == "Contact"

    def test_edge_cases_and_missing_fields(self, parser, vcard_sample):
        """Test handling of missing fields and edge cases"""
        contacts = parser.parse(vcard_sample)

        # All contacts should have basic structure
        for contact in contacts:
            if contact:  # Skip empty contacts
                # Should not throw errors for missing fields
                _ = contact.get("mobile_phone", "")
                _ = contact.get("email", "")
                _ = contact.get("organization", "")
                _ = contact.get("notes", "")
