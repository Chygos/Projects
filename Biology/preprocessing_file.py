
from pathlib import os
from glob import glob
import re
import numpy as np
import gzip
import pandas as pd

# working environment
path = os.getcwd()

# get files
zip_files = np.array(glob(os.path.join(path, '*.gz')))
zip_files


## Helper functions
def get_files(text:str='GSE116520|GSE90604') -> list: 
    files = list(map(lambda file: re.search(text, file), zip_files))
    index = [True if x else False for x in files]
    return (zip_files[index]).tolist()


def get_target_class(filename:str, 
                     line_identifier:str='!Sample_characteristics', 
                     disease_identifier:str=None, 
                     disease_name:str=None) -> pd.DataFrame:
    """
    Extracts target class from a microarray or RNA-seq text file based on a line and disease identifier
    :param filename: Filename/filepath
    :param line_identifier: Character used to identify line that maps the target class
    :param disease_identifier: Regular expression pattern to identify disease and healthy samples
    :param disease_name: Name of the disease. All other are assumed to be healthy tissues
    """
    try:
        target_class = []
        sample_characteristics = []
        sample_xter_id = []
        sample_ids = []

        lines = gzip.open(filename=filename, mode='rt').readlines() # rt= read text
        for i, line in enumerate(lines):
            # get sample characteristics
            if line.startswith(line_identifier):
                xter = line.replace('"', '').replace('\n', '').split('\t')
                xter = list(map(lambda x: re.sub('\w+\s?\w+:', '', x).strip(), xter))
                sample_characteristics.append(xter[1:])
                header = list(set(re.search('\w+\s?\w+:', line).group().replace(":", "").split('\t')))
                sample_xter_id.extend(header)

                # extract line that has the disease identifier
                res = re.search(disease_identifier, line)
                if res is not None:
                    # extract disease name
                    res = res.group().split('\t')
                    target_class = [disease_name if disease_name in i else 'healthy' for i in res]
            
            # get sample id which is immediately after !series matrix table begin
            elif line.startswith('!series_matrix_table_begin'):
                ids = lines[i+1]
                sample_ids.extend(ids.replace('"', '').split()[1:])
        metadata = pd.DataFrame(np.column_stack(sample_characteristics), columns=sample_xter_id)
        metadata['class'] = target_class
        metadata = metadata.apply(lambda x: x.str.capitalize())
        
        # sample IDs may contain Gene ID reference, if it does, remove the first in the list
        if len(sample_ids) > len(metadata):
            sample_ids = sample_ids[1:]
        
        metadata = metadata.assign(sample_id = sample_ids)
        return metadata
    except Exception as err: print(err)



def get_data(filename:str, 
             data_line_identifier:str='!series_matrix_table_begin', 
             has_data_identifier=True)-> pd.DataFrame:

    """
    Extracts data from a microarray or RNA-seq text file based on a line identifier if present
    :param filename: Filename/filepath
    :param data_line_identifier: Character used to identify line that maps the target class
    :param has_data_identifier: Boolean if data has a line identifier
    """
    try:
        lines = gzip.open(filename=filename, mode='rt').readlines() # rt= read text
        
        data = []
        if has_data_identifier:
            if data_line_identifier is None:
                raise TypeError(f'{data_line_identifier} must not be empty if data has an identifier')
            for i, line in enumerate(lines):
                if line.startswith(data_line_identifier):
                    data_lines = lines[i+1:]
        else:
            data_lines = lines.copy()

        headers = data_lines[0].strip().replace('"', '').split()
        if len(data_lines) > 1: # contains both headers and data else skip
            data = [
                line.strip().replace('"', '').split() for line in data_lines[1:] if not line.startswith('!series_matrix_table_end')
                ]
            
        if len(data) > 0:
            if len(headers) < len(data[0]):
                headers.insert(0, 'GeneID')
        data = pd.DataFrame(data, columns=headers)
        data = data.set_index(headers[0])
        data.index = data.index.astype(str)
        return data
    except Exception as err: print(err)

"""
Extracting files
-----------------

Gene data were downloaded from NCI Geodataset website based on their accession numbers. 

Two sets (microarray and bulk RNA seq) of data were downloaded, the data and metadata were extracted and saved.

A). Micro array datasets: GSE116520 and GSE90604 which has both gene expressed (GPL17692) and miRNA expressed (GPL21572) datasets
B). RNA seq datasets: GSE165595 and GSE228512 with the later having both GPL16791 (Hiseq) and GPL24676 (novoseq) sequencing types (both will be merged)

"""

# create directory
os.makedirs('rna', exist_ok=True)
os.makedirs('microarray', exist_ok=True)



# RNA seq data
# 1
filename = 'GSE165595'
GSE165595_data = get_data(get_files('GSE165595')[0], 
                          has_data_identifier=False)

