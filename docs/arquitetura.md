# Arquitetura de Dados - NeoBank

Aqui detalhamos as decisões de arquitetura e o fluxo de dados em cada camada do Data Lake.

## 1. Datalake e Camadas (Medallion)
- **Bronze:** Dados ingeridos em seu formato bruto (raw), preservando a história original sem alterações.
- **Silver:** Dados limpos, filtrados e unificados. Aqui aplicamos a regra de SCD Tipo 2 (Slowly Changing Dimensions) para manter o histórico de alterações dos correntistas (ex: mudança de endereço, status de ativação).
- **Gold:** Dados agregados e otimizados para leitura pelos sistemas de BI e Analytics.

## 2. Padrões de Segurança
Uso de **Access Connector for Azure Databricks** (Unity Catalog / External Locations) para garantir acesso seguro sem trafegar chaves fixas em código.

## 3. Synapse Analytics
O Synapse Serveless SQL é utilizado para criar Tabelas Externas via Polybase apontando para a camada Gold do Data Lake, abstraindo a complexidade para o analista de dados que consumirá a informação em T-SQL purista.
