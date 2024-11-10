## **Introduction**
This contains Jupyter notebooks and Python and R codes for analysing biological datasets.

## **Data Extraction and Analysis**

**Data Extraction**

The datasets used are RNA transcript data generated from microarray or RNA-seq (single-cell or bulk). The datasets (in RNA and microarray folders) were downloaded from the [NCBI Geo dataset website](https://www.ncbi.nlm.nih.gov/geo/) using their accession numbers. Two sets (microarray and bulk RNA seq) of data were downloaded, and the data and metadata were extracted using the [preprocessing file](extract_GEO_data.py) and saved in their respective folders. The [get_illumina_gene_ids.R](get_illumina_gene_ids.R) downloads Gene IDs for probesets based on a given GPL platform while this [file](get_rna_seq_gene_ids.py) gets the gene names for the RNA-seq datasets. This [file](preprocess_gene_ids.py) matches genes in all datasets and saves them alongside their microarray probe IDs.

A). Microarray datasets: GSE116520, GSE90604, which has both mRNA expressed (GPL17692) and miRNA expressed (GPL21572) datasets, plus [13 more datasets](microarray_gpl_ids.csv).
B). RNA seq datasets: GSE165595 and GSE228512 with the latter having both GPL16791 (Hiseq) and GPL24676 (novoseq) sequencing types (both will be merged)

The [analysis file](analysis_file.ipynb) contains a hands-on implementation of differential gene expression analysis in Python.

**Projects**

The [glioma folder](./glioma/) contains code scripts from a personal project to understand the molecular mechanisms in glioma cancers. This project focuses on 

- Identifying diagnostic biomarkers for detecting glioma cancer tissues.
- Identifying diagnostic and prognostic genes in glioma cancer grade progression (from grade 1-4). This was limited to astrocytoma grades.
- Identifying molecular signatures in different glioma cancer cell types. For this purpose, we used astrocytoma, oligodendroglioma, ependymoma and mixed glioma cell types.

Differential gene expression and functional analysis (pathway enrichment analysis) techniques were used to identify differentially expressed genes in each outcome and to determine the roles these differential genes play in the human organism. Pathway Enrichment Analysis was done to determine biological processes, molecular functions, cellular localisation and biological pathways these differentially expressed genes and their gene products are involved. Next, machine learning techniques were applied to develop models to distinguish between normal and tumour outcomes, cancer grades and glioma cancer cell types.


__Note__

> This is a work in progress and will be updated frequently.

