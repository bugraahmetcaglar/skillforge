from __future__ import annotations

import logging
from typing import Any, Optional
import ulid
from vobject import base as vobject

from apps.contact.enums import SourceEnum
from apps.contact.vcard.adapter import VCardAdapter
from apps.user.models import User

logger = logging.getLogger(__name__)


class VCardImportService:
    """
    VCardImportService to handle importing contacts from vCard files.
    This service reads a vCard file, parses it, and saves the contacts to the database.
    It also validates the user and file before processing.

    Attributes:
        user (User): The user who owns the contacts.
        vcard_file (Any): The vCard file to import.
        vcard_file_content (Optional[str]): The content of the vCard file after reading and decoding.
        contacts_data (list[dict]): Parsed contact data from the vCard file.

    Methods:
        get_file_content() -> str: Reads and decodes the vCard file content.
        _parse_vcards(content: str) -> list[dict]: Parses vCard content into a list of contact data dictionaries.
        import_contacts() -> dict: Imports contacts from the vCard file and saves them to the database.
        _adapter_to_contact_data(adapter: VCardAdapter, index: int) -> dict[str, str] | None:
            Converts VCardAdapter data to Contact model format.
        _generate_photo_name(contact_data: dict) -> str: Generates a photo name based on contact information.
        _save_contacts(contacts_data: list[dict]) -> dict: Saves contacts to the database.

    Raises:
        ValueError: If any errors occur during import or validation.
    """

    def __init__(self, user: User, vcard_file: Any):
        """Initialize the service with user and vCard file.
        Args:
            user (User): The user who owns the contacts.
            vcard_file (Any): The vCard file to import.
        Raises:
            ValueError: If user is not provided or if vCard file is invalid.
        """
        self.user = user
        self.vcard_file = vcard_file
        self.vcard_file_content: Optional[str] = None

        self._validate_user()
        self._validate_file()

    def _validate_user(self):
        # Ensure user is provided and is a valid User instance
        if not self.user:
            raise ValueError("User must be provided for vCard import")

        # Check if user is an instance of User model
        if not isinstance(self.user, User):
            raise ValueError("Invalid user type, expected User instance")

        return True

    def _validate_file(self):
        # if vcard_file is not provided
        if not self.vcard_file:
            raise ValueError("No vCard file provided")

        # if vcard_file is empty
        if self.vcard_file.size == 0:
            raise ValueError("vCard file is empty")

        # if vcard_file is not a .vcf extension
        if not self.vcard_file.name.endswith(".vcf"):
            raise ValueError("File must be a .vcf format")

        # if vcard_file is not a file-like object
        if not hasattr(self.vcard_file, "read"):
            raise ValueError("Invalid vCard file format")

        return True

    # Reads the file, decodes it, and returns the content
    def get_vcard_file_content(self) -> str:
        # Check if content is already cached
        if self.vcard_file_content:
            return self.vcard_file_content

        try:
            self.vcard_file.seek(0)
            raw_content = self.vcard_file.read()
            try:
                self.vcard_file_content = raw_content.decode("utf-8")
            except UnicodeDecodeError:
                logger.warning("Failed to decode as UTF-8, trying latin-1")
                self.vcard_file_content = raw_content.decode("latin-1")
        except Exception as err:
            logger.error(f"Failed to read vCard file: {err}")
            raise ValueError(f"Could not read vCard file") from err
        finally:
            try:
                self.vcard_file.close()  # Always try to close the file
            except Exception:
                pass  # Ignore close errors

        if not self.vcard_file_content:
            logger.error("vCard file content is empty after reading")
            raise ValueError("vCard file content is empty")

        return self.vcard_file_content

    # Parse vCard content using VCardAdapter
    def save_vcards(self) -> bool:
        if not self.vcard_file_content:
            self.get_vcard_file_content()

        contact_data: dict[str, Any] = {}

        try:
            vcards = list(vobject.readComponents(self.vcard_file_content))

            for i, vcard in enumerate(vcards):
                try:
                    adapter = VCardAdapter(vcard)
                    contact_data = adapter.to_contact_dict()
                    contact_data["user"] = self.user.id
                    contact_data["import_source"] = SourceEnum.VCARD.value
                    contact_data["external_id"] = f"vcard_{ulid.ULID()}"

                    from apps.contact.tasks import task_save_contact

                    task_save_contact.delay(contact_data=contact_data)  # type: ignore
                except Exception as err:
                    logger.warning(f"Failed to process vCard {i}: {err}")
                    continue
            return True
        except Exception as err:
            logger.error(f"Failed to parse vCard content: {err}")
            raise ValueError("Failed to parse vCard content")
