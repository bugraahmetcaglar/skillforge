from __future__ import annotations

import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def valid_vcard_content() -> str:
    """Valid vCard content with multiple contacts"""
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;Middle;;
TEL;TYPE=CELL:+905321234567
EMAIL:john.doe@example.com
ORG:Example Corp
TITLE:Software Engineer
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Jane Smith
N:Smith;Jane;;;
TEL;TYPE=HOME:05329876543
EMAIL:jane.smith@example.com
BDAY:1990-05-15
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Ali Veli
N:Veli;Ali;;;
TEL;TYPE=CELL:532 111 22 33
EMAIL:ali.veli@example.com
ORG:Turkish Company
END:VCARD"""


@pytest.fixture
def invalid_vcard_content() -> str:
    """Invalid vCard content for error testing"""
    return """INVALID:VCARD
FN:Invalid Contact
EMAIL:invalid@example.com
END:VCARD"""


@pytest.fixture
def empty_vcard_content() -> str:
    """Empty vCard with no contacts"""
    return """BEGIN:VCARD
VERSION:3.0
END:VCARD"""


@pytest.fixture
def turkish_phone_vcard() -> str:
    """vCard with various Turkish phone number formats"""
    return """BEGIN:VCARD
VERSION:3.0
FN:Turkish Contact
N:Contact;Turkish;;;
TEL;TYPE=CELL:05321234567
TEL;TYPE=HOME:0212 555 1234
TEL;TYPE=WORK:532-123-45-67
END:VCARD"""


@pytest.fixture
def vcard_file_factory(db):
    """Factory to create vCard file objects"""

    def _create_file(db, content: str, filename: str = "test.vcf") -> SimpleUploadedFile:
        file_content = content.encode("utf-8")
        return SimpleUploadedFile(filename, file_content, content_type="text/vcard")

    return _create_file
