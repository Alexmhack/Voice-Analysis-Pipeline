import os
import ast

from google.cloud import storage


## GCP UTILS
def delete_gcp_blob(bucket_name, blob_name):
    """Deletes a blob from the GCP Storage Bucket."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"

    gcp_service_account_info = ast.literal_eval(os.getenv("GCP_SERVICE_ACCOUNT_INFO"))
    storage_client = storage.Client.from_service_account_info(gcp_service_account_info)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    generation_match_precondition = None

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to delete is aborted if the object's
    # generation number does not match your precondition.
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation

    blob.delete(if_generation_match=generation_match_precondition)
    return True
