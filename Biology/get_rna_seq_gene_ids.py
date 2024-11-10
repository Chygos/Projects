# Gets gene names and symbol of RNA-Seq processed data

import mygene
from glob import glob
import pandas as pd
import re
from pathlib import os
from tqdm import tqdm

pd.set_option('display.max_columns', 40)

def fetch_gene_names(gene_ids, gene_id_type):
    """
    Gets the gene names and symbols of genes in a gene ID type
    """
    try:
        mg = mygene.MyGeneInfo()
        results = mg.querymany(gene_ids, scope=gene_id_type, fields='symbol, name', 
                               species='human', verbose=False, as_dataframe=True)
        return results
    except Exception as err: print(err)
        

files = glob('rna/*exprs*.csv')

gene_id_map = {'GSE228512':'ensembl.gene', 'GSE165595':'entrezgene'}


for file in files:
    filename = os.path.basename(file)
    file_id = re.search(r'^G..\d+', filename).group()
    gene_id_type = gene_id_map.get(file_id)

    if gene_id_type is None:
        print('No gene ID detected') 
        exit(1)
    
    if gene_id_type:
        gene_data = pd.read_csv(file)
        gene_ids = gene_data.iloc[:, 0].unique().tolist()
        gene_ids = list(map(str, gene_ids))

        # pass gene_ids in chunksize of 3000
        gene_dfs = pd.DataFrame()
        chunk = 3000
        for idx in tqdm(range(0, len(gene_ids), chunk), desc=f"Getting gene names and symbols for {file_id}"):
            gene_id_set = gene_ids[idx:idx+chunk]

            gene_df = fetch_gene_names(gene_id_set, gene_id_type)
            gene_dfs = pd.concat([gene_dfs, gene_df])

        gene_dfs.to_csv(file_id+'_gene_name.csv')
        # print(gene_dfs.head())





