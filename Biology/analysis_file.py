# Loading packages and libraries
from pathlib import os
from glob import glob
import numpy as np
import pandas as pd
import umap
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Literal, Union, Optional
import plotnine as pn
from sklearn import preprocessing, cluster, metrics
# from scipy.spatial.distance import pdist, squareform
from scipy import stats
from collections import Counter
from tqdm import tqdm
from scipy.cluster.hierarchy import linkage, dendrogram
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests # for adjusted pvals
from sklearn.decomposition import PCA
import gseapy as gspy
import csv

# get path
path = os.getcwd()

# function to read data
def read_data(file_id:str, file_type:str, folder:str=None) -> pd.DataFrame:
    """
    Reads data from a file and returns a Pandas DataFrame
    
    :param file_id: File identifier
    :param file_type: Type of data to read. Either a metadata or counts \
                      data containing expressed genes
    :param folder: Folder name
    
    Returns
    -------
    Pandas DataFrame
    """
    try:
        file = None
        if folder:
            filepath = os.path.join(path, folder)
            file = glob(filepath + f'/{file_id}*{file_type}*.csv')[0]
        else:
            file = glob(path + f'/{file_id}*{file_type}*.csv')[0]
        
        df = pd.read_csv(file, index_col=0)
        return df
    except Exception as err: print(err)


metadata = read_data('GSE116520', 'metadata', 'microarray').reset_index()
gene_counts = read_data('GSE116520', 'counts', 'microarray').T

gene_counts.head()
metadata.head()


def get_outliers(x:Union[pd.DataFrame, np.ndarray], 
                 method:Literal['zscore', 'iqr']='zscore') -> int:
    
    if not isinstance(x, (pd.DataFrame, np.ndarray)):
        raise ValueError ('x must be a Pandas DataFrame or Numpy array')
    try:
        if method == 'zscore':
            x_mean = np.mean(x, axis=0)
            x_std = np.std(x, axis=0)
            x_scaled = (x - x_mean)/x_std
            n_outliers = np.sum(abs(x_scaled) > 3, axis=0)
            return n_outliers
        elif method == 'iqr':
            p25 = np.percentile(x, q=25, axis=0)
            p75 = np.percentile(x, q=75, axis=0)
            iqr = p75 - p25
            lower = p25 - 1.5*iqr
            upper = p75 + 1.5*iqr
            n_outliers = np.sum((x < lower) | (x > upper), axis=0)
            return n_outliers
    except Exception as err: print(err)


def winsorizer(df:Union[pd.DataFrame, np.ndarray], percent:Union[int,float]=0.9):
    """
    Winsorizes data based on a certain percent
    :param df: A pandas dataframe or numpy array
    :param percent: Percentage cutoff point where values below or \
                    above limits are winsorized. A float or int
    """
    if not isinstance(df, (pd.DataFrame, np.ndarray)):
        raise ValueError ('df must be a Pandas DataFrame or Numpy array')
    if not isinstance(percent, (int, float)):
        raise ValueError (f'{percent} must be an integer or float')
    cutoff = round((100-percent)/2 if percent > 1 else 100*((1-percent)/2),3)
    upper_percentile = np.percentile(df, q=100-cutoff, axis=0)
    lower_percentile = np.percentile(df, q=cutoff, axis=0)

    upper_limit = np.max(df[df <= upper_percentile], axis=0)
    lower_limit = np.min(df[df >= lower_percentile], axis=0)
    df_winsorised = np.where(
        df < lower_limit, lower_limit, 
        np.where(df > upper_limit, upper_limit, df)
        )
    
    if df.__class__.__name__ == 'DataFrame':
        cols = df.columns
        index = df.index
        df_winsorised = pd.DataFrame(df_winsorised, columns=cols, index=index)
    return df_winsorised


