from google.auth import impersonated_credentials, default
from google.auth.credentials import Credentials
import logging


class GoogleCredentialManager:
    """
    Manages Google Cloud credentials, with optional impersonation of a service account.
    """

    def __init__(self, env: str = "local", impersonation_account: str = None):
        """
        Initialize the GoogleCredentialManager.

        Args:
            env (str): The environment type ('local' or 'production').
            impersonation_account (str, optional): The email of the service account to impersonate.
                                                   If not provided, the default application credentials
                                                   are used.
        """
        self.impersonation_account = impersonation_account
        self.env = env
        self.logger = logging.getLogger("credential_manager")

    def get_credentials(self) -> Credentials:
        """
        Retrieve Google Cloud credentials, optionally impersonating a service account.

        Returns:
            Credentials: Google Cloud credentials.

        Raises:
            ValueError: If the environment is unknown or misconfigured.
        """
        print(f"Environment: {self.env} - Retrieving credentials.")

        source_credentials, _ = default()

        if self.env == "local" and self.impersonation_account:
            print(
                f"Impersonating service account: {self.impersonation_account}"
            )
            return impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.impersonation_account,
                target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        elif self.env == "production" and self.impersonation_account:
            print("Using default service account credentials in production.")
            return impersonated_credentials.Credentials(
                source_credentials=source_credentials,
                target_principal=self.impersonation_account,
                target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )

        elif self.env == "local":
            print("Using local credentials without impersonation.")
            return source_credentials

        else:
            raise ValueError(f"Unknown environment: {self.env}")