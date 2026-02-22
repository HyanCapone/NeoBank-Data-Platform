from pyspark.sql.windows import Window
from pyspark.sql.functions import row_number, col

# 1. Combine the Target (Historical) data with the Inactivated Records
# This is where we prepare the history to ensure no duplicates exist and active records take precedence.
dfmerge = dfClientTAG.unionAll(dfUpdateInativos)

# 2. Apply Window Function to deduplicate records based on CustomerId
# We partition by CustomerId and order by IsActiveMember (Descending) so '1' (Active) comes first.
windowSpec = Window.partitionBy("CustomerId_TAG").orderBy(desc("IsActiveMember_TAG"))

# Assign a row number to each record within its partition
dfmerge = dfmerge.withColumn('_row_number', row_number().over(windowSpec))

# 3. Keep only the most recent/relevant record (where row_number == 1)
dfmerge = dfmerge.where(col('_row_number') == 1).drop('_row_number')

# 4. Final Union: Merge the clean history (dfmerge) with New Registers and Updates
# We must ensure all dataframes have the same structure before unionAll
dfversionfinal = dfmerge.unionAll(dfNewRegister).unionAll(dfUpdate)

# 5. Rename columns back to their original names for the Gold Layer
dfversionfinal = dfversionfinal.withColumnRenamed("RowNumber_TAG", "RowNumber")\
    .withColumnRenamed("CustomerId_TAG", "CustomerId")\
    .withColumnRenamed("Surname_TAG", "Surname")\
    .withColumnRenamed("CreditScore_TAG", "CreditScore")\
    .withColumnRenamed("Geography_TAG", "Geography")\
    .withColumnRenamed("Gender_TAG", "Gender")\
    .withColumnRenamed("Age_TAG", "Age")\
    .withColumnRenamed("Tenure_TAG", "Tenure")\
    .withColumnRenamed("Balance_TAG", "Balance")\
    .withColumnRenamed("NumOfProducts_TAG", "NumOfProducts")\
    .withColumnRenamed("HasCrCard_TAG", "HasCrCard")\
    .withColumnRenamed("IsActiveMember_TAG", "IsActiveMember")\
    .withColumnRenamed("EstimatedSalary_TAG", "EstimatedSalary")\
    .withColumnRenamed("Exited_TAG", "Exited")

# 6. Load into Gold Layer (Data Lake)
# Using coalesce(1) to avoid the "Small Files Problem" in big data, writing a single CSV file.
path_gold_write = 'abfss://silver@sabneobankproject.dfs.core.windows.net/NeoBank_Modelling'
dfversionfinal.coalesce(1).write.mode("overwrite").csv(path=path_gold_write, header=True)

print("Load process completed successfully to Silver/Gold Layer.")