def IQR_trimming(df:Union[pd.DataFrame, np.ndarray], cutoff=3):
    """
    Handles Outliers by capping outliers to the minimum and maximum values 
    without the outliers based on Intequartile range
    
    :param df: A pandas dataframe or numpy array
    :param cutoff: value to indicate outliers
    """
    if not isinstance(df, (pd.DataFrame, np.ndarray)):
        raise ValueError ('df must be a Pandas DataFrame or Numpy array')
    
    df_copy = df.copy()
    if isinstance(df, pd.DataFrame):
        df_copy = df_copy.to_numpy()
    
    p25 = np.percentile(df_copy, q=25, axis=0)
    p75 = np.percentile(df_copy, q=75, axis=0)
    iqr = p75 - p25

    lower_limit = p25 - cutoff*iqr
    upper_limit = p75 + cutoff*iqr
    
    # replace outliers by capping
    df_copy = np.where(
        df_copy < lower_limit, lower_limit, 
        np.where(df_copy > upper_limit, upper_limit, df_copy)
        )

    if df.__class__.__name__ == 'DataFrame':
        cols = df.columns
        index = df.index
        df_copy = pd.DataFrame(df_copy, columns=cols, index=index)
    return df_copy


def zscore_trimming(df:Union[pd.DataFrame, np.ndarray], cutoff=3):
    """
    Handles Outliers by capping outliers to the minimum and maximum values 
    without the outliers based on ZScore method
    
    :param df: A pandas dataframe or numpy array
    :param cutoff: Absolute value to indicate outliers
    """
    if not isinstance(df, (pd.DataFrame, np.ndarray)):
        raise ValueError ('df must be a Pandas DataFrame or Numpy array')
    
    df_copy = df.copy()
    if isinstance(df, pd.DataFrame):
        df_copy = df_copy.to_numpy()
    
    # scale data
    df_scaled = preprocessing.scale(df_copy, axis=0)
    
    # get lower and upper limits (min and max values without the outliers) 
    # of each gene in each sample 
    
    for i in tqdm(range(df_copy.shape[1])):
        outliers = abs(df_scaled[:, i]) > cutoff
        gene_data = df_copy[:, i]
        gene_data_inliers = gene_data[~outliers] # get gene data inlier
        upper_limit = np.max(gene_data_inliers) # get max and min values
        lower_limit = np.min(gene_data_inliers)

        # replace outliers
        gene_data = np.where(
            gene_data < lower_limit, lower_limit, 
            np.where(gene_data > upper_limit, upper_limit, gene_data)
            )
        df_copy[:, i] = gene_data
    
    if df.__class__.__name__ == 'DataFrame':
        cols = df.columns
        index = df.index
        df_copy = pd.DataFrame(df_copy, columns=cols, index=index)
    return df_copy


def outlier_treatment(df:Union[pd.DataFrame, np.ndarray], 
                      cutoff=Union[None, float, int], 
                      percent=Union[None, float, int],
                      treatment_type:Literal['winsorize', 'iqr', 'zscore', None]=None):
    
    if treatment_type == 'winsorize':
        if percent:
            df_copy = winsorizer(df, percent=percent)
    elif treatment_type == 'iqr':
        if cutoff:
            df_copy = IQR_trimming(df, cutoff=cutoff)
    elif treatment_type == 'zscore':
        if cutoff:
            df_copy = zscore_trimming(df, cutoff=cutoff)
    elif treatment_type is None:
        df_copy = df
    else:
        print(f'{treatment_type} not recognised!')
        exit(1)
    return df_copy


def describe_data(x:Union[pd.DataFrame, np.array]) -> pd.DataFrame:
    if isinstance(x, np.ndarray):
        cols = list(map(lambda x: f'col{x}', range(1, x.shape[1]+1)))
        x = pd.DataFrame(x, columns=cols)
    elif isinstance(x, pd.DataFrame):
        cols = x.columns
    else:
        raise TypeError (f'Input value must be a Pandas dataFrame or a Numpy array')
    
    res = pd.DataFrame(columns=cols)
    res.loc['std', :] = x.std()
    res.loc['mean', :] = x.mean()
    res.loc['min', :] = x.min()
    res.loc['p25', :] = x.quantile(q=0.25)
    res.loc['median', :] = x.median()
    res.loc['p75', :] = x.quantile(q=0.75)
    res.loc['max', :] = x.median()
    res.loc['skew', :] = x.skew()
    res.loc['kurt', :] = x.kurtosis()
    res.loc['iqr', :] = x.quantile(q=0.75) - x.quantile(q=0.25)
    res.loc['num_outliers'] = get_outliers(x)
    return res

