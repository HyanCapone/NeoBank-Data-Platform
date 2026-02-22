/* 
Load Data using COPY INTO 
This command reads the cleansed Parquet/CSV files directly from the Data Lake 
and loads them into the Dedicated SQL Pool physical table leveraging MPP compute nodes.
*/

COPY INTO dbo.ClientNeoBank
(
    RowNumber,
    CustomerId,
    Surname,
    CreditScore,
    Geography,
    Gender,
    Age,
    Tenure,
    Balance,
    NumOfProducts,
    HasCrCard,
    IsActiveMember,
    EstimatedSalary,
    Exited
)
FROM 'https://sabneobankproject.blob.core.windows.net/silver/NeoBank_Modelling/neobankclients_databricks.csv'

WITH
(
    FILE_TYPE = 'csv',
    FIELDTERMINATOR = ',',
    -- NEVER hardcode secrets in a real-world production environment! 
    -- Use Managed Identities or Azure Key Vault for enterprise setups.
    CREDENTIAL = (IDENTITY = 'Storage Account ValKey', SECRET = 'YOUR_SECRET_TOKEN_HERE'),
    FIRSTROW = 2
);
GO

/* Final Sanity Check Query */
SELECT TOP 10 * FROM dbo.ClientNeoBank;
SELECT COUNT(*) AS TotalClientesProcessados FROM dbo.ClientNeoBank;
GO
