# Glioma cancers

Gliomas are the most common central nervous system tumours (CNS). They account for approximately 30% of all primary brain tumours and 80% of all malignant tumours, with primary brain tumours causing a vast majority of cancer-related deaths. Gliomas can manifest in children and adults and their incidence depends on age, sex, and ethnicity [[1]](https://www.mdpi.com/1422-0067/22/19/10373). Gliomas occur in the glial cells of the brain and spinal cord and the glioma type depends on the glial cells they originate from. These cells include the astrocytes (astrocytoma), oligodendrocytes (oligodendrocytes/oligodendroglioma) [[2]](https://www.cancerresearchuk.org/about-cancer/brain-tumours/types/glioma-adults/) and the ependymal (ependymoma) glial cells [[3]](https://www.cancerresearchuk.org/about-cancer/brain-tumours/types/ependymoma/). The most common is astrocytoma which is characterised based on the WHO grades: pilocytic (Low Grade/Grade 1) which mainly occurs in children, diffuse (Grade 2), anaplastic (Grade 3) and glioblastoma (Grade 4) [[2]](https://www.cancerresearchuk.org/about-cancer/brain-tumours/types/glioma-adults/) with the survival rates decreasing with increase in grade [[1]](https://www.mdpi.com/1422-0067/22/19/10373).

Diagnosis and management of gliomas rely on tissue biopsy and treatment with radiotherapy and chemotherapy with genetic, transcriptomic and epigenetic alterations found to be key molecular signatures used in diagnosis and prognosis. Key biomarkers implicated in the pathogenesis of gliomas usually include genes involved in cell-cycle regulation. Some diagnostic and prognostic biomarkers implicated in glioma cancers include mutations in IDH, TP53, TERT, ATRX, and EGFR genes, 1p19q deletion, MGMT promoter methylation, etc [[4](https://www.frontiersin.org/journals/oncology/articles/10.3389/fonc.2014.00047/full), [5](https://pmc.ncbi.nlm.nih.gov/articles/PMC5337853/)]. Others include the mutations in the MAPK pathway genes, CDKN2A, MYB and MN1 genes [[1](https://www.mdpi.com/1422-0067/22/19/10373)].

Transcriptomics techniques, which use expression data generated from microarray and RNA sequencing methods, have been used to identify new biomarkers for glioma diagnosis and prognosis. This usually involves finding differential genes in normal and disease conditions. Similarly, machine learning models such as random forests, support vector machines, k-nearest neighbours, etc have been used to identify marker genes that can be used to predict disease outcomes or cancer subtypes [[6](https://www.sciencedirect.com/science/article/pii/S0888754319301740). Here, we apply transcriptomics data analysis to identify genes/RNA transcripts that can be used as potential biomarkers for glioma diagnosis. 

# Methodology

## Data source
Sixteen microarray datasets were downloaded from the Gene Expression Omnibus (GEO) database with assession numbers  GSE116520, GSE19728, GSE4290, GSE43289, GSE43378, GSE43911, GSE44971, GSE45921, GSE50161, GSE5675, GSE66354, GSE68015, GSE73066, GSE74462, and GSE90604.

## Data Preprocessing
Probes IDs in datasets were mapped to their respective gene symbols and common genes (12,699) in all datasets were selected for analysis. Datasets with untransformed expression values were log 2 transformed and all datasets were quantile transformed. To account for possible batch effect, batch effect correction was performed. Because the datasets were used for different experimental purposes, samples in each dataset related to gliomas were selected for analysis. These include ependymoma, glioblastoma, astrocytoma, oligodendroglioma or mixed gliomas (gliomas occurring in both astrocytes and oligodendrocytes). Finally, preprocessed datasets were merged and used for differential gene expression analysis.

## Data Analysis
Differential analysis was performed using the `limma` package in R (version 4.3.2). This was done to identify genes that are differentially expressed at disease conditions. Statistically significant genes based on p-value (false discovery rate, FDR) < 0.05 and absolute log fold change (logFC) of 1.5 and 2, depending on analysis criteria, were chosen as cutoffs. A volcano plot was used to visualise differential genes.

Analysis was done in three areas:
- Finding differentially expressed genes in non-tumour and tumour conditions
- Finding differential genes at tumour grades: G1-G2, G2-G3, G3-G4  of astrocyte-related cancers. These include pilocytic astrocytoma (G1), Low-grade astrocytoma (G2), anaplastic astrocytoma (G3) and glioblastoma multiforme (G4). This will help us identify prognostic biomarkers or key changes in gene expressions with astrocytoma cancer progression.
- Finding differential genes at each cancer cell type of glioma cancer: Astrocytes, ependymomas, oligodendrogliomas/oligodendrocytes and mixed gliomas (oligoastrocytes and astrocytes) to identify genes that are different in each cell-type glioma cancers.

Machine learning techniques were used to predict tumour and non-tumour conditions and detect cancer progression of astrocytoma and cancer cell types. The dataset was randomly split into train and test sets in a 75/25 ratio where the training data was used for model development and the test set used for evaluating performance. To reduce computational time and the number of features, statistically significant genes in the differential expression analysis were selected for model development. Further feature selection method based on the model's inherent feature selection capability was used to obtain the important features.

# Results

## Differential gene expression analysis (DGEA)

### Non-tumour vs Tumour conditions
Genes with absolute logFC above 2 were used as a cutoff to identify differential genes in disease and healthy (reference) conditions. 485 and 166 genes were found to be downregulated and upregulated, respectively, in the disease state. Among these genes are SVOP, CYP4X1, FRMPD4, UHRF1, and PARP9.