describe_data(gene_counts)

def plot_distribution(df, num_genes=15, ncol=5, nrow=3, seed=None, 
                      figsize=(12,6), plot_type='kde'):
    """
    Plots the distribution of randomly selected genes against the class

    :param df: Pandas dataframe
    :param num_genes: Number of genes to plot distribution
    :param seed: Random seed value

    Returns a Matplotlib figure
    """
    try:
        if seed:
            rnd = np.random.RandomState(seed)
            random_idx = rnd.choice(range(df.shape[1]), num_genes, replace=False)
        else:
            random_idx = np.random.choice(range(df.shape[1]), num_genes, replace=False)

        selected_cols = df.columns[random_idx]

        # visualise
        plt.rcParams['font.size'] = 8
        fig, axes = plt.subplots(nrow, ncol, figsize=figsize)
        axes = axes.flatten()
        for col, ax in zip(selected_cols, axes):
            if plot_type == 'box':
                sns.boxplot(data=df, x=metadata['class'].values, y=col, 
                            hue=metadata['class'].values, ax=ax, width=0.6)
            elif plot_type == 'kde':
                sns.kdeplot(data=df, x=col, hue=metadata['class'].values, ax=ax)
            ax.set(xlabel='', ylabel='')
            ax.set_title(f"Gene: {col.replace('_', ' ')}", loc='left', 
                         fontsize=9, fontweight='bold')
        fig.tight_layout()
        plt.rcdefaults()
        plt.show()
    except Exception as err: print(err)

plot_distribution(gene_counts, plot_type='box', seed=10)

# Outlier Treatment
# gene_counts = outlier_treatment(gene_counts, percent=90, treatment_type='winsorize')
# plot_distribution(gene_counts, plot_type='box', seed=10)


# Dimensionality Reduction and Visualisation
def reduce_dimensions(df, n_components=2, reduction_type:Literal['pca', 'umaps']='pca'):
    try:
        X_scaled = preprocessing.scale(df, axis=0)
        
        if reduction_type == 'pca':
            reducer = PCA(n_components=n_components, random_state=42)
            X_trans = reducer.fit_transform(X_scaled)
        elif reduction_type == 'umaps':
            reducer = umap.UMAP(n_components=n_components, random_state=42, n_jobs=1)
            X_trans = reducer.fit_transform(X_scaled)
        
        return pd.DataFrame(X_trans, columns=[f'PC{i+1}' for i in range(X_trans.shape[1])])
    except Exception as err: print(err)

def plot_PCA(df:pd.DataFrame, 
             n_components:Union[int, float]=2, 
             decompose:Union[bool,None]=True,
             reduction_type:Literal['pca', 'umaps']='pca', 
             figsize=(8,5), labels=None):
        
    if decompose:
        X_trans = reduce_dimensions(df, n_components, reduction_type).iloc[:, :2]
    else:
        X_trans = df.iloc[:, :2]
        

    if labels is None:
        base = pn.ggplot(data=X_trans, mapping=pn.aes('PC1', 'PC2'))
    else:
        color = 'target'
        assert len(labels) == len(X_trans)
        X_trans[color] = labels

        base = pn.ggplot(data=X_trans, mapping=pn.aes('PC1', 'PC2', color=color))

    fig = (
        base +
        pn.geom_point(size=2, alpha=0.7) +
        pn.theme_bw() +
        pn.theme(plot_title=pn.element_text(face='bold', hjust=0, size=12), 
                legend_position = 'inside', 
                figure_size = figsize,
                legend_key = pn.element_blank(),
                legend_title = pn.element_text(hjust=0.5, face='bold'),
                panel_grid = pn.element_blank(),
                legend_position_inside=(0.01, 0.96)
                ) +
        pn.ggtitle(f"{reduction_type.replace('s', '').upper()} Dimensionality Reduction") +
        pn.scale_x_continuous(expand=(0.1, 0.15, 0.15, 0.1)) +
        pn.scale_y_continuous(expand=(0.1, 0.1, 0.1, 0.1)) 
    )
    if reduction_type == 'umaps':
        fig = fig + pn.labs(x='UMAP0', y='UMAP1')

    fig.show()

