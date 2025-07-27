from __future__ import annotations

import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def vcard_sample():
    """Sample vCard content for testing"""

    return """BEGIN:VCARD
VERSION:3.0
FN:John Michael Doe
N:Doe;John;Michael;Mr.;Jr.
NICKNAME:Johnny
EMAIL;TYPE=WORK:john.doe@example.com
EMAIL;TYPE=HOME:johnny@personal.com
TEL;TYPE=CELL:0532 123 45 67
TEL;TYPE=HOME:0212 555 1234
TEL;TYPE=WORK:+90 216 444 5555
TEL;TYPE=FAX:0212 555 1235
ORG:Example Corporation;Engineering Department
TITLE:Senior Software Engineer
ROLE:Team Lead
BDAY:1985-03-15
ANNIVERSARY:2010-06-20
ADR;TYPE=HOME:;;123 Main St;Istanbul;Marmara;34000;Turkey
ADR;TYPE=WORK:;;456 Business Ave;Ankara;Central;06000;Turkey
URL:https://johndoe.com
URL:https://linkedin.com/in/johndoe
NOTE:Experienced software engineer specializing in Python and Django. Team lead with 10+ years experience.
CATEGORIES:Business,Developer,Friend
PHOTO:https://example.com/photos/john.jpg
X-CUSTOM-FIELD:Custom Value
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Jane Elizabeth Smith
N:Smith;Jane;Elizabeth;;Dr.
EMAIL:jane.smith@hospital.com
TEL;TYPE=CELL:05551234567
TEL;TYPE=WORK:0312 777 8888
ORG:City Hospital
TITLE:Chief Medical Officer
BDAY:1980-07-22
ADR;TYPE=WORK:;;789 Health St;Izmir;Aegean;35000;Turkey
NOTE:Cardiologist and department head
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Ali Mehmet Veli
N:Veli;Ali;Mehmet;;
EMAIL:ali.veli@turkish-company.com.tr
TEL:532 111 22 33
TEL:0216 333 4444
ORG:Türk Şirketi A.Ş.
TITLE:Genel Müdür
BDAY:1975-12-05
NOTE:Turkish company executive with special characters: çığöşü
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Empty Contact Test
END:VCARD

BEGIN:VCARD
VERSION:3.0
FN:Minimal Contact
EMAIL:minimal@test.com
END:VCARD"""


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

    def _create_file(content: str, filename: str = "test.vcf") -> SimpleUploadedFile:
        file_content = content.encode("utf-8")
        return SimpleUploadedFile(filename, file_content, content_type="text/vcard")

    return _create_file
