from __future__ import annotations

import logging
from typing import Any, Optional
from vobject import base as vobject

from apps.contact.enums import SourceEnum
from apps.contact.models import Contact
from apps.contact.utils import generate_unique_external_id
from apps.contact.vcard.adapter import VCardAdapter
from apps.user.models import User

logger = logging.getLogger(__name__)


class VCardImportService:
    """Service for importing vCard files"""

    def __init__(self, user: User):
        self.user = user

    def import_from_file(self, vcard_file: Any) -> dict[str, Any]:
        """Import contacts from vCard file"""
        try:
            content = self._read_file_content(vcard_file)
            contacts_data = self._parse_vcards(content)
            return self._save_contacts(contacts_data)
        except Exception as err:
            logger.exception(f"Import error: {err}")
            return {"imported_count": 0, "failed_count": 0, "total_processed": 0, "errors": [str(err)]}

    def _read_file_content(self, vcard_file: Any) -> str:
        """Read and decode vCard file content"""
        content = None
        
        try:
            # Ensure file is seeked to the start
            vcard_file.seek(0)
            
            # Read raw content
            raw_content = vcard_file.read()
            
            # Decode content
            try:
                content = raw_content.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning("Failed to decode as UTF-8, trying latin-1")
                content = raw_content.decode("latin-1")
                
            return content
            
        except Exception as e:
            logger.error(f"Failed to read vCard file: {e}")
            raise ValueError(f"Could not read vCard file: {e}")
        
        finally:
            try:
                vcard_file.close()
            except Exception:
                pass

    def _parse_vcards(self, content: str) -> list[dict]:
        """Parse vCard content using VCardAdapter"""
        contacts_data = []

        try:
            # Parse all vCards from content
            vcards = list(vobject.readComponents(content))

            for i, vcard in enumerate(vcards):
                try:
                    adapter = VCardAdapter(vcard)
                    contact_data = self._adapter_to_contact_data(adapter, i)
                    if contact_data:
                        contacts_data.append(contact_data)
                except Exception as err:
                    logger.warning(f"Failed to process vCard {i}: {err}")
                    continue

        except Exception as err:
            logger.error(f"Failed to parse vCard content: {err}")

        return contacts_data

    def _adapter_to_contact_data(self, adapter: VCardAdapter, index: int) -> Optional[dict[str, Any]]:
        """Convert VCardAdapter data to Contact model format"""
        # Skip if no meaningful data
        if not adapter.full_name and not adapter.primary_email and not adapter.mobile_phone:
            return None

        data = {
            "first_name": adapter.first_name or "",
            "middle_name": adapter.middle_name or "",
            "last_name": adapter.last_name or "",
            "full_name": adapter.full_name or "",
            "nickname": adapter.nickname or "",
            "email": adapter.primary_email or "",
            "mobile_phone": adapter.mobile_phone or "",
            "organization": adapter.organization or "",
            "job_title": adapter.job_title or "",
            "notes": adapter.notes or "",
            "birthday": adapter.birthday,
            "anniversary": adapter.anniversary,
            "user": self.user,
            "import_source": SourceEnum.VCARD.value,
        }

        # Generate unique external ID
        data["external_id"] = generate_unique_external_id(data=data, index=index, user=self.user)

        return data

    def _save_contacts(self, contacts_data: list[dict]) -> dict[str, Any]:
        """Save contacts to database"""
        if not contacts_data:
            return {
                "imported_count": 0,
                "failed_count": 0,
                "total_processed": 0,
                "errors": ["No valid contacts found"],
            }

        try:
            # Prepare Contact objects
            contact_objects = [Contact(**data) for data in contacts_data]

            # Bulk create with ignore_conflicts to handle duplicates
            created_contacts = Contact.objects.bulk_create(contact_objects, batch_size=500, ignore_conflicts=True)

            imported_count = len(created_contacts)
            failed_count = len(contact_objects) - imported_count

            return {
                "imported_count": imported_count,
                "failed_count": failed_count,
                "total_processed": len(contacts_data),
                "errors": [],
            }

        except Exception as err:
            logger.exception(f"Failed to save contacts: {err}")
            return {
                "imported_count": 0,
                "failed_count": len(contacts_data),
                "total_processed": len(contacts_data),
                "errors": [str(err)],
            }


# VCardParser artık gereksiz - silindi!
