# Databricks connection script using Service Principal (Microsoft Entra ID / OAuth)
# This script configures the connection between Azure Databricks and Azure Data Lake Storage Gen2.
# Note: In environments with Unity Catalog enabled, External Locations are the recommended approach.

# 1. Provide the credentials (these should ideally be stored in Azure Key Vault and referenced via Databricks Secrets)
client_id = 'd3aab496-1a05-49f6-bc45-4583bbadf944'
tenant_id = 'abda5095-837f-4c4e-b901-71581baaa2ec'
client_secret = '<YOUR_CLIENT_SECRET_HERE>' # Warning: Do not hardcode secrets in production code.
storage_account_name = 'sabneobankproject'
container_name = 'bronze'

# 2. Configure the directory structure for the OAuth protocol
configs = {
    "fs.azure.account.auth.type": "OAuth",
    "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
    "fs.azure.account.oauth2.client.id": f"{client_id}",
    "fs.azure.account.oauth2.client.secret": f"{client_secret}",
    "fs.azure.account.oauth2.client.endpoint": f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"
}

# 3. Mount the Data Lake container to the Databricks File System (DBFS)
# This allows reading and writing to the Data Lake as if it were a local file system.
dbutils.fs.mount(
    source = f"abfss://{container_name}@{storage_account_name}.dfs.core.windows.net/",
    mount_point = f"/mnt/{storage_account_name}/{container_name}",
    extra_configs = configs
)

print(f"Directory /mnt/{storage_account_name}/{container_name} successfully mounted using OAuth.")
