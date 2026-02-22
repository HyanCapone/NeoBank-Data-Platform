from pyspark.sql.functions import desc, asc, when, col

# 1. Define paths for the Data Lake layers
path_bronze = 'abfss://bronze@sabneobankproject.dfs.core.windows.net/NeoBank_Modelling_Source.csv'
path_gold = 'abfss://gold@sabneobankproject.dfs.core.windows.net/NeoBank_Modelling.csv'

# 2. Read the source (New daily data) and the target (Current historical data)
dfClientSRC = spark.read.csv(path_bronze, header=True, inferSchema=True)
dfClientTAG = spark.read.csv(path_gold, header=True, inferSchema=True)

# 3. Rename columns to facilitate the join and identify changes (Source vs Target)
dfClientSRC = dfClientSRC.withColumnRenamed("RowNumber", "RowNumber_SRC")\
    .withColumnRenamed("CustomerId", "CustomerId_SRC")\
    .withColumnRenamed("Surname", "Surname_SRC")\
    .withColumnRenamed("CreditScore", "CreditScore_SRC")\
    .withColumnRenamed("Geography", "Geography_SRC")\
    .withColumnRenamed("Gender", "Gender_SRC")\
    .withColumnRenamed("Age", "Age_SRC")\
    .withColumnRenamed("Tenure", "Tenure_SRC")\
    .withColumnRenamed("Balance", "Balance_SRC")\
    .withColumnRenamed("NumOfProducts", "NumOfProducts_SRC")\
    .withColumnRenamed("HasCrCard", "HasCrCard_SRC")\
    .withColumnRenamed("IsActiveMember", "IsActiveMember_SRC")\
    .withColumnRenamed("EstimatedSalary", "EstimatedSalary_SRC")\
    .withColumnRenamed("Exited", "Exited_SRC")

dfClientTAG = dfClientTAG.withColumnRenamed("RowNumber", "RowNumber_TAG")\
    .withColumnRenamed("CustomerId", "CustomerId_TAG")\
    .withColumnRenamed("Surname", "Surname_TAG")\
    .withColumnRenamed("CreditScore", "CreditScore_TAG")\
    .withColumnRenamed("Geography", "Geography_TAG")\
    .withColumnRenamed("Gender", "Gender_TAG")\
    .withColumnRenamed("Age", "Age_TAG")\
    .withColumnRenamed("Tenure", "Tenure_TAG")\
    .withColumnRenamed("Balance", "Balance_TAG")\
    .withColumnRenamed("NumOfProducts", "NumOfProducts_TAG")\
    .withColumnRenamed("HasCrCard", "HasCrCard_TAG")\
    .withColumnRenamed("IsActiveMember", "IsActiveMember_TAG")\
    .withColumnRenamed("EstimatedSalary", "EstimatedSalary_TAG")\
    .withColumnRenamed("Exited", "Exited_TAG")

# 4. Perform a Left Join to compare Source (Bronze) against Target (Gold)
dfClientJoin = dfClientSRC.join(dfClientTAG, dfClientSRC.CustomerId_SRC == dfClientTAG.CustomerId_TAG, how='left')

# 5. Extract purely NEW records (Where the ID doesn't exist in the Target table)
dfNewRegister = dfClientJoin.where(dfClientJoin.RowNumber_TAG.isNull())
dfNewRegister = dfNewRegister.select(
    'RowNumber_SRC', 'CustomerId_SRC', 'Surname_SRC', 'CreditScore_SRC', 'Geography_SRC', 
    'Gender_SRC', 'Age_SRC', 'Tenure_SRC', 'Balance_SRC', 'NumOfProducts_SRC', 'HasCrCard_SRC', 
    'IsActiveMember_SRC', 'EstimatedSalary_SRC', 'Exited_SRC'
)

# 6. Identify records that suffered an UPDATE (They exist in both, but at least one column is different)
dfUpdate = dfClientJoin.where("""
    (CustomerId_SRC == CustomerId_TAG) and
    (RowNumber_TAG != RowNumber_TAG or
     Surname_SRC != Surname_TAG or
     CreditScore_SRC != CreditScore_TAG or
     Geography_SRC != Geography_TAG or
     Gender_SRC != Gender_TAG or
     Age_SRC != Age_TAG or
     Tenure_SRC != Tenure_TAG or
     Balance_SRC != Balance_TAG or
     NumOfProducts_SRC != NumOfProducts_TAG or
     HasCrCard_SRC != HasCrCard_TAG or
     IsActiveMember_SRC != IsActiveMember_TAG or
     EstimatedSalary_SRC != EstimatedSalary_TAG or
     Exited_SRC != Exited_TAG)
""")

# We need the old record to "inactivate" it (SCD-2 Logic) and the new record to insert it
dfUpdateInativos = dfUpdate

dfUpdate = dfUpdate.select(
    'RowNumber_SRC', 'CustomerId_SRC', 'Surname_SRC', 'CreditScore_SRC', 'Geography_SRC', 
    'Gender_SRC', 'Age_SRC', 'Tenure_SRC', 'Balance_SRC', 'NumOfProducts_SRC', 'HasCrCard_SRC', 
    'IsActiveMember_SRC', 'EstimatedSalary_SRC', 'Exited_SRC'
)

dfUpdateInativos = dfUpdateInativos.select(
    'RowNumber_TAG', 'CustomerId_TAG', 'Surname_TAG', 'CreditScore_TAG', 'Geography_TAG', 
    'Gender_TAG', 'Age_TAG', 'Tenure_TAG', 'Balance_TAG', 'NumOfProducts_TAG', 'HasCrCard_TAG', 
    'IsActiveMember_TAG', 'EstimatedSalary_TAG', 'Exited_TAG'
)

# 7. Inactivate the old records (Set IsActiveMember to 0)
dfUpdateInativos = dfUpdateInativos.withColumn(
    'IsActiveMember_TAG', 
    when(dfUpdateInativos.IsActiveMember_TAG == '1', '0').otherwise(dfUpdateInativos.IsActiveMember_TAG)
)

print("ETL SCD-2 Process Finished: New registers, Updates and Inactives separated.")
