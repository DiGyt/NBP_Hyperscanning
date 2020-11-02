import time
import logging
logging.basicConfig(format='%(asctime)s %(message)s')

import numpy as np
import networkx as nx

def epochs_swi(epoch_matrix):
    n_epochs = epoch_matrix.shape[0]
    n_freqs = epoch_matrix.shape[-1]
    small_worlds = np.zeros([n_epochs, n_freqs])
    for epoch in range(n_epochs):
        for freq in range(n_freqs):
            progress = (epoch / n_epochs + freq / n_freqs / n_epochs) * 100
            logging.warning("Progress: {} %".format(progress))
            print("Progress: {} %".format(progress), flush=True)
            
            small_worlds[epoch, freq] = core_swi(epoch_matrix[epoch, :, :, freq], nrand=5)
            
    return small_worlds


def core_swi(graph_matrix, nrand=10):
    
    # create an graph from the matrix
    graph = nx.convert_matrix.from_numpy_array(graph_matrix)
    
    # create a container for the later small world references
    small_worlds = []
    for i in range(nrand):
        rand_ref = nx.random_reference(graph, connectivity=True, seed=None)
        latt_ref= nx.lattice_reference(graph, niter=1,D=None, connectivity=True, seed=None)
        
        # create all metrics: CPL&CC for observed/random/lattice
        CPL = nx.average_shortest_path_length(graph, weight=None, method=None)
        CPL_R = nx.average_shortest_path_length(rand_ref, weight=None, method=None)
        CPL_L = nx.average_shortest_path_length(latt_ref, weight=None, method=None)
        CC = nx.average_clustering(graph)
        CC_R = nx.average_clustering(rand_ref)
        CC_L = nx.average_clustering(latt_ref)
        
        # calculate SWI
        SWI = ( (CPL - CPL_L) / (CPL_R - CPL_L) )   *   ( (CC - CC_R) / (CC_L - CC_R) )
        small_worlds.append(SWI)
        
    return np.mean(small_worlds)


from joblib import Parallel, delayed
def multi_small_world(epoch_matrix, n_jobs=4):
    """Calculate the small world coefficient using parallel processing jobs
    for separated epochs."""
    parts = np.linspace(0, len(epoch_matrix), n_jobs + 1, dtype=int)
    results = Parallel(n_jobs=n_jobs)(delayed(epochs_swi)(epoch_matrix[parts[i]:parts[i+1]]) for i in range(n_jobs))
    return np.concatenate(results, axis=0)

# Since we decided to rely on networkx, we won't have to use the rest of the functions
######################################################################################   

'''
from multiprocessing import Pool
def multi_small_world(epoch_matrix, n_jobs=4):
    """Calculate the small world coefficient using parallel processing jobs
    for separated epochs."""
    parts = np.linspace(0, len(epoch_matrix), n_jobs + 1, dtype=int)
    cuts = [epoch_matrix[parts[i]:parts[i+1]] for i in range(n_jobs)]
    with Pool(n_jobs) as pool:
        results = pool.map(epochs_small_world, cuts)
    return np.concatenate(results, axis=0)   

'''
def epochs_small_world(epoch_matrix):
    """Takes a time-frequency epoched connectivity matrix of shape
    [epochs, channels, channels, frequencies] and returns a matrix
    of small worldnesses over the epochs and frequency axes."""
    n_epochs = epoch_matrix.shape[0]
    n_freqs = epoch_matrix.shape[-1]
    omegas = np.zeros([n_epochs, n_freqs])
    for epoch in range(n_epochs):
        for freq in range(n_freqs):
            # monitor progress
            progress = (epoch / n_epochs + freq / n_freqs / n_epochs) * 100
            logging.warning("Progress: {} %".format(progress))
            print("Progress: {} %".format(progress), flush=True)
            
            graph = nx.convert_matrix.from_numpy_array(epoch_matrix[epoch, :, :, freq])
            time.sleep(0.1) # give the CPU rest and prevent it from freezing
            omegas[epoch, freq] = nx.algorithms.smallworld.omega(graph, nrand=5)
            
            time.sleep(0.2) # give the CPU rest and prevent it from freezing
                
    return 1 - np.abs(omegas)

    
