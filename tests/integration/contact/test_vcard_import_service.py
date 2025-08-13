import pytest

from unittest import mock

from apps.contact.vcard.services import VCardImportService


@pytest.mark.integration
@pytest.mark.django_db
class TestVCardImportServiceIntegration:

    @mock.patch("apps.contact.tasks.task_save_contact.delay")
    def test_save_vcards_with_comprehensive_vcard(
        self, mock_task_save_contact, user, vcard_sample, vcard_file_factory
    ):
        # Arrange
        vcard_file = vcard_file_factory(vcard_sample)
        service = VCardImportService(user=user, vcard_file=vcard_file)

        # Act
        result = service.save_vcards()

        # Assert
        assert result is True
        assert mock_task_save_contact.call_count == 5
