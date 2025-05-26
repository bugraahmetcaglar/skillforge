from __future__ import annotations

import pytest

from apps.contact.services.vcard_service import VCardParser


@pytest.mark.current
@pytest.mark.unit
class TestVCardParser:
    """Unit tests for individual VCardParser methods"""

    @pytest.mark.parametrize(
        "encoded,expected",
        [
            # Turkish names
            ("Bu=C4=9Fra", "Buğra"),
            ("Ahmet", "Ahmet"),
            ("=C3=87a=C4=9Flar", "Çağlar"),
            ("Bu=C4=9Fra Ahmet =C3=87a=C4=9Flar", "Buğra Ahmet Çağlar"),
            # Individual Turkish characters
            ("=C3=A7", "ç"),  # ç (c with cedilla)
            ("=C3=87", "Ç"),  # Ç (C with cedilla)
            ("=C4=9F", "ğ"),  # ğ (g with breve)
            ("=C4=9E", "Ğ"),  # Ğ (G with breve)
            ("=C4=B1", "ı"),  # ı (dotless i)
            ("=C4=B0", "İ"),  # İ (I with dot)
            ("=C3=B6", "ö"),  # ö (o with diaeresis)
            ("=C3=96", "Ö"),  # Ö (O with diaeresis)
            ("=C5=9F", "ş"),  # ş (s with cedilla)
            ("=C5=9E", "Ş"),  # Ş (S with cedilla)
            ("=C3=BC", "ü"),  # ü (u with diaeresis)
            ("=C3=9C", "Ü"),  # Ü (U with diaeresis)
            # Complex Turkish names
            ("Mustafa Kemal Atat=C3=BCrk", "Mustafa Kemal Atatürk"),
            ("Mehmet =C3=96zdemir", "Mehmet Özdemir"),
            ("Ay=C5=9Fe G=C3=BCne=C5=9F", "Ayşe Güneş"),
            ("=C4=B0smail =C3=87elik", "İsmail Çelik"),
            ("G=C3=B6khan =C5=9Eahin", "Gökhan Şahin"),
            ("B=C3=BC=C5=9Fra =C4=B0=C4=9Fneci", "Büşra İğneci"),
            # Edge cases
            ("", ""),
            ("Simple Text", "Simple Text"),
            ("Bu=C4", "Bu=C4"),  # Malformed encoding
            ("=ZZ", "=ZZ"),  # Invalid hex
            ("Ahmet123=C4=9F@test.com", "Ahmet123ğ@test.com"),  # Mixed content
        ],
    )
    def test_decode_manual_method(self, vcard_parser, encoded, expected):
        """Test _decode_manual method with quoted-printable encoding"""
        result = vcard_parser._decode_manual(encoded)
        assert (
            result == expected
        ), f"Failed to decode '{encoded}' to '{expected}', got '{result}'"

    @pytest.mark.parametrize(
        "input_phone,expected",
        [
            # US formats
            ("+1-804-200-3448", "+18042003448"),
            ("+1 804 200 3448", "+18042003448"),
            ("+1 (804) 200-3448", "+18042003448"),
            ("+1-(804)-200-3448", "+18042003448"),
            ("+1.804.200.3448", "+18042003448"),
            ("1-804-200-3448", "+18042003448"),
            ("1 804 200 3448", "+18042003448"),
            ("(804) 200-3448", "+18042003448"),
            ("804-200-3448", "+18042003448"),
            ("804 200 3448", "+18042003448"),
            ("8042003448", "+18042003448"),
            ("18042003448", "+18042003448"),
            # Turkish formats
            ("+90-532-123-4567", "+905321234567"),
            ("+90 532 123 4567", "+905321234567"),
            ("+90 (532) 123-45-67", "+905321234567"),
            ("90-532-123-4567", "+905321234567"),
            ("0532-123-4567", "+905321234567"),
            ("0532 123 4567", "+905321234567"),
            ("532-123-4567", "+905321234567"),
            ("532 123 4567", "+905321234567"),
            ("5321234567", "+905321234567"),
            ("905321234567", "+905321234567"),
            # International formats
            ("+44-20-7946-0958", "+442079460958"),  # UK
            ("+33-1-42-86-83-26", "+33142868326"),  # France
            ("+49-30-12345678", "+4930123456778"),  # Germany
            # Edge cases
            ("", ""),
            ("   ", "   "),  # Only spaces
            ("abc", "abc"),  # No digits
            ("+", "+"),  # Only plus
            ("123", "+123"),  # Very short
            ("tel:+1-804-200-3448", "+18042003448"),  # URI format
            ("  +1 804 200 3448  ", "+18042003448"),  # With leading/trailing spaces
        ],
    )
    def test_normalize_phone_method(self, vcard_parser, input_phone, expected):
        """Test _normalize_phone method with various phone formats"""
        result = vcard_parser._normalize_phone(input_phone)
        assert (
            result == expected
        ), f"Failed to normalize '{input_phone}' to '{expected}', got '{result}'"

    @pytest.mark.parametrize(
        "type_param,expected",
        [
            (["CELL", "VOICE"], "CELL"),
            (["WORK", "VOICE"], "WORK"),
            (["HOME"], "HOME"),
            (["VOICE"], "VOICE"),
            ("CELL", "CELL"),
            ("WORK", "WORK"),
            ("HOME", "HOME"),
            (None, "OTHER"),
            ([], "OTHER"),
        ],
    )
    def test_get_type_method(self, vcard_parser, type_param, expected):
        """Test _get_type method for phone type detection"""

        # Mock field object
        class MockField:
            def __init__(self, type_param):
                self.type_param = type_param

        field = MockField(type_param)
        result = vcard_parser._get_type(field)
        assert result == expected

    def test_split_blocks_method(self, vcard_parser, sample_vcard_block):
        """Test _split_blocks method"""
        # Test with single vCard
        blocks = vcard_parser._split_blocks(sample_vcard_block)
        assert len(blocks) == 1
        assert blocks[0].startswith("BEGIN:VCARD")
        assert blocks[0].strip().endswith("END:VCARD")

        # Test with multiple vCards
        double_vcard = sample_vcard_block + "\n\n" + sample_vcard_block
        blocks = vcard_parser._split_blocks(double_vcard)
        assert len(blocks) == 2

    def test_parse_manual_method(self, vcard_parser, sample_vcard_block):
        """Test _parse_manual method"""
        result = vcard_parser._parse_manual(sample_vcard_block)

        assert result is not None
        assert result.get("full_name") == "Buğra Ahmet Çağlar"
        assert result.get("first_name") == "Buğra"
        assert result.get("last_name") == "Çağlar"
        assert result.get("email") == "bugra.caglar@example.com"
        assert result.get("mobile_phone") == "+905321234567"


