import numpy as np


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
