import os
from google.cloud import storage
from google.oauth2 import service_account
import aiohttp

BUCKET_NAME = 'discord_imports'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/ltper/PCKSTATS/prunners.json"
storage_client = storage.Client()
bucket = storage_client.get_bucket(BUCKET_NAME)

async def upload_stream_to_gcs(data, destination_blob_name):
    """Uploads byte data to Google Cloud Storage."""
    blob = bucket.blob(destination_blob_name)
    # Upload the byte data
    blob.upload_from_string(data)
    # The public URL can be used to directly access the uploaded file via HTTP.
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{destination_blob_name}"

def get_public_url_of_blob(destination_blob_name):
    """Generate a public URL for the blob to make it accessible over the internet."""
    blob = bucket.blob(destination_blob_name)
    
    return blob.public_url
