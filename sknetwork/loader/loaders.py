#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on November 15, 2019
@author: Quentin Lutz <qlutz@enst.fr>
This module's code is freely adapted from TorchKGE's torchkge.data.DataLoader.py code.
"""

from os import environ, makedirs, remove
from os.path import exists, expanduser, join
from urllib.request import urlretrieve
from typing import Optional

from sknetwork.loader import parse_tsv, parse_labels, parse_hierarchical_labels

import shutil
import zipfile


def get_data_home(data_home: Optional[str] = None):
    """
    Returns a path to a storage folder depending on the dedicated environment variable and user input.

    Parameters
    ----------
    data_home: str
        The folder to be used for dataset storage
    """
    if data_home is None:
        data_home = environ.get('SCIKIT_NETWORK_DATA',
                                join('~', 'scikit_network_data'))
    data_home = expanduser(data_home)
    if not exists(data_home):
        makedirs(data_home)
    return data_home


def clear_data_home(data_home: Optional[str] = None):
    """
    Clears a storage folder depending on the dedicated environment variable and user input.

    Parameters
    ----------
    data_home: str
        The folder to be used for dataset storage
    """
    data_home = get_data_home(data_home)
    shutil.rmtree(data_home)


def load_vital_wikipedia(data_home: Optional[str] = None, outputs: str = 'both', return_titles: bool = False,
                         return_labels: bool = False, return_labels_true: bool = False, max_depth: int = 1):
    """
    Returns a path to a storage folder depending on the dedicated environment variable and user input.

    Parameters
    ----------
    data_home: str
        The folder to be used for dataset storage
    outputs: str
        Defines what should be returned. Possible options are 'adjacency' for the adjacency of hyperlinks of the various
        Wikipedia articles, 'biadjacency' for the count matrix of the stems or 'both' for both.
    return_titles: bool
        Denotes if the titles of the articles should be returned
    return_labels: bool
        Denotes if the titles  of the articles and the stems should be returned
    return_labels_true: bool
        Denotes if the categories of the articles should be returned
    max_depth: int
        Denotes the maximum depth to use for the categories

    Returns
    -------
    output:
        A subset of the following, depending on the parameters that have been passed: [adjacency], [biadjacency],
        [article_titles], [stems], [categories].

    """
    if data_home is None:
        data_home = get_data_home()
    data_path = data_home + '/vital_wikipedia'
    if not exists(data_path):
        makedirs(data_path, exist_ok=True)
        urlretrieve("https://graphs.telecom-paristech.fr/datasets/vital_wikipedia.zip",
                    data_home + '/vital_wikipedia.zip')
        with zipfile.ZipFile(data_home + '/vital_wikipedia.zip', 'r') as zip_ref:
            zip_ref.extractall(data_home)
        remove(data_home + '/vital_wikipedia.zip')

    if outputs == 'adjacency':
        output = [parse_tsv(data_path + '/en-internal-links.txt', reindex=False)]
    elif outputs == 'biadjacency':
        output = [parse_tsv(data_path + '/en-articles-stems.txt', bipartite=True, reindex=False)]
    elif outputs == 'both':
        output = [parse_tsv(data_path + '/en-internal-links.txt', reindex=False),
                  parse_tsv(data_path + '/en-articles-stems.txt', bipartite=True, reindex=False)]
    else:
        raise ValueError("Outputs must be 'adjacency', 'biadjacency' or 'both'.")

    if return_labels:
        output.append(parse_labels(data_path + '/en-articles.txt'))
        output.append(parse_labels(data_path + '/en-stems.txt'))
    elif return_titles:
        output.append(parse_labels(data_path + '/en-articles.txt'))
    if return_labels_true:
        output.append(parse_hierarchical_labels(data_path + '/en-categories.txt', max_depth))

    return tuple(output)