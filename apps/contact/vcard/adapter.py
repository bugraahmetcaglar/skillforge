from __future__ import annotations

import datetime
from typing import Any, Dict, List, Optional
import vobject

from core.utils import recursive_getattr


class VCardAdapter:
    """Adapter for a single vobject.vCard instance."""

    def __init__(self, vcard: vobject.base.Component):
        self.vcard = vcard
        self._cache: Dict[str, Any] = {}

    def _get_cached(self, key: str, getter_func) -> Any:
        """Cache expensive operations"""
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
    def nickname(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.nickname.value")

    @property
    def email(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.email.value")

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
        emails = self.emails
        return emails[0]["value"] if emails else None

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
    def mobile_phone(self) -> Optional[str]:
        """Get mobile phone number"""
        for phone in self.phones:
            if "CELL" in phone.get("type", []) or "MOBILE" in phone.get("type", []):
                return phone["value"]
        # Fallback to first phone if no mobile found
        return self.phones[0]["value"] if self.phones else None

    @property
    def addresses(self) -> List[Dict[str, str]]:
        """Get all addresses with their types"""

        def _get_addresses():
            addresses = []
            if hasattr(self.vcard, "adr_list"):
                for adr in self.vcard.adr_list:
                    addresses.append(self._parse_address(adr))
            elif hasattr(self.vcard, "adr"):
                addresses.append(self._parse_address(self.vcard.adr))
            return addresses

        return self._get_cached("addresses", _get_addresses)

    @property
    def primary_address(self) -> Optional[str]:
        """Get formatted primary address"""
        addresses = self.addresses
        return addresses[0]["full"] if addresses else None

    # Organization info
    @property
    def organization(self) -> Optional[str]:
        org = recursive_getattr(self, "vcard.org.value")
        if isinstance(org, list):
            return org[0] if org else None
        return org

    @property
    def job_title(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.title.value")

    @property
    def department(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.role.value")

    @property
    def birthday(self) -> Optional[datetime.date]:
        breakpoint()
        birthday_str = recursive_getattr(self, "vcard.bday.value")
        if birthday_str:
            try:
                return datetime.datetime.strptime(str(birthday_str), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None
        return None

    @property
    def anniversary(self) -> Optional[datetime.date]:
        anniversary_str = recursive_getattr(self, "vcard.x_anniversary.value")
        if anniversary_str:
            try:
                return datetime.datetime.strptime(str(anniversary_str), "%Y-%m-%d").date()
            except (ValueError, TypeError):
                return None

    @property
    def photo_url(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.photo.value")

    @property
    def websites(self) -> List[str]:
        return recursive_getattr(self, "vcard.url.value", [])

    @property
    def social_profiles(self) -> dict:
        return recursive_getattr(self, "vcard.x_social_profiles.value", {})

    @property
    def notes(self) -> Optional[str]:
        return recursive_getattr(self, "vcard.note.value")

    @property
    def urls(self) -> List[str]:
        return recursive_getattr(self, "vcard.url.value", [])

    # Utility methods
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "nickname": self.nickname,
            "emails": self.emails,
            "phones": self.phones,
            "addresses": self.addresses,
            "organization": self.organization,
            "job_title": self.job_title,
            "department": self.department,
            "birthday": self.birthday,
            "anniversary": self.anniversary,
            "urls": self.urls,
            "notes": self.notes,
        }

    def _parse_address(self, adr) -> Dict[str, str]:
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
