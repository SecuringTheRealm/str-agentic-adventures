"""Service for Azure Blob Storage operations with SAS token generation."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from app.config import get_settings

logger = logging.getLogger(__name__)

# Lazy singleton
_blob_service: BlobStorageService | None = None


class BlobStorageService:
    """Wraps Azure Blob Storage operations with DefaultAzureCredential auth."""

    def __init__(self) -> None:
        self._client = None
        self._configured = False

    def _ensure_client(self) -> bool:
        """Lazily create the BlobServiceClient."""
        if self._client is not None:
            return True
        if self._configured:
            return False

        settings = get_settings()
        self._configured = True

        # Try account name + DefaultAzureCredential first
        if settings.azure_storage_account_name:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.storage.blob import BlobServiceClient

                account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
                self._client = BlobServiceClient(
                    account_url=account_url,
                    credential=DefaultAzureCredential(),
                )
                logger.info("Blob storage configured via managed identity")
                return True
            except Exception as e:
                logger.warning("Failed to init blob storage via MI: %s", e)

        # Fall back to connection string
        if settings.storage_connection_string:
            try:
                from azure.storage.blob import BlobServiceClient

                self._client = BlobServiceClient.from_connection_string(
                    settings.storage_connection_string
                )
                logger.info("Blob storage configured via connection string")
                return True
            except Exception as e:
                logger.warning("Failed to init blob storage: %s", e)

        logger.info("Blob storage not configured — images will use data URIs")
        return False

    def upload_image(
        self,
        container: str,
        blob_name: str,
        data: bytes,
        content_type: str = "image/png",
    ) -> str | None:
        """Upload image bytes and return a SAS URL.

        Returns None if blob storage is not configured.
        """
        if not self._ensure_client():
            return None
        try:
            from azure.storage.blob import ContentSettings

            blob_client = self._client.get_blob_client(
                container=container, blob=blob_name
            )
            blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )

            # Generate SAS token (1 hour expiry)
            sas_token = self._generate_sas_token(container, blob_name)
            if sas_token:
                return f"{blob_client.url}?{sas_token}"

            # Fallback: return the raw URL (will only work if public access is on)
            return blob_client.url
        except Exception as e:
            logger.warning("Failed to upload image to blob storage: %s", e)
            return None

    def _generate_sas_token(self, container: str, blob_name: str) -> str | None:
        """Generate a SAS token for a blob, trying user delegation key first."""
        from azure.storage.blob import BlobSasPermissions, generate_blob_sas

        settings = get_settings()

        if settings.azure_storage_account_name:
            # Use user delegation key for MI-based SAS
            try:
                delegation_key = self._client.get_user_delegation_key(
                    key_start_time=datetime.now(UTC),
                    key_expiry_time=datetime.now(UTC) + timedelta(hours=2),
                )
                return generate_blob_sas(
                    account_name=settings.azure_storage_account_name,
                    container_name=container,
                    blob_name=blob_name,
                    user_delegation_key=delegation_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.now(UTC) + timedelta(hours=1),
                )
            except Exception as e:
                logger.warning(
                    "User delegation SAS failed, trying account key: %s", e
                )

        # Fallback: extract account key from connection-string credential
        account_key = (
            self._client.credential.account_key
            if hasattr(self._client.credential, "account_key")
            else None
        )
        if not account_key:
            return None

        return generate_blob_sas(
            account_name=self._client.account_name,
            container_name=container,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(UTC) + timedelta(hours=1),
        )


def get_blob_storage_service() -> BlobStorageService:
    """Get or create the singleton BlobStorageService."""
    global _blob_service  # noqa: PLW0603
    if _blob_service is None:
        _blob_service = BlobStorageService()
    return _blob_service
