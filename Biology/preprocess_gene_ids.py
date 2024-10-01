import re
from glob import glob
import pandas as pd
from pathlib import os
from tqdm import tqdm


def read_gene_file(file, columns=None):
    try:
        return pd.read_csv(file, low_memory=False, usecols=columns)
    except FileNotFoundError as err: print(err)
    except ValueError as err: print(err)
    exit(1)



files = glob('gpl_gene_ids/*gene_ids*.csv')

# print(files)

# dict to get genes in each dataset
data_genes = {}
file_gpls = {} #get GPL IDs for each dataset

# matched genes in all datasets
matched_genes = set()

for file in tqdm(files, desc='Extracting Gene Names and getting genes in all datasets'):
    df = read_gene_file(file)
    df_cols = df.columns
    select_cols = ['ID'] + [col for col in df_cols if col.lower().replace('_', ' ') in ['gene symbol', 'gene assignment']]
    if len(select_cols) == 2:
        # get GPL platform ID
        gpl = re.search('GPL[0-9]+', file).group()
        gse = re.search('GSE[0-9]+', file).group()
        
        # mostly for unannotated data
        if 'gene_assignment' in select_cols:
            temp = df[select_cols]
            temp = temp.assign(Gene_symbol = temp[select_cols[-1]].str.strip().str.split('//').str[1].str.strip())
            temp = temp.rename({'Gene_symbol':'Gene symbol'}, axis=1)
            temp = temp[['ID', 'Gene symbol']].dropna().drop_duplicates()
            temp = temp.set_index('ID')
            temp.index.name = None
            temp = temp.to_dict()['Gene symbol']
            
            # add gpl and probe IDs of GEO GSE dataset
            file_gpls[gse] = gpl
            data_genes[gse] = temp

            # check for genes present in all dataset
            if len(matched_genes) == 0:
                matched_genes.update(set(list(temp.values())))
            else:
                matched_genes.intersection_update(set(list(temp.values())))
        else:
            temp = df[select_cols].dropna().drop_duplicates()
            temp = temp.rename({select_cols[-1]: 'Gene symbol'}, axis=1)
            temp = temp.set_index('ID')
            temp.index.name = None
            temp = temp.to_dict()['Gene symbol']
            file_gpls[gse] = gpl
            data_genes[gse] = temp

            if len(matched_genes) == 0:
                matched_genes.update(set(list(temp.values())))
            else:
                matched_genes.intersection_update(set(list(temp.values())))


# save matched probes with their respective gene names
os.makedirs('microarray_genes_ids', exist_ok=True)

# create dataframe to match probe in each GPL platform with gene symbol
matched_genes_df = pd.DataFrame({'Genes' : sorted(list(matched_genes))})
print(len(matched_genes_df))

for gse in tqdm(file_gpls.keys(), desc='Merging Genes in all datasets with their respective Probe IDs'):
    gse_data = pd.DataFrame({
        'ID':data_genes[gse].keys(), 
        'Genes':data_genes[gse].values()
        })
    gse_data = gse_data[gse_data['Genes'].isin(matched_genes_df.Genes)]

    temp_df = matched_genes_df.merge(gse_data, on='Genes', how='inner')
    filename = os.path.join('microarray_genes_ids', gse+ '_' + file_gpls[gse]+'.csv')
    temp_df.to_csv(filename, index=False)
