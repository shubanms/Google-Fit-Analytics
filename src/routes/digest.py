import os
import zipfile

import pandas as pd

from io import BytesIO
from fastapi import APIRouter
from fastapi import UploadFile, File

from src.core.logger import logger
from src.schemas.schemas import DataDigestResponse, DataDigestError


router = APIRouter()


@router.post('/digest-file/')
async def upload_file(file: UploadFile = File(...)):
    zip_bytes = await file.read()
    zip_stream = BytesIO(zip_bytes)

    with zipfile.ZipFile(zip_stream, "r") as zip_ref:
        csv_files = {
            os.path.basename(name): zip_ref.read(name)
            for name in zip_ref.namelist()
            if name.endswith(".csv") and not name.endswith("Daily activity metrics/Daily activity metrics.csv")
        }

    if not csv_files:
        return DataDigestError(
            message="File not processed",
            error="No valid CSV files found in the zip"
        )

    dataframes = []
    for filename, file_content in csv_files.items():
        df = pd.read_csv(BytesIO(file_content))
        df["Date"] = filename.replace(".csv", "")
        dataframes.append(df)

    dataframe = pd.concat(dataframes, ignore_index=True)

    response = DataDigestResponse(
        message="File processed successfully",
        row_count=dataframe.shape[0],
        columns=dataframe.columns.tolist()
    )

    logger.info(f"Dataframe shape: {dataframe.shape}")
    logger.info(f"Dataframe columns: {dataframe.columns}")

    return response
