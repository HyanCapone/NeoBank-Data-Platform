/* 1. Ensure File Format Exists */
IF NOT EXISTS (SELECT * FROM sys.external_file_formats WHERE name = 'SynapseDelimitedTextFormat')
    CREATE EXTERNAL FILE FORMAT [SynapseDelimitedTextFormat]
    WITH ( FORMAT_TYPE = DELIMITEDTEXT ,
           FORMAT_OPTIONS (
             FIELD_TERMINATOR = ',',
             STRING_DELIMITER = '"',
             FIRST_ROW = 2,
             USE_TYPE_DEFAULT = TRUE
            ))
GO

/* 2. Ensure External Data Source exists mapping to the Silver Layer */
IF NOT EXISTS (SELECT * FROM sys.external_data_sources WHERE name = 'silver_sabneobankproject_dfs_core_windows_net')
    CREATE EXTERNAL DATA SOURCE [silver_sabneobankproject_dfs_core_windows_net]
    WITH (
        LOCATION = 'abfss://silver@sabneobankproject.dfs.core.windows.net',
        TYPE = HADOOP
    )
GO

/* 3. Create the External Table */
/* This table acts as a pointer to the data sitting in the Data Lake, enabling T-SQL queries without data duplication. */

IF EXISTS (SELECT * FROM sys.external_tables WHERE name = 'extNeoBankClient') 
    DROP EXTERNAL TABLE [dbo].[extNeoBankClient]; 
GO 

CREATE EXTERNAL TABLE dbo.extNeoBankClient (
    RowNumber varchar(200),
    CustomerId varchar(200),
    Surname varchar(200),
    CredtScore varchar(200),
    Geography varchar(200),
    Gender varchar(200),
    Age varchar(200),
    Tenure varchar(200),
    Balance varchar(200),
    NumOfProducts varchar(200),
    HasCrCard varchar(200),
    IsActiveMember varchar(200),
    EstimatedSalary varchar(200),
    Exited varchar(200)
    )
    WITH (
    LOCATION = 'NeoBank_Modelling/neobankclients_databricks.csv',
    DATA_SOURCE = [silver_sabneobankproject_dfs_core_windows_net],
    FILE_FORMAT = [SynapseDelimitedTextFormat]
    )
GO

/* 4. Validation Query */
SELECT TOP 100 * FROM dbo.extNeoBankClient
GO