## Decompose along sample axis
plot_PCA(gene_counts, reduction_type='pca', labels=metadata['class'])

plot_PCA(gene_counts, reduction_type='umaps', labels=metadata['class'])


# Decomposing along gene axis
def run_optimal_clusters(df, n_clusters=15, scale=True, decompose=False, 
                         variance_cutoff:Union[int,float]=0.95,
                         axis_name:Literal['gene', 'sample']='sample',
                         dist_type:Literal['cosine', 'euclidean', 'correlation', None]=None):
    n_clusters = n_clusters
    sil_scores = []
    # reduce number of dimensions
    X = df.copy()

    if decompose:
        X = reduce_dimensions(X, n_components=variance_cutoff, reduction_type='pca')
        print('Number of components capturing {:.0f}% variance is {}'.format(
            100*variance_cutoff, X.shape[1]))
    if scale:
        X = preprocessing.scale(X)
    
    if axis_name == 'gene':
        X = X.T

    if len(X) < n_clusters:
        n_clusters = min(len(X), n_clusters)

    for i in tqdm(range(2, n_clusters+1)):
        if dist_type == 'euclidean':
            res = cluster.AgglomerativeClustering(i, linkage='ward', metric=dist_type)
        elif dist_type is None:
            res = cluster.KMeans(i, max_iter=500, n_init=10)
        elif dist_type != 'euclidean':
            res = cluster.AgglomerativeClustering(i, linkage='average', metric=dist_type)
        res.fit(X)
        sil_scores.append(metrics.silhouette_score(X, res.labels_))

    # visualise
    fig, ax = plt.subplots(1, figsize=(8,4.5))
    ax.plot(list(range(2,n_clusters+1)), sil_scores, 'o-', linewidth=1.4, markersize=3)
    ax.set_xticks(range(2, n_clusters+1, 2), range(2, n_clusters+1, 2))
    ax.set_xlabel('Number of clusters')
    ax.set_title('Silhouette Method', loc='left', fontweight='bold', fontsize=10)
    ax.set_ylabel('Silhouette scores', fontweight='bold')
    fig.tight_layout()
    plt.show()


def plot_dendrogram(df, scale=True, method='ward', metric='euclidean', 
                    axis_name:Literal['gene', 'sample']='sample'):
    if scale:
        X = preprocessing.scale(df, axis=0)
    if axis_name == 'gene':
        X = X.T
    
    plt.figure(figsize=(8,4.5))
    dendrogram(linkage(X, method='ward', metric='euclidean'))
    plt.title('Hierarchical Clustering', loc='left', fontweight='bold')
    plt.ylabel('Distances')
    plt.xlabel(axis_name.title()+'s')
    if axis_name == 'sample':
        plt.xticks(rotation=0, fontsize=7)
    else:
        plt.xticks([], rotation=0, fontsize=7)
    plt.show()


run_optimal_clusters(gene_counts, scale=True, dist_type='correlation')

run_optimal_clusters(gene_counts, decompose=True, scale=False)
plot_dendrogram(gene_counts)

