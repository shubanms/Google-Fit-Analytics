import os

from fastapi import APIRouter, UploadFile, File

from src.core.logger import logger
from src.service.digest_service import digest_file
from src.service.blob_service import BlobStorageClient

router = APIRouter()

container_client = BlobStorageClient().get_container_client(str(os.getenv("AZURE_UPLOAD_CONTAINER_NAME")))

@router.post('/digest-file/')
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename}")

    response = await digest_file(file)

    return response
