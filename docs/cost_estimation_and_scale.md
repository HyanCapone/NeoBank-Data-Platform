# 💸 FinOps & Scalability: Azure NeoBank Data Platform

As a Data Engineer, building a platform is only half the battle. Designing it to be cost-effective and understanding when and how it should scale is what defines a mature architecture.

Below is the cost estimation and scalability plan for the NeoBank Data Platform, calculated for the **East US 2** region (based on official Azure Pricing limits).

---

## Scenario A: Proof of Concept (POC) / Development
In a learning or POC environment, costs are kept strictly minimum by using the lowest viable tiers and leveraging auto-termination.

| Azure Service | Configuration (POC) | Active Usage | Estimated Cost (Monthly) |
| :--- | :--- | :--- | :--- |
| **Data Lake Storage Gen2** | Hot Tier, LRS (~1 GB of data) | 24/7 (Storage only) | **~$0.02** |
| **Azure Databricks** | Standard Tier (All-Purpose Compute)<br>Single Node (`Standard_DS3_v2`)<br>Auto-termination at 30 mins | 10 Hours / Month | **~$5.50** <br>*(~$0.40/DBU + VM)* |
| **Synapse Analytics** | Dedicated SQL Pool (DW100c)<br>Paused when not in use | 2 Hours / Month | **~$3.02** <br>*(~$1.51/Hour)* |
| **Total POC Estimated Cost** | **Minimal Viable Architecture** | **~12 Hours of Activity** | **~$8.54 / Month** |

### FinOps Highlights for POC:
- **Never leave the Synapse Dedicated Pool running.** Dedicated SQL Pools charge per hour whether you run queries or not. Always PAUSE the pool after your `COPY INTO` operations.
- **Databricks Auto-Termination:** Configuring clusters to shut down after 30 minutes of inactivity saves hundreds of dollars across a team.

---

## Scenario B: Production Real-World MVP & Scalability
A $9 POC is great, but how much data can this exact same architecture handle in a real-world scenario before it "breaks"?

### Current Architecture Limits (The "Basic" Production Setup)
Even at the lowest configuration (Single Node Databricks + DW100c Synapse), this architecture is remarkably powerful:
1. **Azure Databricks (`Standard_DS3_v2`):** Can comfortably ingest, transform (SCD-2), and load between **20 GB to 50 GB of new daily data** during a nightly batch window.
2. **Azure Synapse (DW100c):** Can store **~1 TB of compressed historical Data Warehousing data** (using Clustered Columnstore Indexes) and serve Power BI dashboards to dozens of concurrent users with sub-second latency.

### When to Scale (The Triggers)
When the business grows beyond the MVP, you don't rewrite the code. You simply scale the compute natively in Azure.

#### 1. When to scale Azure Databricks (Compute Up)
* **The Trigger:** Your nightly ETL pipeline (Bronze ➔ Silver ➔ Gold) begins to exceed the agreed SLA window (e.g., a process that took 15 minutes now takes 2 hours due to data volume).
* **The Action:** Move from a *Single Node* cluster to a *Multi-Node Standard Cluster* and enable **Autoscaling** (e.g., Min 2 Workers, Max 8 Workers). Spark's distributed nature will automatically partition the workload across the new nodes.

#### 2. When to scale Azure Synapse Analytics (DWU Up)
* **The Trigger (Concurrency):** You have hundreds of BI Analysts or automated reporting tools firing complex queries simultaneously, causing queries to queue.
* **The Trigger (Ad-Hoc Slowness):** Complex analytical queries over unpartitioned massive historical data begin to lag. In a DW100c, you only have **1 Compute Node** managing all 60 of Synapse's internal distributions.
* **The Action:** Move the slider to **DW400c** or **DW500c**. At DW400c, Azure spins up 4 dedicated Compute Nodes behind the scenes, meaning each node is only responsible for querying 15 distributions in parallel, drastically cutting down query times across billions of rows.
