import os

from fastapi import APIRouter, UploadFile, File

from src.core.logger import logger
from src.service.blob_service import BlobStorageClient

router = APIRouter()

container_client = BlobStorageClient().get_container_client(
    str(os.getenv("AZURE_UPLOAD_CONTAINER_NAME")))


@router.post('/upload-file/')
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")

    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file.file.read(), overwrite=True)

    return {"message": "File uploaded successfully"}