GSE165595_metadata = get_target_class(get_files('GSE165595')[1], 
                                      disease_identifier='tumou?r status: .+', 
                                      disease_name='Tumor')

print(f'\nGEO Accession Number: {filename}\nData: {GSE165595_data.shape}\tMetadata: {GSE165595_metadata.shape}\n')

GSE165595_data.to_csv(os.path.join(path, 'rna', filename+'_counts.csv'))
GSE165595_metadata.to_csv(os.path.join(path, 'rna', filename+'_metadata.csv'), index=False)

# 2
filename = 'GSE228512'
GSE228512_hiseq_metadata = get_target_class(get_files('GSE228512-GPL16791')[0], 
                                            disease_identifier='disease: .+', 
                                            disease_name='Glioblastoma') # hiseq

GSE228512_hiseq_data = get_data(get_files('GSE228512_hiseq')[0], 
                                has_data_identifier=False) # hiseq


GSE228512_novoseq_metadata = get_target_class(get_files('GSE228512-GPL24676')[0], 
                                              disease_identifier='disease: .+', 
                                              disease_name='Glioblastoma') #novaseq

GSE228512_novoseq_data = get_data(get_files('GSE228512_novaseq')[0], 
                                  has_data_identifier=False) # novoseq

# merge both nova and hiseq data
GSE228512_data = pd.concat([GSE228512_hiseq_data, GSE228512_novoseq_data], axis=1)
GSE228512_metadata = pd.concat([
    GSE228512_hiseq_metadata, 
    GSE228512_novoseq_metadata
    ], axis=0, ignore_index=True)

print(f'GEO Accession Number: {filename}\nData: {GSE228512_data.shape}\tMetadata: {GSE228512_metadata.shape}\n')

GSE228512_data.to_csv(os.path.join(path, 'rna', filename+'_counts.csv'))
GSE228512_metadata.to_csv(os.path.join(path, 'rna', filename+'_metadata.csv'), index=False)

# delete these
del GSE228512_hiseq_data, GSE228512_novoseq_data, GSE228512_hiseq_metadata, GSE228512_novoseq_metadata


# MicroArray datasets
# 1
filename = 'GSE116520'
GSE116520_metadata = get_target_class(get_files('GSE116520')[0], 
                                      '!Sample_characteristics', 
                                      'disease state: .+', 
                                      'Glioblastoma')

GSE116520_data = get_data(get_files('GSE116520')[0], 
                          '!series_matrix_table_begin', 
                          True)

print(f'GEO Accession Number: {filename}\nData: {GSE116520_data.shape}\tMetadata: {GSE116520_metadata.shape}\n')

GSE116520_data.to_csv(os.path.join(path, 'microarray', filename+'_counts.csv'))
GSE116520_metadata.to_csv(os.path.join(path, 'microarray', filename+'_metadata.csv'), index=False)


# 2
filename = 'GSE90604_rna'
GSE90604_rna_metadata = get_target_class(get_files('GSE90604-GPL17692')[0], 
                                         '!Sample_characteristics', 'sample type: .+', 
                                         'tumor')

GSE90604_rna_data = get_data(get_files('GSE90604-GPL17692')[0], 
                             '!series_matrix_table_begin', 
                             True)



print(f'GEO Accession Number: {filename}\nData: {GSE90604_rna_data.shape}\tMetadata: {GSE90604_rna_metadata.shape}\n')

GSE90604_rna_data.to_csv(os.path.join(path, 'microarray', filename+'_counts.csv'))
GSE90604_rna_metadata.to_csv(os.path.join(path, 'microarray', filename+'_metadata.csv'), index=False)


# 3
filename = 'GSE90604_mirna'
GSE90604_mirna_metadata = get_target_class(get_files('GSE90604-GPL21572')[0], 
                                           '!Sample_characteristics', 
                                           'sample type: .+', 
                                           'tumor')

GSE90604_mirna_data = get_data(get_files('GSE90604-GPL21572')[0], 
                               '!series_matrix_table_begin', 
                               True)

print(f'Filename: {filename}\nData: {GSE90604_mirna_data.shape}\tMetadata: {GSE90604_mirna_metadata.shape}\n')

GSE90604_mirna_data.to_csv(os.path.join(path, 'microarray', filename+'_counts.csv'))
GSE90604_mirna_metadata.to_csv(os.path.join(path, 'microarray', filename+'_metadata.csv'), index=False)


# show files
print('='*80) print('Dataset Preview\n-----------------\n') print
(GSE90604_rna_data.iloc[:, :5].head()) print('-'*80, end='\n\n') print
(GSE90604_mirna_data.iloc[:, :5].head()) print('-'*80, end='\n\n') print
(GSE116520_data.iloc[:, :5].head()) print('-'*80, end='\n\n') print
(GSE165595_data.iloc[:, :5].head()) print('-'*80, end='\n\n') print
(GSE228512_data.iloc[:, :5].head()) print('-'*80, end='\n\n')
