# 💸 FinOps & Escalabilidade: Plataforma de Dados Azure NeoBank

Como Engenheiro de Dados, construir a plataforma é apenas metade da batalha. Projetá-la para ser eficiente em custos e entender quando e como ela deve escalar é o que define uma arquitetura madura.

Abaixo está o plano de estimativa de custos e escalabilidade para a Plataforma de Dados NeoBank, calculado para a região **East US 2** (com base nos limites oficiais de preços do Azure).

---

## Cenário A: Prova de Conceito (POC) / Desenvolvimento
Em um ambiente de aprendizado ou POC, os custos são mantidos estritamente no mínimo usando as camadas mais básicas viáveis e aproveitando o auto-encerramento (auto-termination).

| Serviço Azure | Configuração (POC) | Uso Ativo | Custo Estimado (Mensal) |
| :--- | :--- | :--- | :--- |
| **Data Lake Storage Gen2** | Hot Tier, LRS (~1 GB de dados) | 24/7 (Apenas armazenamento) | **~$0.02** |
| **Azure Databricks** | Standard Tier (All-Purpose Compute)<br>Single Node (`Standard_DS3_v2`)<br>Auto-encerramento em 30 min | 10 Horas / Mês | **~$5.50** <br>*(~$0.40/DBU + VM)* |
| **Synapse Analytics** | Dedicated SQL Pool (DW100c)<br>Pausado quando não utilizado | 2 Horas / Mês | **~$3.02** <br>*(~$1.51/Hora)* |
| **Custo Total Estimado (POC)** | **Arquitetura Mínima Viável** | **~12 Horas de Atividade** | **~$8.54 / Mês** |

### Destaques FinOps para a POC:
- **Nunca deixe o Synapse Dedicated Pool rodando.** Pools SQL Dedicados cobram por hora, quer você execute consultas ou não. SEMPRE PAUSE o pool após suas operações de `COPY INTO`.
- **Auto-encerramento do Databricks:** Configurar clusters para desligar após 30 minutos de inatividade economiza centenas de dólares em uma equipe.

---

## Cenário B: MVP do Mundo Real em Produção & Escalabilidade
Uma POC de $9 é ótima, mas quantos dados essa exata arquitetura consegue lidar em um cenário do mundo real antes de "quebrar"?

### Limites da Arquitetura Atual (O Setup "Básico" de Produção)
Mesmo na configuração mais baixa (Single Node Databricks + DW100c Synapse), esta arquitetura é incrivelmente poderosa:
1. **Azure Databricks (`Standard_DS3_v2`):** Pode confortavelmente ingerir, transformar (SCD-2) e carregar entre **20 GB a 50 GB de novos dados diários** durante uma janela de lote (batch) noturna.
2. **Azure Synapse (DW100c):** Pode armazenar **~1 TB de dados históricos comprimidos de Data Warehousing** (usando Índices Clustered Columnstore) e servir dashboards do Power BI para dezenas de usuários simultâneos com latência de sub-segundos.

### Quando Escalar (Os Gatilhos)
Quando o negócio cresce além do MVP, você não reescreve o código. Você simplesmente escala a computação nativamente no Azure.

#### 1. Quando escalar o Azure Databricks (Compute Up)
* **O Gatilho:** Seu pipeline ETL noturno (Bronze ➔ Silver ➔ Gold) começa a exceder a janela de SLA acordada (ex: um processo que levava 15 minutos agora leva 2 horas devido ao volume de dados).
* **A Ação:** Mude de um cluster *Single Node* para um *Multi-Node Standard Cluster* e habilite o **Autoscaling** (ex: Min 2 Workers, Max 8 Workers). A natureza distribuída do Spark particionará automaticamente a carga de trabalho pelos novos nós.

#### 2. Quando escalar o Azure Synapse Analytics (DWU Up)
* **O Gatilho (Concorrência):** Você tem centenas de Analistas de BI ou ferramentas de relatórios automatizados disparando consultas complexas simultaneamente, fazendo com que as consultas entrem em fila de espera.
* **O Gatilho (Lentidão Ad-Hoc):** Consultas analíticas complexas sobre dados históricos massivos não particionados começam a ficar lentas. Em um DW100c, você tem apenas **1 Compute Node** gerenciando todas as 60 distribuições internas do Synapse.
* **A Ação:** Mova o controle deslizante para **DW400c** ou **DW500c**. No DW400c, o Azure ativa 4 Compute Nodes dedicados nos bastidores, o que significa que cada nó é responsável por consultar apenas 15 distribuições em paralelo, reduzindo drasticamente o tempo de consulta em bilhões de linhas.
