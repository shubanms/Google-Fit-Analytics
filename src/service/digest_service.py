import os
import zipfile
import time

import pandas as pd

from io import BytesIO
from src.core.logger import logger
from src.schemas.schemas import DataDigestResponse, DataDigestError
from src.service.blob_service import BlobStorageClient

container_client = BlobStorageClient().get_container_client(
    str(os.getenv("AZURE_DIGEST_CONTAINER_NAME")))


async def digest_file(file):
    start_time = time.time()

    zip_bytes = await file.read()
    zip_stream = BytesIO(zip_bytes)

    logger.info("Reading ZIP file contents...")
    with zipfile.ZipFile(zip_stream, "r") as zip_ref:
        csv_files = {
            os.path.basename(name): zip_ref.read(name)
            for name in zip_ref.namelist()
            if name.endswith(".csv") and not name.endswith("Daily activity metrics/Daily activity metrics.csv")
        }

    if not csv_files:
        logger.warning("No valid CSV files found in the zip.")
        return DataDigestError(
            message="File not processed",
            error="No valid CSV files found in the zip"
        )

    logger.info(f"Extracted {len(csv_files)} CSV files from the ZIP.")

    dataframes = []
    for filename, file_content in csv_files.items():
        df = pd.read_csv(BytesIO(file_content))
        df["Date"] = filename.replace(".csv", "")
        dataframes.append(df)

    dataframe = pd.concat(dataframes, ignore_index=True)

    logger.info(f"Final dataframe created with shape: {dataframe.shape}")
    logger.info("Uploading dataframe to Azure Blob Storage...")

    csv_stream = BytesIO()
    dataframe.to_csv(csv_stream, index=False)
    csv_stream.seek(0)

    blob_client = container_client.get_blob_client("dataframe.csv")
    blob_client.upload_blob(csv_stream, overwrite=True,
                            timeout=600, blob_type="BlockBlob", max_concurrency=4)

    logger.info("Dataframe successfully uploaded to Azure Blob Storage.")

    total_time = time.time() - start_time
    logger.info(f"Total execution time: {total_time:.2f} seconds")

    response = DataDigestResponse(
        message="File processed successfully",
        process_time_sec=total_time,
        row_count=dataframe.shape[0],
        columns=dataframe.columns.tolist()
    )

    return response
