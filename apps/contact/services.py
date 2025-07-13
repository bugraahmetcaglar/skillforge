from __future__ import annotations

import logging
import quopri

from typing import Any
from vobject.base import readOne as vobject_readOne

from apps.contact.enums import SourceEnum
from apps.contact.models import Contact
from apps.contact.utils import generate_external_id, normalize_phone_number
from apps.user.models import User
from core.utils import recursive_getattr

logger = logging.getLogger(__name__)


class VCardImportService:
    """Service for importing vCard files"""

    def __init__(self, user: Any):
        if user and isinstance(user, User):
            self.user = user
        else:
            self.user = None

    def import_from_file(self, vcard_file: Any) -> dict[str, Any]:
        try:
            content = vcard_file.read().decode("utf-8")
            contacts = VCardParser().parse(content)
            return self._save_contacts(contacts)
        except UnicodeDecodeError:
            logger.exception("Failed to decode vCard file, trying alternative encoding")
            return {}
        except Exception as err:
            logger.exception(f"Import error: {err}")
            return {}

    def _save_contacts(self, contacts: list[dict]) -> dict[str, Any]:
        imported_count = failed_count = 0
        errors = []

        for i, data in enumerate(contacts):
            try:
                data.update({"user": self.user, "import_source": "vcard"})

                # Skip completely empty contacts
                if not any(data.get(f) for f in ["first_name", "last_name", "full_name", "email", "mobile_phone"]):
                    logger.error(f"Skipping empty contact {i+1}: {data = }")
                    failed_count += 1
                    continue

                # Generate external_id from full name or name parts
                data["external_id"] = generate_external_id(
                    data=f"{data.get("mobile_phone")}", source=SourceEnum.VCARD.value
                )

                Contact.objects.create(**data)
                imported_count += 1

            except Exception as err:
                logger.exception(f"Failed to save contact {i+1}: {data = }, {err = }")
                failed_count += 1
                errors.append(f"Contact {i+1}: {err}")

        return {
            "imported_count": imported_count,
            "failed_count": failed_count,
            "total_processed": len(contacts),
            "errors": errors,
        }


class VCardParser:
    """Parser for vCard content"""

    def parse(self, content: str) -> list[dict]:
        blocks = self._split_blocks(content)
        contacts = []

        for block in blocks:
            try:
                vcard = vobject_readOne(block)
                contact = self._extract_data(vcard)
                if contact:
                    contacts.append(contact)
            except Exception as err:
                logger.warning(f"Failed to parse vCard block: {err}, 'block': {block}")
                contact = self._parse_manual(block)
                if contact:
                    contacts.append(contact)

        return contacts

    def _split_blocks(self, content: str) -> list[str]:
        blocks = []
        current = []

        for line in content.strip().split("\n"):
            line = line.strip()
            if line.startswith("BEGIN:VCARD"):
                current = [line]
            elif line.startswith("END:VCARD"):
                current.append(line)
                blocks.append("\n".join(current))
                current = []
            elif current:
                current.append(line)

        return blocks

    def _extract_data(self, vcard: Any) -> dict:
        data = {}

        self.extract_full_name(vcard=vcard)
        data = self.extract_name(vcard=vcard, data=data)
        data = self.extract_phone_numbers(vcard=vcard, data=data)
        data = self._extract_email(vcard=vcard, data=data)

        # Other fields
        for field, attr in [("organization", "org"), ("job_title", "title"), ("notes", "note")]:
            if hasattr(vcard, attr):
                value = self._decode_value(getattr(vcard, attr))
                if value:
                    data[field] = value

        data["birthday"] = recursive_getattr(vcard, "bday.value")

        return data

    def extract_full_name(self, vcard: Any) -> str:
        """Extract full name from vCard"""
        if hasattr(vcard, "fn"):
            return self._decode_value(vcard.fn)
        return ""

    def extract_name(self, vcard: Any, data: dict) -> dict:
        """Extract first and last name from vCard"""
        if hasattr(vcard, "n"):
            try:
                name = vcard.n.value
                data["first_name"] = getattr(name, "given", "") or ""
                data["last_name"] = getattr(name, "family", "") or ""
                data["middle_name"] = getattr(name, "additional", "") or ""
            except Exception as err:
                logger.exception(f"Failed to extract name: {err}")

        if not data.get("first_name") and data.get("full_name"):
            parts = data["full_name"].split(" ", 1)
            data["first_name"] = parts[0]
            if len(parts) > 1:
                data["last_name"] = parts[1]
        return data

    def extract_phone_numbers(self, vcard: Any, data: dict) -> dict:
        phones = []
        if hasattr(vcard, "tel"):
            tels = vcard.tel if isinstance(vcard.tel, list) else [vcard.tel]
            for tel in tels:
                try:
                    # Use core utility for phone normalization
                    number = normalize_phone_number(tel.value.strip())
                    if number:
                        phone_type = self._get_type(tel)
                        phones.append({"number": number, "type": phone_type})

                        # Set primary phone
                        if not data.get("mobile_phone"):
                            data["mobile_phone"] = number
                except Exception as err:
                    logger.exception(f"Failed to extract phone number: {err}, 'tel': {tel}")
                    continue
        return data

    def _extract_email(self, vcard: Any, data: dict) -> dict:
        if hasattr(vcard, "email"):
            try:
                email = recursive_getattr(vcard, "email.value") or recursive_getattr(vcard, "email[0].value")
                data["email"] = email.strip().lower()
            except Exception as err:
                logger.exception(f"Failed to extract email: {err}, 'email': {vcard.email}")
        return data

    def _decode_value(self, field: Any) -> str:
        try:
            value = field.value
            if hasattr(field, "encoding_param") and "QUOTED-PRINTABLE" in (field.encoding_param or []):
                value = quopri.decodestring(value.encode()).decode("utf-8")
            return value.strip() if value else ""
        except Exception as err:
            logger.exception(f"Failed to decode field value: {err}, 'field': {field}")
            return str(getattr(field, "value", ""))

    def _get_type(self, field: Any) -> str:
        try:
            if hasattr(field, "type_param") and field.type_param:
                types = field.type_param
                if isinstance(types, list):
                    for t in ["CELL", "WORK", "HOME"]:
                        if t in types:
                            return t
                    return types[0].upper()
                return types.upper()
        except Exception as err:
            logger.exception(f"Failed to get type from field: {err}, 'field': {field}")
            pass
        return "OTHER"

    def _parse_manual(self, block: str) -> dict | None:
        """Fallback manual parsing"""
        data = {}

        for line in block.split("\n"):
            if ":" not in line:
                continue

            try:
                field, value = line.split(":", 1)
                field = field.split(";")[0]  # Remove parameters

                if field == "FN":
                    data["full_name"] = self._decode_manual(value)

                elif field == "N":
                    parts = value.split(";")
                    if len(parts) >= 2:
                        data["last_name"] = self._decode_manual(parts[0])
                        data["first_name"] = self._decode_manual(parts[1])

                elif field == "TEL" and not data.get("mobile_phone"):
                    # Use utility function for phone normalization
                    data["mobile_phone"] = normalize_phone_number(value.strip())

                elif field == "EMAIL" and not data.get("email"):
                    data["email"] = value.strip().lower()

            except Exception as err:
                logger.warning(f"Failed to parse line '{line}': {err}")
                continue

        return data if data else None

    def _decode_manual(self, value: str) -> str:
        try:
            if "=" in value:
                return quopri.decodestring(value.encode()).decode("utf-8")
        except Exception as err:
            logger.exception(f"Failed to decode manual value: {err}, 'value': {value}")
            pass
        return value
