import pytest

from apps.contact.services import VCardParser


@pytest.fixture
def sample_vcard_content(self):
    return """BEGIN:VCARD
VERSION:3.0
FN:John Doe
N:Doe;John;;;
EMAIL:john@example.com
TEL:+905321234567
ORG:Example Corp
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Jane Smith
N:Smith;Jane;;;
EMAIL:jane@example.com
TEL:05551234567
END:VCARD"""


@pytest.fixture
def parser(self):
    return VCardParser()