@pytest.mark.unit
class TestVCardParserManualParsing:
    """Unit tests for individual VCardImportService methods"""

    @pytest.mark.parametrize(
        "contact_data,expected_prefix",
        [
            # Test with full_name
            ({"full_name": "Buğra Ahmet Çağlar"}, "vcard_"),
            ({"full_name": "John Doe"}, "vcard_"),
            # Test without full_name but with first/last name
            ({"first_name": "Buğra", "last_name": "Çağlar"}, "vcard_"),
            ({"first_name": "John", "last_name": "Doe"}, "vcard_"),
            # Test with only email
            ({"email": "test@example.com"}, "vcard_"),
            ({"email": "buğra@example.com"}, "vcard_"),
            # Test with only phone
            ({"mobile_phone": "+905321234567"}, "vcard_"),
            # Test with empty data
            ({}, "vcard_"),
        ],
    )
    def test_generate_external_id_method(
        self, vcard_import_service, contact_data, expected_prefix
    ):
        """Test _generate_external_id method with various contact data"""
        result = vcard_import_service._generate_external_id(contact_data)
        assert result.startswith(expected_prefix)
        assert len(result) == 38  # "vcard_" + 32 char MD5 hash

        # Test that same input produces same output (deterministic)
        result2 = vcard_import_service._generate_external_id(contact_data)
        assert result == result2
