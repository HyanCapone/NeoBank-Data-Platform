/* 
Create Physical Table in the Dedicated SQL Pool 
Data Warehousing Strategy:
- DISTRIBUTION = HASH (CustomerId): Ideal for Fact tables or large Dimensions to leverage Massively Parallel Processing (MPP).
- CLUSTERED COLUMNSTORE INDEX: Ideal for analytical workloads. achieving high data compression and fast column-based querying.
*/

CREATE TABLE ClientNeoBank
(
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
WITH
(
    DISTRIBUTION = HASH (CustomerId),
    CLUSTERED COLUMNSTORE INDEX
);
GO
