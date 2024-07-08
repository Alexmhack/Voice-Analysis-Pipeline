import os
import io

from typing import Optional, Dict, Any

from azure.storage.blob import BlobServiceClient

AZURE_ACCOUNT_NAME = os.getenv("AZURE_ACCOUNT_NAME")
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
AZURE_STORAGE_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={AZURE_ACCOUNT_NAME};AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")


def upload_blob_stream(
    input_stream,
    file_name,
    folder_name,
    blob_service_client: Optional[BlobServiceClient] = None,
) -> Dict[str, Any]:
    """Uploads data stream to Azure blob storage using block-blob"""
    if not blob_service_client:
        blob_service_client = BlobServiceClient.from_connection_string(
            AZURE_STORAGE_CONNECTION_STRING
        )

    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME,
        blob=f"{folder_name}/{file_name}",
    )
    blob_client.upload_blob(input_stream, blob_type="BlockBlob", overwrite=True)
    return blob_client.url


def check_blob_exists(folder_name: str, file_name: str) -> bool:
    """Returns True if a blob exists with the defined parameters, and returns False otherwise."""
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME,
        blob=f"{folder_name}/{file_name}",
    )
    return blob_client.exists()


def download_blob_to_stream(folder_name: str, file_name: str) -> io.BytesIO:
    """Downloads blob and returns a stream"""
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=f"{folder_name}/{file_name}"
    )

    downloader = blob_client.download_blob(max_concurrency=1)
    blob_text = downloader.readall()
    return blob_text


def get_blob_url(folder_name: str, file_name: str) -> io.BytesIO:
    """Downloads blob and returns a stream"""
    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )
    blob_client = blob_service_client.get_blob_client(
        container=AZURE_STORAGE_CONTAINER_NAME, blob=f"{folder_name}/{file_name}"
    )
    return blob_client.url
