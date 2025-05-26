# apps/contact/utils/vcard_parser.py
from __future__ import annotations

import vobject
import quopri
import re
from typing import Any, Iterator, TextIO
from datetime import datetime
from pathlib import Path


class VCardParser:
    """Enhanced vCard parser with automatic file handling"""

    def __init__(self, file_path: str | Path | TextIO | None = None):
        """Initialize parser with optional file path

        Args:
            file_path: Path to vCard file, file object, or None
        """
        self.file_path = file_path
        self._content = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup if needed"""
        self._content = None

    def parse_file(self, file_path: str | Path | TextIO) -> Iterator[dict[str, Any]]:
        """Parse vCard file with automatic file handling

        Args:
            file_path: Path to file, file object, or uploaded file

        Yields:
            dict: Contact data for each vCard entry
        """
        try:
            # Handle different input types
            if hasattr(file_path, "read"):
                # It's a file-like object (uploaded file)
                content = self._read_file_object(file_path)
            else:
                # It's a file path
                content = self._read_file_path(file_path)

            # Parse the content
            yield from self.parse_content(content)

        except Exception as e:
            raise ValueError(f"Error parsing vCard file: {str(e)}")

    def parse_content(self, content: str) -> Iterator[dict[str, Any]]:
        """Parse vCard content string"""
        if not self.validate_content(content):
            raise ValueError("Invalid vCard format")

        try:
            # Try vobject first
            vcards = vobject.readComponents(content)

            for vcard in vcards:
                contact_data = self._extract_vcard_data(vcard)
                if self._is_valid_contact(contact_data):
                    yield contact_data

        except Exception:
            # Fallback to manual parsing
            yield from self._manual_parse(content)

    def _read_file_object(self, file_obj) -> str:
        """Read content from file-like object (Django UploadedFile)"""
        try:
            # Save current position
            original_position = file_obj.tell() if hasattr(file_obj, "tell") else 0

            # Read content
            if hasattr(file_obj, "seek"):
                file_obj.seek(0)

            content = file_obj.read()

            # Decode if bytes
            if isinstance(content, bytes):
                content = content.decode("utf-8")

            # Reset position
            if hasattr(file_obj, "seek"):
                file_obj.seek(original_position)

            return content

        except Exception as e:
            raise ValueError(f"Error reading file object: {str(e)}")

    def _read_file_path(self, file_path: str | Path) -> str:
        """Read content from file path with automatic file handling"""
        try:
            path = Path(file_path)

            # Use context manager for automatic file closing
            with open(path, "r", encoding="utf-8") as file:
                return file.read()

        except FileNotFoundError:
            raise ValueError(f"File not found: {file_path}")
        except UnicodeDecodeError:
            # Try different encodings
            encodings = ["latin1", "cp1252", "iso-8859-1"]
            for encoding in encodings:
                try:
                    with open(path, "r", encoding=encoding) as file:
                        return file.read()
                except UnicodeDecodeError:
                    continue
            raise ValueError(
                f"Unable to decode file with any common encoding: {file_path}"
            )
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

    @staticmethod
    def validate_content(content: str) -> bool:
        """Check if content is valid vCard format"""
        try:
            if not content or not content.strip():
                return False

            # Check for vCard markers
            if "BEGIN:VCARD" not in content or "END:VCARD" not in content:
                return False

            return True
        except Exception:
            return False

    @staticmethod
    def _extract_vcard_data(vcard) -> dict[str, Any]:
        """Extract contact data from vCard object"""
        contact = {}

        try:
            # Extract name - handle both N and FN
            if hasattr(vcard, "n"):
                n_value = vcard.n.value
                contact["last_name"] = (
                    VCardParser._clean_text(n_value.family) if n_value.family else ""
                )
                contact["first_name"] = (
                    VCardParser._clean_text(n_value.given) if n_value.given else ""
                )

                # Handle middle name
                if hasattr(n_value, "additional") and n_value.additional:
                    if isinstance(n_value.additional, list) and n_value.additional[0]:
                        contact["middle_name"] = VCardParser._clean_text(
                            n_value.additional[0]
                        )
                    elif isinstance(n_value.additional, str):
                        contact["middle_name"] = VCardParser._clean_text(
                            n_value.additional
                        )

            # Fallback to FN if N doesn't provide enough info
            if hasattr(vcard, "fn"):
                full_name = VCardParser._clean_text(vcard.fn.value)
                contact["full_name"] = full_name

                # Parse name if not already set
                if not contact.get("first_name") or not contact.get("last_name"):
                    parsed_name = VCardParser._parse_full_name(full_name)
                    if not contact.get("first_name"):
                        contact["first_name"] = parsed_name.get("first_name", "")
                    if not contact.get("last_name"):
                        contact["last_name"] = parsed_name.get("last_name", "")

            # Extract phone number
            phone = VCardParser._extract_phone(vcard)
            if phone:
                contact["phone"] = VCardParser._clean_phone(phone)

            # Extract email
            if hasattr(vcard, "email"):
                contact["email"] = VCardParser._clean_text(vcard.email.value)

            # Extract notes
            if hasattr(vcard, "note"):
                contact["notes"] = VCardParser._clean_text(vcard.note.value)

            # Extract organization
            if hasattr(vcard, "org"):
                org_value = vcard.org.value
                if isinstance(org_value, str):
                    contact["organization"] = VCardParser._clean_text(org_value)
                elif hasattr(org_value, "__iter__"):
                    contact["organization"] = VCardParser._clean_text(
                        " ".join(str(x) for x in org_value if x)
                    )

            # Extract birthday
            if hasattr(vcard, "bday"):
                birthday = VCardParser._parse_birthday(vcard.bday.value)
                if birthday:
                    contact["birthday"] = birthday

            return contact

        except Exception as e:
            return {"error": f"Error extracting vCard data: {str(e)}"}

    @staticmethod
    def _parse_full_name(full_name: str) -> dict[str, str]:
        """Parse Turkish full names intelligently"""
        if not full_name:
            return {}

        # Clean and split
        name_parts = full_name.strip().split()
        if not name_parts:
            return {}

        result = {}

        # Handle titles/prefixes
        titles = {
            "Dr.",
            "Prof.",
            "Doç.",
            "Av.",
            "Müh.",
            "Dr",
            "Prof",
            "Doç",
            "Av",
            "Müh",
        }

        # Remove titles
        while name_parts and name_parts[0].rstrip(".") in titles:
            name_parts.pop(0)
        while name_parts and name_parts[-1].rstrip(".") in titles:
            name_parts.pop()

        if not name_parts:
            return {}

        if len(name_parts) == 1:
            result["first_name"] = name_parts[0]
        elif len(name_parts) == 2:
            result["first_name"] = name_parts[0]
            result["last_name"] = name_parts[1]
        else:
            # İlk kelime isim, geri kalanlar soyisim
            result["first_name"] = name_parts[0]
            result["last_name"] = " ".join(name_parts[1:])

        return result

    @staticmethod
    def _extract_phone(vcard) -> str | None:
        """Extract phone number with priority: CELL > HOME > others"""
        phones = []

        try:
            if hasattr(vcard, "tel_list"):
                cell_phones = []
                other_phones = []

                for tel in vcard.tel_list:
                    phone_value = tel.value
                    if hasattr(tel, "params") and tel.params:
                        if "CELL" in str(tel.params).upper():
                            cell_phones.append(phone_value)
                        else:
                            other_phones.append(phone_value)
                    else:
                        other_phones.append(phone_value)

                phones = cell_phones + other_phones

            elif hasattr(vcard, "tel"):
                phones.append(vcard.tel.value)

        except Exception:
            pass

        return phones[0] if phones else None

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and decode text (handle quoted-printable encoding)"""
        if not text:
            return ""

        try:
            # Handle quoted-printable encoding
            if "=" in text and any(c in text for c in "0123456789ABCDEF"):
                try:
                    decoded = quopri.decodestring(text.encode("latin1")).decode("utf-8")
                    return decoded.strip()
                except Exception:
                    pass

            return text.strip()

        except Exception:
            return str(text).strip()

    @staticmethod
    def _clean_phone(phone: str) -> str:
        """Clean and normalize phone number for Turkey"""
        if not phone:
            return ""

        # Remove all non-digit characters except +
        cleaned = re.sub(r"[^\d+]", "", phone.strip())

        # Handle Turkish phone formats
        if cleaned.startswith("90") and len(cleaned) == 12:
            cleaned = "+" + cleaned
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = "+90" + cleaned[1:]
        elif not cleaned.startswith("+") and len(cleaned) == 10:
            cleaned = "+90" + cleaned
        elif cleaned.startswith("5") and len(cleaned) == 10:
            cleaned = "+90" + cleaned

        return cleaned

    @staticmethod
    def _parse_birthday(bday_value: str) -> str | None:
        """Parse birthday from various formats"""
        if not bday_value:
            return None

        try:
            formats = ["%Y-%m-%d", "%Y%m%d", "%d/%m/%Y", "%m/%d/%Y"]

            for fmt in formats:
                try:
                    date_obj = datetime.strptime(bday_value, fmt)
                    return date_obj.strftime("%Y-%m-%d")
                except ValueError:
                    continue

        except Exception:
            pass

        return None

    @staticmethod
    def _manual_parse(content: str) -> Iterator[dict[str, Any]]:
        """Manual parsing fallback"""
        cards = content.split("BEGIN:VCARD")

        for card_content in cards[1:]:
            if "END:VCARD" not in card_content:
                continue

            contact = {}
            lines = card_content.split("\n")

            for line in lines:
                line = line.strip()
                if ":" not in line:
                    continue

                try:
                    key_part, value = line.split(":", 1)
                    key = key_part.split(";")[0]

                    if key == "FN":
                        full_name = VCardParser._clean_text(value)
                        contact["full_name"] = full_name
                        parsed_name = VCardParser._parse_full_name(full_name)
                        contact.update(parsed_name)

                    elif key == "N":
                        name_parts = value.split(";")
                        if len(name_parts) >= 2:
                            contact["last_name"] = VCardParser._clean_text(
                                name_parts[0]
                            )
                            contact["first_name"] = VCardParser._clean_text(
                                name_parts[1]
                            )
                            if len(name_parts) > 2 and name_parts[2]:
                                contact["middle_name"] = VCardParser._clean_text(
                                    name_parts[2]
                                )

                    elif key.startswith("TEL"):
                        if not contact.get("phone"):
                            contact["phone"] = VCardParser._clean_phone(value)

                    elif key.startswith("EMAIL"):
                        if not contact.get("email"):
                            contact["email"] = VCardParser._clean_text(value)

                    elif key == "NOTE":
                        contact["notes"] = VCardParser._clean_text(value)

                    elif key == "ORG":
                        contact["organization"] = VCardParser._clean_text(value)

                    elif key == "BDAY":
                        birthday = VCardParser._parse_birthday(value)
                        if birthday:
                            contact["birthday"] = birthday

                except Exception:
                    continue

            if VCardParser._is_valid_contact(contact):
                yield contact

    @staticmethod
    def _is_valid_contact(contact: dict) -> bool:
        """Check if contact has minimum required fields"""
        has_phone = bool(contact.get("phone"))
        has_name = bool(
            contact.get("first_name")
            or contact.get("last_name")
            or contact.get("full_name")
        )

        return has_phone and has_name