def cluster_genes(
        df:pd.DataFrame, 
        n_clusters:int=2,
        decompose:bool=False,
        variance_cutoff:Union[int,float]=0.95,
        scale:bool=True,
        reduction_type:Literal['pca', 'umaps']='pca',
        cluster_type:Literal['gene', 'sample']='sample',
        plot=False
        ):
    """
    Clusters genes using Hierarchical Agglomerative clustering. 

    :param df: Pandas DataFrame
    :param n_cluster: Number of clusters
    :param decompose: Apply PCA to decompose features into Principal components
    :param variance_cutoff: Percentage variance captured by principal components (PCs)
    :param scale: To scale data (Standardisation)
    :param cluster_type: If clustering should be done along sample or gene axis
    """
    X = df.copy()
    # reduce dimensions
    if decompose:
        X = reduce_dimensions(X, n_components=variance_cutoff)
        print('Number of components capturing {:.0f}% variance is {}'.format(
            100*variance_cutoff, X.shape[1]))
    if scale:
        X = preprocessing.scale(X, axis=0)

    if cluster_type == 'gene':
        X = X.T
        
    # fit cluster
    res = cluster.AgglomerativeClustering(n_clusters, metric='euclidean', linkage='ward')    
    res.fit(X)
    labels = res.labels_
    labels = list(map(lambda x: f'cluster {x+1}', labels))
    
    # visualise data using pca
    if plot:
        plot_PCA(X, decompose=True, labels=labels, reduction_type=reduction_type)
    else:
        return labels


cluster_genes(gene_counts, plot=True)


## Differential Gene Analysis

def plot_volacano(deg_res:pd.DataFrame):
    if not isinstance(deg_res, pd.DataFrame):
        raise TypeError ('deg_res must be a Pandas DataFrame')
    
    # get the negative log of pval and color to map differentially expressed genes
    deg_res['neg_log_pval'] = -np.log10(deg_res['padj'])
    color = np.where(
        (deg_res['padj'] < 0.05) & (deg_res['Log2FC'] > 2), 'Up', 
        np.where((deg_res['padj'] < 0.05) & (deg_res['Log2FC'] < -2), 
                 'Down', 'Insig'))
    
    fig = (
        pn.ggplot(deg_res, pn.aes(x='Log2FC', y='neg_log_pval', color=color)) +
        pn.geom_point(alpha=0.5) +
        pn.geom_vline(xintercept=0, linetype='dashed', alpha=0.4) + 
        pn.theme_bw() +
        pn.theme(legend_position='inside', 
                 legend_position_inside = (0.93, 0.96),
                 legend_title = pn.element_text(hjust=0.5, face='bold'),
                 panel_grid=pn.element_blank(),
                 legend_key=pn.element_blank(), 
                 plot_title=pn.element_text(face='bold', hjust=0, size=11)) +
        pn.labs(title='Volcano Plot', color='DEG class', x=r'Log$_{2}$FC', y='-Log$_{10}$ padj') + 
        pn.scale_x_continuous(expand=(0.1, 0.15, 0.15, 0.1)) +
        pn.scale_y_continuous(expand=(0.1, 0.1, 0.1, 0.1)) +
        pn.scale_color_manual(values=('seagreen', 'black', 'crimson'))
    )
    fig.show()


def get_groups(genes, targets):
    """
    Gets gene expressions for each gene by target class
    """
    groups_dict = {}
    unique_targets = np.unique(targets)
    for i in unique_targets:
        groups_dict[i] = genes.values[targets == i]
    return groups_dict


def calc_LFC(genes:pd.DataFrame, targets:Union[pd.DataFrame, pd.Series], pos_label:str=None):
    subtract = np.vectorize(lambda x,y: x - y) # calculates log2 fold change
    
    # get group datasets
    gene_names = genes.columns.tolist()
    grouped_data = get_groups(genes, targets)
    groups = list(grouped_data.keys()) # get target class names

    # get genes mean values for each class
    grouped_mean_vals = np.column_stack(
        list(map(lambda x: np.mean(x, axis=0), grouped_data.values()))
    )
    
    grouped_mean_vals = pd.DataFrame(grouped_mean_vals, columns=groups)

    if pos_label:
        pos_label = pos_label.title()
        # sort based on user's target class of interest
        groups = [pos_label] + [i for i in groups if i != pos_label]
    
    # reverse by positive label (label of interest)
    grouped_mean_vals = grouped_mean_vals[groups]

    # stack to calculate Log2 fold change 
    # [[test, control] for all genes] -> length equals number of genes
    grouped_mean_vals = [grouped_mean_vals.iloc[:, i] \
                         for i in range(grouped_mean_vals.shape[1])]
    
    # get log2FC
    LFC = subtract(*grouped_mean_vals)
    return LFC, grouped_data, gene_names


