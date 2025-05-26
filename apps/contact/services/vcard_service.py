from __future__ import annotations

import logging
import quopri
from typing import Any

from vobject.base import readOne as vobject_readOne

from apps.contact.models import Contact
from apps.user.models import User

logger = logging.getLogger(__name__)


class VCardImportService:
    """Service for importing vCard files"""

    def import_from_file(self, vcard_file: Any, user: User) -> dict[str, Any]:
        try:
            content = vcard_file.read().decode("utf-8")
            parser = VCardParser()
            contacts = parser.parse(content)
            return self._save_contacts(contacts, user)
        except UnicodeDecodeError:
            raise ValueError("Invalid file encoding")
        except Exception as e:
            logger.error(f"Import error: {e}")
            raise ValueError(f"Import failed: {e}")

    def _save_contacts(self, contacts: list[dict], user: User) -> dict[str, Any]:
        imported_count = failed_count = 0
        errors = []

        
        for i, data in enumerate(contacts):
            try:
                data.update({"owner": user, "import_source": "vcard"})

                # Skip completely empty contacts
                if not any(
                    data.get(f)
                    for f in ["first_name", "last_name", "email", "mobile_phone"]
                ):
                    failed_count += 1
                    continue

                Contact.objects.create(**data)
                imported_count += 1

            except Exception as e:
                failed_count += 1
                errors.append(f"Contact {i+1}: {e}")

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
                # Try vobject first
                vcard = vobject_readOne(block)
                contact = self._extract_data(vcard)
                if contact:
                    contacts.append(contact)
            except Exception:
                # Fallback to manual parsing
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

        # Names
        if hasattr(vcard, "fn"):
            data["full_name"] = self._decode_value(vcard.fn)

        if hasattr(vcard, "n"):
            try:
                n = vcard.n.value
                data["first_name"] = getattr(n, "given", "") or ""
                data["last_name"] = getattr(n, "family", "") or ""
                data["middle_name"] = getattr(n, "additional", "") or ""
            except:
                pass

        # Fallback: split full name
        if not data.get("first_name") and data.get("full_name"):
            parts = data["full_name"].split(" ", 1)
            data["first_name"] = parts[0]
            if len(parts) > 1:
                data["last_name"] = parts[1]

        # Phones
        phones = []
        if hasattr(vcard, "tel"):
            tels = vcard.tel if isinstance(vcard.tel, list) else [vcard.tel]
            for tel in tels:
                try:
                    number = self._normalize_phone(tel.value.strip())
                    if number:
                        phone_type = self._get_type(tel)
                        phones.append({"number": number, "type": phone_type})

                        # Set primary phone
                        if not data.get("mobile_phone"):
                            data["mobile_phone"] = number
                except:
                    continue

        data["phones"] = phones

        # Email
        if hasattr(vcard, "email"):
            try:
                email = (
                    vcard.email.value
                    if not isinstance(vcard.email, list)
                    else vcard.email[0].value
                )
                data["email"] = email.strip().lower()
            except:
                pass

        # Other fields
        for field, attr in [
            ("organization", "org"),
            ("job_title", "title"),
            ("notes", "note"),
        ]:
            if hasattr(vcard, attr):
                value = self._decode_value(getattr(vcard, attr))
                if value:
                    data[field] = value

        # Birthday
        if hasattr(vcard, "bday"):
            try:
                data["birthday"] = vcard.bday.value
            except:
                pass

        return data

    def _decode_value(self, field: Any) -> str:
        try:
            value = field.value
            if hasattr(field, "encoding_param") and "QUOTED-PRINTABLE" in (
                field.encoding_param or []
            ):
                value = quopri.decodestring(value.encode()).decode("utf-8")
            return value.strip() if value else ""
        except:
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
        except:
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
                    data["mobile_phone"] = self._normalize_phone(value.strip())
                elif field == "EMAIL" and not data.get("email"):
                    data["email"] = value.strip().lower()
            except:
                continue

        return data if data else None

    def _decode_manual(self, value: str) -> str:
        try:
            if "=" in value:
                return quopri.decodestring(value.encode()).decode("utf-8")
        except:
            pass
        return value

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to +90XXXXXXXXXX format"""
        if not phone:
            return ""

        # Remove all non-digits
        digits = "".join(c for c in phone if c.isdigit())

        if not digits:
            return phone  # Return original if no digits found

        # Turkish phone number patterns
        if digits.startswith("90") and len(digits) == 12:
            # Already correct: 905323543683
            return f"+{digits}"
        elif digits.startswith("5") and len(digits) == 10:
            # Missing country code: 5323543683
            return f"+90{digits}"
        elif digits.startswith("05") and len(digits) == 11:
            # Leading zero: 05323543683
            return f"+90{digits[1:]}"
        elif len(digits) == 10 and digits[0] in "5":
            # Mobile without prefix: 5323543683
            return f"+90{digits}"
        elif len(digits) == 11 and digits.startswith("05"):
            # 05323543683 format
            return f"+90{digits[1:]}"
        else:
            # International or other format - keep as is but add + if missing
            return f"+{digits}" if not phone.startswith("+") else phone
