/* Setup Master Key */
CREATE MASTER KEY ENCRYPTION BY PASSWORD = '123456789@Passw';
GO

/* Create Scoped Credential for Data Lake Access via SAS Token */
CREATE DATABASE SCOPED CREDENTIAL CredencialNeoBank
WITH IDENTITY = 'SHARED ACCESS SIGNATURE',
SECRET = '<YOUR_SAS_TOKEN_HERE>'; 
GO

/* Create External Data Source (Bronze Layer) */
CREATE EXTERNAL DATA SOURCE DS_NEOBANKbronze
WITH (
    LOCATION = 'https://sabneobankproject.blob.core.windows.net/bronze',
    CREDENTIAL = CredencialNeoBank
);
GO

/* 
Create External File Format for CSV 
USE_TYPE_DEFAULT = TRUE is a best practice to handle NULL values appropriately.
*/
CREATE EXTERNAL FILE FORMAT formato_csv
WITH(
    FORMAT_TYPE = DELIMITEDTEXT,
    FORMAT_OPTIONS(
        FIELD_TERMINATOR = ',',
        STRING_DELIMITER = '"',
        FIRST_ROW = 2,
        USE_TYPE_DEFAULT = TRUE
    )
);
GO