def run_OLS(genes:pd.DataFrame, 
            target:pd.Series, 
            pos_label:Union[str, None]=None) -> np.ndarray:
    
    def run_wald_test(model):
        if hasattr(model, 'wald_test'):
            res = model.wald_test(r_matrix='class=0', scalar=False)
            return res.pvalue

    groups = np.unique(target)
    colnames = genes.columns.tolist()

    # if class of interest, pos_label value is 1, then rearrange groups
    if pos_label and pos_label in groups:
        groups_map = {i:1 if i==pos_label else 0 for i in groups}
        groups = [pos_label] + [i for i in groups if i != pos_label]
    else:
        groups_map = {i:j for i,j in zip(groups, range(len(groups)))}
    
    X = target.map(groups_map).to_frame()
    X['intercept'] = 1 # add intercept
    y = gene_counts.reset_index(drop=True)

    fit_models = np.vectorize(lambda col: sm.GLM(
        y[col], X, family=sm.families.Gaussian()).fit()
    )
    models = fit_models(colnames)
    
    pvals = np.vectorize(run_wald_test)(models)
    assert len(pvals) == len(colnames)
    return pvals


def DGE_analysis(genes, target, pos_label=None, 
                 method:Literal['ttest', 'lm']='ttest'):
    
    LFC, grouped_data, gene_names =  calc_LFC(genes, target, pos_label)
    if method == 'ttest':
        # perform stat test
        if len(grouped_data.keys()) == 2:
            _, pval = stats.ttest_ind(*grouped_data.values())
        else:
            print('Number of groups must be 2')
            exit()
    elif method == 'lm':
        pval = run_OLS(genes, target, pos_label)
    else:
        print(f'{method} not recognised!')
        exit(1)

    _, adj_pval, _, _ = multipletests(pval, method='fdr_bh')
    result = pd.DataFrame(np.c_[LFC, pval, adj_pval], 
                          index=gene_names, 
                          columns=['Log2FC', 'pval', 'padj'])
    
    assert len(result) == len(gene_names)
    result = result.sort_values(['padj', 'Log2FC'], ascending=[True, True])
    return result


# Linear Method

results_lm = DGE_analysis(gene_counts, metadata['class'], pos_label='glioblastoma', method='lm')
results_lm

# selecting statistically differentially expressed genes with 2-fold change
upregulated_genes = results_lm[(results_lm.padj < 0.05) & (results_lm.Log2FC > 2)]
downregulated_genes = results_lm[(results_lm.padj < 0.05) & (results_lm.Log2FC < -2)]

# %%
upregulated_genes.shape, downregulated_genes.shape


# visualise DEGs
plot_volacano(results_lm)
upregulated = upregulated_genes.index.tolist()
downregulated = downregulated_genes.index.tolist()


# saving upregulated and downregulated genes to a file
os.makedirs('DGE', exist_ok=True)

with open('DGE/upregulated.txt', mode='wt') as upreg_genes:
    genes = '\n'.join(upregulated)
    upreg_genes.writelines(genes)

with open('DGE/downregulated.txt', mode='wt') as downreg_genes:
    genes = '\n'.join(downregulated)
    downreg_genes.writelines(genes)


# selecting differentially expressed genes
deg_genes = gene_counts[upregulated + downregulated]
# plot some of the DEGs
plot_distribution(deg_genes, plot_type='box', seed=10)


# T-test method
# T-Test result
results_tt = DGE_analysis(gene_counts, metadata['class'], pos_label='glioblastoma')
results_tt


# selecting statistically differentially expressed genes with 2-fold change
print('Upregulated Genes: ', sum((results_tt.padj < 0.05) & (results_tt.Log2FC > 2)))
print('Downregulated Genes: ', sum((results_tt.padj < 0.05) & (results_tt.Log2FC < -2)))

plot_volacano(results_tt)


# Clustering genes to find similarities and differences

plot_dendrogram(deg_genes[upregulated], axis_name='gene')
plot_dendrogram(deg_genes[downregulated], axis_name='gene')

