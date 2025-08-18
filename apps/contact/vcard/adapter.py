from __future__ import annotations

import base64
import datetime
import logging
import vobject

from typing import Any, Dict, List, Optional

from core.utils import recursive_getattr


logger = logging.getLogger(__name__)


class VCardAdapter:
    """Adapter for a single vobject.vCard instance.

    Tried with Google Contacts, exported via vCard format.
    Supports parsing and accessing various vCard properties in a consistent way.
    See vcard_sample() fixture for example usage. (TestVCardImportServiceIntegration.test_import_from_file_vcard_sample_creates_all_contacts())
    """

    def __init__(self, vcard: vobject.base.Component):
        self.vcard = vcard
        self._cache: Dict[str, Any] = {}

    def _get_cached(self, key: str, getter_func) -> Any:
        """Cache results of expensive property getters."""
        if key not in self._cache:
            self._cache[key] = getter_func()
        return self._cache[key]

    @property
    def first_name(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.n.value.given")

    @property
    def middle_name(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.n.value.additional")

    @property
    def last_name(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.n.value.family")

    @property
    def full_name(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.fn.value")

    @property
    def emails(self) -> List[Dict[str, str]]:
        """Get all email addresses with their types"""

        def _get_emails():
            emails = []
            if hasattr(self.vcard, "email_list"):
                for email in self.vcard.email_list:
                    emails.append({"value": email.value, "type": getattr(email, "type_param", ["INTERNET"])})
            elif hasattr(self.vcard, "email"):
                email = self.vcard.email
                emails.append({"value": email.value, "type": getattr(email, "type_param", ["INTERNET"])})
            return emails

        return self._get_cached("emails", _get_emails)

    @property
    def primary_email(self) -> Optional[str]:
        """Get the first email address"""
        return self.emails[0]["value"] if self.emails else None

    @property
    def phones(self) -> List[Dict[str, str]]:
        """Get all phone numbers with their types"""

        def _get_phones():
            phones = []
            if hasattr(self.vcard, "tel_list"):
                for tel in self.vcard.tel_list:
                    phones.append({"value": tel.value, "type": getattr(tel, "type_param", ["VOICE"])})
            elif hasattr(self.vcard, "tel"):
                tel = self.vcard.tel
                phones.append({"value": tel.value, "type": getattr(tel, "type_param", ["VOICE"])})
            return phones

        return self._get_cached("phones", _get_phones)

    @property
    def primary_phone(self) -> str | None:
        """Get first available phone (use this for general fallback)"""
        from apps.contact.utils import normalize_phone_number

        if self.phones:
            return normalize_phone_number(self.phones[0]["value"])

        return None

    @property
    def addresses(self) -> List[Dict[str, str]]:
        """Get all addresses with their types"""

        def _get_addresses():
            addresses = []
            try:
                # Check for adr_list first
                if hasattr(self.vcard, "adr_list"):
                    for adr in self.vcard.adr_list:
                        parsed_address = self._parse_address(adr)
                        if parsed_address:
                            addresses.append(parsed_address)
                # Fallback to single adr
                elif hasattr(self.vcard, "adr"):
                    parsed_address = self._parse_address(self.vcard.adr)
                    if parsed_address:
                        addresses.append(parsed_address)
                # Alternative: Check vcard.contents
                elif hasattr(self.vcard, "contents"):
                    adr_list = self.vcard.contents.get("adr", [])
                    for adr in adr_list:
                        parsed_address = self._parse_address(adr)
                        if parsed_address:
                            addresses.append(parsed_address)
            except Exception as e:
                logger.debug(f"Error parsing addresses: {e}")

            return addresses

        return self._get_cached("addresses", _get_addresses)

    @property
    def primary_address(self) -> str | None:
        """Get formatted primary address"""
        addresses = self.addresses
        return addresses[0]["full"] if addresses else None

    # TODO: bug with -> ORG:B;Tech
    # Organization info
    @property
    def organization(self) -> str | None:
        org = recursive_getattr(self, "vcard.org.value")
        if isinstance(org, list):
            return org[0] if org else None
        return org

    @property
    def job_title(self) -> str | None:
        return recursive_getattr(self, "vcard.title.value")

    @property
    def department(self) -> str | None:
        return recursive_getattr(self, "vcard.role.value")

    @property
    def birthday(self) -> datetime.date | None:
        birthday_str = recursive_getattr(self, "vcard.bday.value")
        if birthday_str:
            try:
                return datetime.datetime.strptime(str(birthday_str), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None
        return None

    @property
    def websites(self) -> List[str]:
        websites = []
        url_list = recursive_getattr(self, "vcard.url_list", [])
        for url in url_list:
            if hasattr(url, "value"):
                websites.append(url.value)
        return websites

    @property
    def notes(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.note.value")

    @property
    def photo_url(self) -> str | None:
        """Get photo URL if available, None if not set."""

        def _get_photo_url():
            try:
                if not hasattr(self.vcard, "photo"):
                    return None

                photo_value = self.vcard.photo.value

                # If it's a string and looks like URL, return it
                if isinstance(photo_value, str) and photo_value.startswith(("http://", "https://")):
                    return photo_value

                return None
            except Exception as e:
                logger.debug(f"Error getting photo URL: {e}")
                return None

        return self._get_cached("photo_url", _get_photo_url)

    @property
    def vcard_photo_base64(self) -> str | None:
        """Get base64 photo data if it's binary, None if it's a URL or not set."""

        def _get_photo_base64():
            try:
                if not hasattr(self.vcard, "photo"):
                    return None

                photo_value = self.vcard.photo.value

                # If it's binary data, convert to base64
                if isinstance(photo_value, bytes):
                    return base64.b64encode(photo_value).decode("utf-8")

                return None
            except Exception as e:
                logger.debug(f"Error getting photo base64: {e}")
                return None

        return self._get_cached("vcard_photo_base64", _get_photo_base64)

    @property
    def vcard_mime_type(self) -> str | None:
        """Get MIME type for base64 photo, None if it's URL"""

        def _get_mime_type():
            try:
                if not hasattr(self.vcard, "photo"):
                    return None

                photo_value = self.vcard.photo.value

                # Only return MIME type for binary data
                if isinstance(photo_value, bytes):
                    if photo_value.startswith(b"\xff\xd8"):
                        return "image/jpeg"
                    elif photo_value.startswith(b"\x89PNG"):
                        return "image/png"
                    elif photo_value.startswith(b"GIF87a") or photo_value.startswith(b"GIF89a"):
                        return "image/gif"
                    elif "JPEG" in photo_value.decode("utf-8", errors="ignore"):
                        return "image/jpeg"  # default
                    elif "PNG" in photo_value.decode("utf-8", errors="ignore"):
                        return "image/png"
                    elif "GIF" in photo_value.decode("utf-8", errors="ignore"):
                        return "image/gif"
                    else:
                        return None
                return None
            except Exception as e:
                logger.debug(f"Error getting MIME type: {e}")
                return None

        return self._get_cached("vcard_mime_type", _get_mime_type)

    # Utility methods
    def to_contact_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        try:
            return {
                "first_name": self.first_name,
                "middle_name": self.middle_name,
                "last_name": self.last_name,
                "full_name": self.full_name,
                "emails": self.emails,
                "phones": self.phones,
                "addresses": self.addresses,
                "organization": self.organization,
                "job_title": self.job_title,
                "department": self.department,
                "birthday": self.birthday.isoformat() if self.birthday else None,
                "websites": self.websites,
                "photo_url": self.photo_url,
                "notes": self.notes,
                # TODO: "vcard_photo_base64": self.vcard_photo_base64,
                # TODO: "vcard_mime_type": self.vcard_mime_type,
            }
        except Exception as err:
            logger.error(f"Error converting vCard to dict: {err}")
            raise ValueError(f"Failed to convert vCard to dict")

    def _parse_address(self, adr) -> dict[str, str]:
        """Parse address object into dictionary"""
        if hasattr(adr, "value"):
            value = adr.value
            return {
                "street": getattr(value, "street", ""),
                "city": getattr(value, "city", ""),
                "region": getattr(value, "region", ""),
                "code": getattr(value, "code", ""),
                "country": getattr(value, "country", ""),
                "type": getattr(adr, "type_param", "HOME"),
                "full": self._format_address(value),
            }
        return {}

    def _format_address(self, adr_value) -> str:
        """Format address as single string"""
        parts = [
            getattr(adr_value, "street", ""),
            getattr(adr_value, "city", ""),
            getattr(adr_value, "region", ""),
            getattr(adr_value, "code", ""),
            getattr(adr_value, "country", ""),
        ]
        return ", ".join(filter(None, parts))

    def __repr__(self) -> str:
        return f"VCardAdapter(name='{self.full_name}', emails={len(self.emails)})"
