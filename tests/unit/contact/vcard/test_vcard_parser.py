from __future__ import annotations

import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.current
@pytest.mark.unit
class TestVCardParser:
    def test_split_blocks(self, parser, sample_vcard_content):
        """Test splitting vCard content into individual blocks"""
        blocks = parser._split_blocks(sample_vcard_content)

        assert len(blocks) == 2
        assert blocks[0].startswith("BEGIN:VCARD")
        assert blocks[0].endswith("END:VCARD")
        assert "John Doe" in blocks[0]
        assert "Jane Smith" in blocks[1]

    def test_extract_full_name(self, parser):
        """Test extracting full name from vCard"""
        mock_vcard = MagicMock()
        mock_vcard.fn.value = "John Doe"

        with patch.object(parser, "_decode_value", return_value="John Doe"):
            result = parser.extract_full_name(mock_vcard)
            assert result == "John Doe"

    def test_extract_name_from_n_field(self, parser):
        """Test extracting name components from N field"""
        mock_vcard = MagicMock()
        mock_name = MagicMock()
        mock_name.given = "John"
        mock_name.family = "Doe"
        mock_name.additional = "Middle"
        mock_vcard.n.value = mock_name

        data = {}
        result = parser.extract_name(mock_vcard, data)

        assert result["first_name"] == "John"
        assert result["last_name"] == "Doe"
        assert result["middle_name"] == "Middle"

    def test_extract_phone_numbers(self, parser):
        """Test extracting and normalizing phone numbers"""
        mock_vcard = MagicMock()
        mock_tel = MagicMock()
        mock_tel.value = "0532 123 45 67"
        mock_vcard.tel = [mock_tel]

        with patch.object(parser, "_get_type", return_value="CELL"):
            data = {}
            result = parser.extract_phone_numbers(mock_vcard, data)

            assert result["mobile_phone"] == "+905321234567"

    def test_extract_email(self, parser):
        """Test extracting email address"""
        mock_vcard = MagicMock()

        with patch("core.utils.recursive_getattr", return_value="john@example.com"):
            data = {}
            result = parser._extract_email(mock_vcard, data)

            assert result["email"] == "john@example.com"

    def test_decode_value_quoted_printable(self, parser):
        """Test decoding quoted-printable encoded values"""
        mock_field = MagicMock()
        mock_field.value = "=C4=B0stanbul"
        mock_field.encoding_param = ["QUOTED-PRINTABLE"]

        with patch("quopri.decodestring") as mock_decode:
            mock_decode.return_value.decode.return_value = "İstanbul"
            result = parser._decode_value(mock_field)
            assert result == "İstanbul"

    def test_get_type_from_field(self, parser):
        """Test extracting type from vCard field"""
        mock_field = MagicMock()
        mock_field.type_param = ["CELL", "PREF"]

        result = parser._get_type(mock_field)
        assert result == "CELL"

    def test_parse_manual_fallback(self, parser):
        """Test manual parsing fallback"""
        vcard_block = """BEGIN:VCARD
FN:John Doe
N:Doe;John;;;
TEL:+905321234567
EMAIL:john@example.com
END:VCARD"""

        with patch.object(parser, "_decode_manual", side_effect=lambda x: x):
            result = parser._parse_manual(vcard_block)

            assert result is not None
            assert result["full_name"] == "John Doe"
            assert result["first_name"] == "John"
            assert result["last_name"] == "Doe"

    def test_parse_with_vobject_success(self, parser, sample_vcard_content):
        """Test successful parsing with vobject"""
        with patch("vobject.base.readOne") as mock_readone, patch.object(
            parser, "_extract_data", return_value={"name": "John"}
        ):

            mock_vcard = MagicMock()
            mock_readone.return_value = mock_vcard

            result = parser.parse(sample_vcard_content)

            assert len(result) == 2
            assert all(contact == {"name": "John"} for contact in result)

    def test_parse_with_vobject_failure_fallback(self, parser):
        """Test fallback to manual parsing when vobject fails"""
        vcard_content = """BEGIN:VCARD
FN:John Doe
END:VCARD"""

        with patch("vobject.base.readOne", side_effect=Exception("Parse error")), patch.object(
            parser, "_parse_manual", return_value={"name": "John"}
        ):

            result = parser.parse(vcard_content)

            assert len(result) == 1
            assert result[0] == {"name": "John"}

    def test_decode_manual_quoted_printable(self, parser):
        """Test manual decoding of quoted-printable"""
        with patch("quopri.decodestring") as mock_decode:
            mock_decode.return_value.decode.return_value = "İstanbul"
            result = parser._decode_manual("=C4=B0stanbul")
            assert result == "İstanbul"

    def test_decode_manual_regular_text(self, parser):
        """Test manual decoding of regular text"""
        result = parser._decode_manual("Regular Text")
        assert result == "Regular Text"

    def test_extract_data_comprehensive(self, parser):
        """Test comprehensive data extraction from vCard"""
        mock_vcard = MagicMock()

        # Mock all the extraction methods
        with patch.object(parser, "extract_full_name", return_value="John Doe"), patch.object(
            parser, "extract_name", return_value={"first_name": "John"}
        ), patch.object(parser, "extract_phone_numbers", return_value={"mobile_phone": "+905321234567"}), patch.object(
            parser, "_extract_email", return_value={"email": "john@example.com"}
        ), patch(
            "core.utils.recursive_getattr", return_value=None
        ):

            # Mock additional fields
            mock_vcard.org = MagicMock()
            mock_vcard.title = MagicMock()
            mock_vcard.note = MagicMock()

            with patch.object(parser, "_decode_value", side_effect=lambda x: "Mocked Value"):
                result = parser._extract_data(mock_vcard)

                assert "first_name" in result
                assert "mobile_phone" in result
                assert "email" in result