# upregulated genes
cluster_genes(deg_genes[upregulated], 3, cluster_type='gene', plot=True)
cluster_genes(deg_genes[upregulated], 3, cluster_type='gene', plot=True, reduction_type='umaps')

# downregulated genes
cluster_genes(deg_genes[downregulated], 2, cluster_type='gene', plot=True)
cluster_genes(deg_genes[downregulated], 2, cluster_type='gene', plot=True, reduction_type='umaps')


# library/database names in gseapy
lib_names = pd.Series(gspy.get_library_name(), name='library_names')
print(len(lib_names))


def get_functional_results(gene_list, gene_set, organism='Human', outdir=None, cutoff=None):
    """
    Queries and gets functional annotation of genes in an organism from a given database

    :param gene_list (str, list, pd.DataFrame, np.ndarray): List of genes to query from functional annotation database
    :param gene_set (list, str): string or list of annnotation database to query
    :param organism: Type of organism to query from database
    :param description: Description to describe query 
    :param outdir: Output directory to save query data
    :param cutoff: cutoff for adjusted p-value
    """
    if cutoff:
        result = gspy.enrichr(gene_list=gene_list, gene_sets=gene_set, 
                              organism=organism, cutoff=cutoff, outdir=outdir)
    else:
        result = gspy.enrichr(gene_list=gene_list, gene_sets=gene_set, 
                              organism=organism, outdir=outdir)

    return result


# Get gene IDs of Illumina probes
bm = gspy.Biomart()

# get biomart attributes
f = bm.get_attributes()

with open('DGE/attribute_names.txt', 'wt') as file:
    names = '\n'.join(np.sort(f.Attribute.unique()).tolist())
    file.writelines(names)


# select those with illumina
f[f.Attribute.str.contains('illumina', regex=True, case=False)]


# get gene names of Illumina IDs
def get_gene_ids(gene_list):
    gene_ids1 = bm.query(dataset='hsapiens_gene_ensembl', 
                        attributes=['illumina_humanref_8_v3', 'external_gene_name'], 
                        filters={'illumina_humanref_8_v3': gene_list}
                        ).rename({'illumina_humanref_8_v3':'probe_id'}, axis=1)

    gene_ids2 = bm.query(dataset='hsapiens_gene_ensembl', 
                        attributes=['illumina_humanwg_6_v3', 'external_gene_name'], 
                        filters={'illumina_humanwg_6_v3': gene_list}
                        ).rename({'illumina_humanwg_6_v3' : 'probe_id'}, axis=1)

    gene_ids = pd.concat([gene_ids1, gene_ids2]).dropna().drop_duplicates()
    return gene_ids


def save_annotation_file(annotation_result, filename, folder_name=None, cutoff=0.05):
    """
    Saves result of functional annotation data

    :param annotation_result: Result of annotated data
    :param filename: filename
    :param folder_name: folder name to save file
    :param cutoff: adjusted p-value cutoff 
    """
    if folder_name:
        filepath = os.path.join(path, folder_name, filename+'.csv')
    else:
        filepath = os.path.join(path, filename)

    if hasattr(annotation_result, 'results'):
        result = annotation_result.results

    if cutoff:
        result = result[result['Adjusted P-value'] < cutoff]

    with open(filepath, 'wt') as file:
        csv_writer = csv.writer(file, lineterminator='\r')
        csv_writer.writerow(result.columns.tolist())
        csv_writer.writerows(result.values.tolist())


def plot_figure(annotation_result, title=None):
    fig = gspy.barplot(annotation_result.res2d, title=title)
    plt.yticks(fontsize=9)
    plt.xticks(fontsize=9)
    plt.xlabel(fig.get_xlabel(), fontsize=10)
    plt.title(fig.get_title(), fontweight='bold', fontsize=15);


# get gene ids
gene_ids_up = get_gene_ids(upregulated)
gene_ids_down = get_gene_ids(downregulated)

# save to file
gene_ids_down.to_csv('DGE/downregulated_gene_names.csv', index=False)
gene_ids_up.to_csv('DGE/upregulated_gene_names.csv', index=False)