def weighted_shortest_path(matrix):
    """
    Calculate the shortest path lengths between all nodes in a weighted graph.

    This is an implementation of the Floyd-Warshall algorithm for finding the shortest
    path lengths of an entire graph matrix. Implementation taken from:
    https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm
    """
    inverse_mapping = np.max(matrix) - matrix

    n_nodes = len(matrix)
    distances = np.empty([n_nodes, n_nodes])
    for i in range(n_nodes):
        for j in range(n_nodes):
            distances[i, j] = inverse_mapping[i, j]

    # not sure if we even need this, since the coherences of [i,i] are always 1 and therefore 0 in the inverse mapping
    # for i in range(n_nodes):
    #  distances[i,i] = 0

    for k in range(n_nodes):
        for i in range(n_nodes):
            for j in range(n_nodes):
                if distances[i, j] > distances[i, k] + distances[k, j]:
                    distances[i, j] = distances[i, k] + distances[k, j]

    return distances


def weighted_characteristic_path_length(matrix):
    """Calculate the characteristic path length for weighted graphs."""
    n_nodes = len(matrix)
    min_distances = weighted_shortest_path(matrix)

    sum_vector = np.empty(n_nodes)
    for i in range(n_nodes):
        # calculate the inner sum
        sum_vector[i] = (1 / (n_nodes - 1)) * np.sum([min_distances[i, j] for j in range(n_nodes) if j != i])

    return (1 / n_nodes) * np.sum(sum_vector)


def weighted_node_degree(matrix):
    """Calculate the node degree for all nodes in a weighted graph."""
    return np.sum(matrix, axis=-1)


def weighted_triangle_number(matrix):
    """Calculate the weighted geometric mean of triangles around i for all nodes i in a weighted graph."""
    n_nodes = len(matrix)

    mean_vector = np.empty([n_nodes])
    for i in range(n_nodes):
        triangles = np.array(
            [[matrix[i, j] * matrix[i, h] * matrix[j, h] for j in range(n_nodes)] for h in range(n_nodes)]) ** (1 / 3)
        mean_vector[i] = (1 / 2) * np.sum(triangles, axis=(0, 1))

    return mean_vector


def weighted_clustering_coeff(matrix):
    """Calculate the clustering coefficient for a weighted graph."""
    n = len(matrix)
    t = weighted_triangle_number(matrix)
    k = weighted_node_degree(
        matrix)  # FIXME: k is denoted by rubinov to be the non weighted k. Can this be right? How to measure non weighted k for weighted graphs?

    return (1 / n) * np.sum((2 * t) / (k * (k - 1)))


def weighted_small_world_coeff(matrix):
    """Calculate the weighted small world coefficient of a matrix."""
    n_nodes = len(matrix)
    random_graph = np.random.rand(n_nodes, n_nodes)  # uniform random from [0 to 1]
    C = weighted_clustering_coeff(matrix)
    C_rand = weighted_clustering_coeff(random_graph)
    L = weighted_characteristic_path_length(matrix)
    L_rand = weighted_characteristic_path_length(random_graph)

    return (C / C_rand) / (L / L_rand)


def epochs_weighted_small_world_coeff(epoch_matrix):
    """Calculate the weighted small world coeff. of a epoched connectivity matrix.
    The epoch_matrix must be of shape (n_epochs, n_chans, n_chans, n_freqs)"""
    n_epochs = epoch_matrix.shape[0]
    n_freqs = epoch_matrix.shape[-1]
    small_world_coeffs = np.empty((n_epochs, n_freqs))
    
    # calculate the small worldedness for each epoch and frequency.
    for ep_idx in range(n_epochs):
        for freq_idx in range(n_freqs):
            cur_mat = epoch_matrix[ep_idx, :, :, freq_idx]
            small_world_coeffs[ep_idx, freq_idx] = weighted_small_world_coeff(cur_mat)
    
    return small_world_coeffs


# Other graph measures
def weighted_global_efficiency(matrix):
    """The weighted global efficiency is closely related to the characteristic path length."""
    n_nodes = len(matrix)
    inverse_min_distances = weighted_shortest_path(matrix)

    sum_vector = np.empty(n_nodes)
    for i in range(n_nodes):
        # calculate the inner sum
        sum_vector[i] = (1 / (n_nodes - 1)) * np.sum(
            [1 / inverse_min_distances[i, j] for j in range(n_nodes) if j != i])

    return (1 / n_nodes) * np.sum(sum_vector)


def weighted_transitivity(matrix):
    """The transitivity is related to the clustering coefficient."""

    t = weighted_triangle_number(matrix)
    k = weighted_node_degree(
        matrix)  # FIXME: k is denoted by rubinov to be the non weighted k. Can this be right? How to measure non weighted k for weighted graphs?

    return np.sum(2 * t) / np.sum(k * (k - 1))
