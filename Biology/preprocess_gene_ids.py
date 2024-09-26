
import re
from glob import glob
import pandas as pd
import numpy as np
from pathlib import os
from io import StringIO
import csv


def read_gene_file(file, columns=None):
    try:
        return pd.read_csv(file, low_memory=False, usecols=columns)
    except FileNotFoundError as err: print(err)
    except ValueError as err: print(err)
    exit(1)



files = glob('*gene_ids*.csv')

print(files)



# GSE116520_GPL10558

gse116520_10558 = read_gene_file(files[0], ['ID', 'Gene symbol', 'Gene ID', 'Platform_SEQUENCE'])
gse116520_10558.head()


# GSE90604_GPL17692
gse90604_17692 = read_gene_file(files[1], ['ID', 'gene_assignment', 'mrna_assignment'])
gse90604_17692.head()


# extract gene names from GPL 17692
gse90604_17692['Gene symbol'] = gse90604_17692.gene_assignment.str.split(' // ').str[1].str.strip()

# get gene symbol and their ID and create a map
gene_maps = gse116520_10558[['Gene symbol', 'Gene ID']].dropna()\
    .drop_duplicates()\
        .set_index('Gene symbol')\
            .to_dict()['Gene ID']



# merge genes from both platforms alongside their probe IDs and save
g1 = sorted(gse116520_10558['Gene symbol'].dropna().unique().tolist())
g2 = gse90604_17692['Gene symbol'].dropna().unique().tolist()

matched_genes = sorted(set(g1).intersection(set(g2)))
print('Number of genes matched in both datasets is {}'.format(len(matched_genes)))


genes = pd.DataFrame([(i, gene_maps[i]) for i in matched_genes], columns=['Gene symbol', 'Gene ID'])

# merge probe IDs from both data
genes = genes\
    .merge(gse116520_10558.drop('Gene ID', axis=1), on='Gene symbol', how='inner')\
        .merge(gse90604_17692[['ID', 'Gene symbol']], suffixes=['_GPL10558', '_GPL17692'],  on='Gene symbol')

genes.to_csv('microarray_genes.csv', index=False)



print(genes.head())


# GSE90604_GPL21572
# data = read_gene_file(files[2], ['ID', 'Accession_ID', 'Accession', 
#                                  'Transcript ID(Array Design)', 
#                                  'Sequence Type', 'Target Genes']
#                     )
# print(data.head())
# f = (
#     data['Target Genes']
#      .str.replace('^(MTI) // --- //', '', regex=True)
#      .apply(lambda x:np.nan if re.search(r'\w+ ///', x) is None else re.findall(r'[a-zA-Z0-9\._]+ ///', x))
#      .apply(lambda x: ''.join(x).replace('///', '').strip() if isinstance(x, list) else x)
#      #.apply(lambda x: len(x.split()) if isinstance(x, str) else 0)
#     )

# print(f.dropna())
# print(data['Transcript ID(Array Design)'].dropna().nunique())
# print(data[data['Transcript ID(Array Design)'].str.contains('^(?!^(hsa))', regex=True)])
# print(data[data['Transcript ID(Array Design)'].str.contains('^(hsa)', regex=True)])
# print(data[data['Sequence Type'].str.contains('miRNA')])
# print(data.shape)