print('Number of gene names in upregulated genes: {}'.format(
    gene_ids_up.external_gene_name.nunique()))

print('Number of gene names in downregulated genes: {}'.format(
    gene_ids_down.external_gene_name.nunique()))



# Functional Annotation

upregulated_gene_ids = gene_ids_up.external_gene_name.unique().tolist()
downregulated_gene_ids = gene_ids_down.external_gene_name.unique().tolist()

# Biological Processes

enr_GO_upreg = get_functional_results(gene_list=upregulated_gene_ids, 
                                      gene_set='GO_Biological_Process_2023')

enr_GO_downreg = get_functional_results(gene_list=downregulated_gene_ids,
                                        gene_set='GO_Biological_Process_2023')


save_annotation_file(enr_GO_upreg, 'Bio_process_upreg', 'DGE/annotation_result', None)
save_annotation_file(enr_GO_downreg, 'Bio_process_downreg', 'DGE/annotation_result', None)

plot_figure(enr_GO_upreg, title='Upregulated Genes for Biological Processes')

plot_figure(enr_GO_downreg, title='Downregulated Genes for Biological Processes')


# Molecular function

enr_MF_upreg = get_functional_results(gene_list=upregulated_gene_ids, 
                                      gene_set='GO_Molecular_Function_2023')

enr_MF_downreg = get_functional_results(gene_list=downregulated_gene_ids, 
                                        gene_set='GO_Molecular_Function_2023')

save_annotation_file(enr_MF_upreg, 'Molecular_func_upreg', 'DGE/annotation_result', None)
save_annotation_file(enr_MF_downreg, 'Molecular_func_downreg', 'DGE/annotation_result', None)

plot_figure(enr_MF_upreg, title='Upregulated Genes for Molecular Function')
plot_figure(enr_MF_downreg, title='Downregulated Genes for Molecular Function')


# Cellular component

enr_CC_upreg = get_functional_results(gene_list=upregulated_gene_ids, 
                                      gene_set='GO_Cellular_Component_2023')

enr_CC_downreg = get_functional_results(gene_list=downregulated_gene_ids, 
                                        gene_set='GO_Cellular_Component_2023')

save_annotation_file(enr_CC_upreg, 'cellular_component_upreg', 'DGE/annotation_result', None)
save_annotation_file(enr_CC_downreg, 'cellular_component_downreg', 'DGE/annotation_result', None)

plot_figure(enr_CC_upreg, title='Upregulated Genes for Cellular Component')

plot_figure(enr_CC_downreg, title='Downregulated Genes for Cellular Component')


# Pathway Analysis

# KEGG
enr_kegg_upreg = get_functional_results(gene_list=upregulated_gene_ids, 
                                        gene_set='KEGG_2021_Human')

enr_kegg_downreg = get_functional_results(gene_list=downregulated_gene_ids, 
                                          gene_set='KEGG_2021_Human')

save_annotation_file(enr_kegg_upreg, 'kegg_upreg', 'DGE/annotation_result', None)
save_annotation_file(enr_kegg_downreg, 'kegg_downreg', 'DGE/annotation_result', None)

plot_figure(enr_kegg_upreg, title='Upregulated Genes (KEGG Pathway)')
plot_figure(enr_kegg_downreg, title='Downregulated Genes (KEGG Pathway)')

# Reactome

enr_reactome_upreg = get_functional_results(gene_list=upregulated_gene_ids, 
                                            gene_set='Reactome_2022')

enr_reactome_downreg = get_functional_results(gene_list=downregulated_gene_ids, 
                                              gene_set='Reactome_2022')

save_annotation_file(enr_reactome_upreg, 'reactome_upreg', 'DGE/annotation_result', None)
save_annotation_file(enr_reactome_downreg, 'reactome_downreg', 'DGE/annotation_result', None)

plot_figure(enr_reactome_upreg, title='Upregulated Genes (Reactome Pathway)')
plot_figure(enr_reactome_downreg, title='Downregulated Genes (Reactome Pathway)')


