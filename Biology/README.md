## **Introduction**
This contains Jupyter notebooks and Python and R codes for analysing biological datasets.

The datasets that will be used are RNA transcript data generated from microarray or RNA-seq (single-cell or bulk). Techniques that will be used to analyse them include the application of differential gene expression analysis to determine differentially expressed genes in a diseased state. 

## **Data Extraction and Analysis**

**Data Extraction**

The datasets (in RNA and microarray folders) were downloaded from the [NCBI Geo dataset website](https://www.ncbi.nlm.nih.gov/geo/) based on their accession numbers. Two sets (microarray and bulk RNA seq) of data were downloaded, and the data and metadata were extracted using the (preprocessing_file.py) and saved in their respective folders.

A). Microarray datasets: GSE116520 and GSE90604 which has both gene expressed (GPL17692) and miRNA expressed (GPL21572) datasets
B). RNA seq datasets: GSE165595 and GSE228512 with the latter having both GPL16791 (Hiseq) and GPL24676 (novoseq) sequencing types (both will be merged)

**Data Analysis**

In the data analysis part differentially expressed genes in the diseased state were identified using a statistical method. This can be found in the (analysis_file.ipynb)[analysis file]. Exploratory data analysis and preprocessing techniques were performed before analysis.

NB: >This is a work in progress and can be updated.

