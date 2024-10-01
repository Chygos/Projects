## **Introduction**
This contains Jupyter notebooks and Python and R codes for analysing biological datasets.

The datasets that will be used are RNA transcript data generated from microarray or RNA-seq (single-cell or bulk). Techniques that will be used to analyse them include the application of differential gene expression analysis to determine differentially expressed genes in a diseased state and functional annotation of differential genes. 

## **Data Extraction and Analysis**

**Data Extraction**

The datasets (in RNA and microarray folders) were downloaded from the [NCBI Geo dataset website](https://www.ncbi.nlm.nih.gov/geo/) based on their accession numbers. Two sets (microarray and bulk RNA seq) of data were downloaded, and the data and metadata were extracted using the [preprocessing file](extract_GEO_data.py) and saved in their respective folders. The [get_illumina_gene_ids.R](get_illumina_gene_ids.R) downloads Gene IDs for probesets based on a given GPL platform while the [file](get_rna_seq_gene_ids.py) gets the gene names for the RNA-seq datasets.

A). Microarray datasets: GSE116520, GSE90604, which has both mRNA expressed (GPL17692) and miRNA expressed (GPL21572) datasets, plus [13 more datasets](microarray_gpl_ids.csv).
B). RNA seq datasets: GSE165595 and GSE228512 with the latter having both GPL16791 (Hiseq) and GPL24676 (novoseq) sequencing types (both will be merged)

**Data Analysis**

In the data analysis part differentially expressed genes in the diseased state were identified using a statistical method. This can be found in the [analysis file](analysis_file.ipynb). Exploratory data analysis and preprocessing techniques were performed before analysis. Pathway Enrichment Analysis was done to determine biological processes, molecular functions, cellular localisation and biological pathways these differentially expressed genes and their gene products are involved.

NB: >This is a work in progress and can be updated.

