
"""
Author: Chigozie Nkwocha
Date: 13.08.2024
"""

from pathlib import os
from glob import glob
import re
import numpy as np
import gzip
from tqdm import tqdm
import pandas as pd
from collections import Counter
import argparse, sys

# working environment
path = os.getcwd()

# get files
zip_files = np.array(glob(os.path.join(path, '*.gz')))
zip_files


## Helper functions
def get_target_class(filename:str, 
                     line_identifier:str='!Sample_characteristics'
                     ) -> pd.DataFrame:
    """
    Extracts target class from a microarray or RNA-seq text file based on a line and disease identifier
    :param filename: Filename/filepath
    :param line_identifier: Character used to identify line that maps the target class
    """
    try:
        sample_characteristics = []
        sample_ids = []
        sample_xter_ids = []
        
        lines = gzip.open(filename=filename, mode='rt').readlines() # rt= read text

        count = 0 # monitors the number of lines with line identifier
        for i, line in enumerate(lines):
            # get sample characteristics
            if line.startswith(line_identifier):
                xter = line.replace('"', '').replace('\n', '').split('\t')
                #xter = list(map(lambda x: re.sub(r'\w+\s?\w+:', '', x).strip(), xter))
                sample_characteristics.append(xter[1:])
                count = count + 1
                sample_xter_ids.append(f'sample_xter{count}')
            
            
            # get sample id which is immediately after !series matrix table begin
            elif line.startswith('!series_matrix_table_begin'):
                ids = lines[i+1]
                sample_ids.extend(ids.replace('"', '').split()[1:])
        metadata = pd.DataFrame(np.column_stack(sample_characteristics), columns=sample_xter_ids)
        
        # sample IDs may contain Gene ID reference, if it does, remove the first in the list
        if len(sample_ids) > len(metadata):
            sample_ids = sample_ids[1:]
        
        metadata = metadata.assign(sample_id = sample_ids)
        return metadata
    except ValueError as err: print(err)



def get_data(filename:str, 
             data_line_identifier:str='!series_matrix_table_begin', 
             has_data_identifier:bool=True)-> pd.DataFrame:

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
    except ValueError as err: print(err)


def main(args = sys.argv[1:]):
    parser = argparse.ArgumentParser(prog='Gene Expression Extractor', 
                                    description='Extract Gene Expression Datasets')
    
    parser.add_argument('-f', '--filename', nargs='+', help='Gene expression files to extract', 
                        type=str, required=True)
    
    parser.add_argument('--merge', required=False, choices=['T', 'F'], 
                        default='F', help='Valid inputs are T|F')
    
    parser.add_argument('-li', '--line_identifier', required=False, type=str, default='!Sample_characteristics',
                        help='Character used to identify line that maps the target class')

    parser.add_argument('-hdi', '--has_data_identifier', default=True, type=bool, choices=[True, False],
                        help='Boolean to indicate if expression data has a line identifier')

    parser.add_argument('-dli', '--data_line_identifier', help='line identifier to get dataset', 
                        default='!series_matrix_table_begin')

    parser.add_argument('-o', '--out', metavar='path/to/outfile.txt', help='Path to write data to')

    # parse arguments
    args = parser.parse_args()

    # variable to store expression data and metadata
    exprs = None
    metadata = None

    # raise error if file is not given
    if args.filename is None:
        raise ValueError('Must pass a filename or list of filenames')
        
    # provided filename, line identifier, disease name and identifier
    # check if merge
    if args.filename and all([args.line_identifier, 
                              args.data_line_identifier, 
                              args.has_data_identifier]):
        if args.merge == 'T' and len(args.filename) > 1:
            metadata = pd.concat(
                [
                    get_target_class(file, line_identifier=args.line_identifier)
                    for file in args.filename
                ], axis=0)
            
            exprs = pd.concat(
                [
                    get_data(file, 
                            data_line_identifier=args.data_line_identifier, 
                            has_data_identifier=args.has_data_identifier) 
                    for file in args.filename
                ], axis=1)
        elif args.merge == 'F' and len(args.filename) == 1:
            metadata = get_target_class(args.filename[0], 
                                        line_identifier=args.line_identifier
                                        )
            
            exprs = get_data(args.filename[0], 
                        data_line_identifier=args.data_line_identifier, 
                        has_data_identifier=args.has_data_identifier)
        
    else:
        raise ValueError ('--Error. Provide filename. Use -f or --filename to represent them')


    if args.out:
        if os.path.exists(os.path.join(path, args.out)):
            metadata.to_csv(args.out.replace('.csv', '') + '_metadata.csv', index=False)
            exprs.to_csv(args.out.replace('.csv', '') + '_counts.csv', index=False)
        else:
            os.makedirs(os.path.dirname(os.path.join(path, args.out)), exist_ok=True)
            if metadata is not None and exprs is not None:
                outfile = args.out.replace('.csv', '') + '_' + '.csv'
                metadata.to_csv(outfile + '_metadata.csv', index=False)
                exprs.to_csv(outfile + '_exprs.csv', index=True)

    elif args.out is None:
        os.makedirs('extracted_files', exist_ok=True)
        if len(args.filename) > 1:
            outfile = list(map(lambda x: re.search(r'GSE\d+', x).group(), args.filename))
            outfile = os.path.join(path, 'extracted_files', '-'.join(outfile))
        else:
            outfile = re.search(r'GSE\d+', args.filename[0]).group()
            outfile = os.path.join(path, 'extracted_files', outfile)
            if metadata is not None and exprs is not None:
                metadata.to_csv(outfile + '_metadata.csv', index=False)
                exprs.to_csv(outfile + '_exprs.csv', index=True)
                
    # print head of datasets
    if exprs is not None and metadata is not None:
        print('Metadata')
        print("=="*50)
        print(metadata.head())

        print('\nExpression')
        print("=="*50)
        print(exprs.head())
        
        print(f'file saved in {os.path.dirname(outfile)}')

    else:
        print('No files saved!')



if __name__ == "__main__":
    if len(sys.argv) > 1:
        print('Extracting files....')
        main()
