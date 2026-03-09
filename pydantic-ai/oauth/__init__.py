from slack_sdk.oauth.installation_store import FileInstallationStore

installation_store = FileInstallationStore(
    base_dir="./data/installations",
    historical_data_enabled=False,
)

__all__ = ["installation_store"]
