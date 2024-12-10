from typing import Literal, Union, Optional
from tqdm import tqdm
import pandas as pd
import plotnine as pn
from sklearn import preprocessing as sk_preprocess, cluster, metrics
from sklearn.decomposition import PCA
import umap

# Dimensionality Reduction and Visualisation
def reduce_dimensions(df:pd.DataFrame, 
                      n_components:Union[int,float]=2, 
                      reduction_type:Literal['pca', 'umaps']='pca'):
    try:
        X_scaled = sk_preprocess.scale(df, axis=0)
        
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
                legend_position_inside=(0.01, 0.96) #(0.88, 0.96)
                ) +
        pn.ggtitle(f"{reduction_type.replace('s', '').upper()} Dimensionality Reduction") +
        pn.scale_x_continuous(expand=(0.1, 0.15, 0.15, 0.1)) +
        pn.scale_y_continuous(expand=(0.1, 0.1, 0.1, 0.1)) 
    )
    if reduction_type == 'umaps':
        fig = fig + pn.labs(x='UMAP0', y='UMAP1')

    return(fig)
    #fig.show()
