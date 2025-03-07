import os
import dotenv

from azure.storage.blob import BlobServiceClient
from src.core.logger import logger


class BlobStorageClient:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self) -> None:
        """
            Initialize connection to Azure Blob Storage once.
            This method is called only once when the singleton instance is created.
        """

        dotenv.load_dotenv()

        self.connection_string = str(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        print(self.connection_string)
        if not self.connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING is not set")

        logger.info("Connecting to Azure Blob Storage")

        try:
            self.service_client = BlobServiceClient.from_connection_string(
                self.connection_string)
            logger.info("Successfully connected to Azure Blob Storage")
        except Exception as e:
            logger.error(f"Failed to connect to Azure Blob Storage: {e}")
            raise e

    def get_container_client(self, container_name):
        """Get a client for the specified container."""
        return self.service_client.get_container_client(container_name)
