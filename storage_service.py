import os
from google.cloud import storage
from google.oauth2 import service_account
import aiohttp
from datetime import timedelta

BUCKET_NAME = 'discord_imports'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ltper/OneDrive/Documents/Packrunners/prunners.json"
storage_client = storage.Client()
bucket = storage_client.get_bucket(BUCKET_NAME)

def generate_signed_url(blob_name):
    """Generate a v4 signed URL for downloading a blob."""
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=15),  # URL valid for 15 minutes
        method="GET")

    return url

async def upload_stream_to_gcs(data, destination_blob_name):
    """Uploads byte data to Google Cloud Storage."""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data)
    # Generate a signed URL for secure access
    return generate_signed_url(destination_blob_name)
