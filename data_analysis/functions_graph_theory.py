import time
import logging
logging.basicConfig(format='%(asctime)s %(message)s')
from joblib import Parallel, delayed
import numpy as np


def epochs_swi(epoch_matrix, n_avg=1, n_iter=1):
    """Calculate the small world index over a range of epochs."""
    n_epochs = epoch_matrix.shape[0]
    n_freqs = epoch_matrix.shape[-1]
    small_worlds = np.zeros([n_epochs, n_freqs])
    for epoch in range(n_epochs):
        for freq in range(n_freqs):
            progress = (epoch / n_epochs + freq / n_freqs / n_epochs) * 100
            logging.warning("Progress: {} %".format(progress))
            print("Progress: {} %".format(progress), flush=True)
            
            cur_mat = remove_self_edges(epoch_matrix[epoch, :, :, freq])
            small_worlds[epoch, freq] = weighted_sw_index(cur_mat, n_avg=n_avg, n_iter=n_iter)
    return small_worlds


def multi_small_world(epoch_matrix, n_jobs=4, n_avg=1, n_iter=1):
    """Calculate the small world coefficient using parallel processing jobs
    for separated epochs."""
    parts = np.linspace(0, len(epoch_matrix), n_jobs + 1, dtype=int)
    results = Parallel(n_jobs=n_jobs)(delayed(epochs_swi)(epoch_matrix[parts[i]:parts[i+1]],
                                                          n_avg=n_avg, n_iter=n_iter) for i in range(n_jobs))
    (delayed(processInput)(i,j) for i,j in zip(a,b))
    return np.concatenate(results, axis=0)


def weighted_shortest_path(matrix):
  """
  Calculate the shortest path lengths between all nodes in a weighted graph.

  This is an implementation of the Floyd-Warshall algorithm for finding the shortest
  path lengths of an entire graph matrix. Implementation taken from:
  https://en.wikipedia.org/wiki/Floyd%E2%80%93Warshall_algorithm

  This implementation is actually identical to scipy.sparse.csgraph.floyd_warshall,
  which we found after the implementation.
  """
  matrix = invert_matrix(matrix)

  n_nodes = len(matrix)
  distances = np.empty([n_nodes, n_nodes])
  for i in range(n_nodes):
    for j in range(n_nodes):
      distances[i,j] = matrix[i, j]
  
  for i in range(n_nodes):
    distances[i,i] = 0

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
    sum_vector[i] = (1/(n_nodes-1)) * np.sum([min_distances[i, j] for j in range(n_nodes) if j != i])

  return (1/n_nodes) * np.sum(sum_vector)


def weighted_node_degree(matrix):
  """Calculate the node degree for all nodes in a weighted graph."""
  return np.sum(matrix, axis=-1)


def unweighted_node_degree(matrix):
  """Calculate the node degree for all nodes in a weighted graph."""
  return np.sum(np.ceil(matrix), axis=-1)


def weighted_triangle_number(matrix):
  """Calculate the weighted geometric mean of triangles around i for all nodes i in a weighted graph."""
  n_nodes = len(matrix)

  mean_vector = np.empty([n_nodes])
  for i in range(n_nodes):
    triangles = np.array([[matrix[i, j] * matrix[i, k] * matrix[j, k] for j in range(n_nodes)] for k in range(n_nodes)])**(1/3)
    mean_vector[i] = (1/2) * np.sum(triangles, axis=(0,1))
  
  return mean_vector


def weighted_clustering_coeff(matrix):
  """Calculate the clustering coefficient for a weighted graph."""
  n = len(matrix)
  t = weighted_triangle_number(matrix)
  k = weighted_node_degree(matrix)  # Here we use the actual weights in the network as a reference
  #k = unweighted_node_degree(matrix) # here we use the !max possible weights as reference
  return (1/n) * np.sum((2 * t)/(k * (k - 1)))


def weighted_clustering_coeff_z(matrix):
  """Calculate the Zhang's CC."""
  n_nodes = len(matrix)
  ccs = []
  for i in range(n_nodes):
    upper = np.sum([[matrix[i,j] * matrix[j,k] * matrix[i,k] for k in range(n_nodes)] for j in range(n_nodes)])
    lower = np.sum([[matrix[i,j] * matrix[i,k] for k in range(n_nodes) if j!=k] for j in range(n_nodes)])
    ccs.append(upper/lower)

  return np.mean(ccs)


def weighted_sw_sigma(matrix, n_avg=1, n_iter=1):
  """Calculate the weighted small world coefficient sigma of a matrix."""
  C = weighted_clustering_coeff(matrix)
  L = weighted_characteristic_path_length(matrix)

  sigmas = []
  for i in range(n_avg):
    random_graph = random_reference(matrix, n_iter=n_iter)
    C_rand = weighted_clustering_coeff(random_graph)
    L_rand = weighted_characteristic_path_length(random_graph)
    sigma = (C/C_rand) / (L/L_rand)
    print("C: {}, Cr: {}, Cl: {}\nL: {}, Lr: {}, Ll: {}\nSigma: {}".format(C, C_rand, C_latt, L, L_rand, L_latt, sigma))
    sigmas.append(sigma)

  return np.mean(sigmas)


def weighted_sw_omega(matrix, n_avg=1, n_iter=1):
  """Calculate the weighted small world coefficient omega of a matrix."""
  C = weighted_clustering_coeff(matrix)
  L = weighted_characteristic_path_length(matrix)
    
  omegas = []
  for i in range(n_avg):
    random_graph = random_reference(matrix, n_iter=n_iter)
    lattice_graph = lattice_reference(matrix, n_iter=n_iter)
    C_latt = weighted_clustering_coeff(lattice_graph)
    L_rand = weighted_characteristic_path_length(random_graph)
    print("C: {}, Cr: {}, Cl: {}\nL: {}, Lr: {}, Ll: {}\nOmega: {}".format(C, C_rand, C_latt, L, L_rand, L_latt, omega))
    omega = (L_rand/L) / (C/C_latt)
    omegas.append(omega)

  return np.mean(omegas)


def weighted_sw_index(matrix, n_avg=1, n_iter=1):
  """Calculate the weighted small world coefficient omega of a matrix."""
  C = weighted_clustering_coeff_z(matrix)
  L = weighted_characteristic_path_length(matrix)
    
  indices = []
  for i in range(n_avg):
    random_graph = random_reference(matrix, n_iter=n_iter)
    lattice_graph = lattice_reference(matrix, n_iter=n_iter)
    C_rand = weighted_clustering_coeff_z(random_graph)
    C_latt = weighted_clustering_coeff_z(lattice_graph)
    L_rand = weighted_characteristic_path_length(random_graph)
    L_latt = weighted_characteristic_path_length(lattice_graph)
    index = ((L - L_latt) / (L_rand - L_latt)) * ((C - C_rand) / (C_latt - C_rand))
    print("C: {}, Cr: {}, Cl: {}\nL: {}, Lr: {}, Ll: {}\nSWI: {}".format(C, C_rand, C_latt, L, L_rand, L_latt, index))
    indices.append(index)
  return np.mean(indices)


def weighted_global_efficiency(matrix):
  """The weighted global efficiency is closely related to the characteristic path length."""
  n_nodes = len(matrix)
  min_distances = weighted_shortest_path(matrix)

  sum_vector = np.empty(n_nodes)
  for i in range(n_nodes):
    # calculate the inner sum
    sum_vector[i] = (1/(n_nodes-1)) * np.sum([1 / min_distances[i, j] for j in range(n_nodes) if j != i])

  return (1/n_nodes) * np.sum(sum_vector)


def weighted_transitivity(matrix):
  """The transitivity is related to the clustering coefficient."""
  
  n = len(matrix)
  t = weighted_triangle_number(matrix)
  #k = weighted_node_degree(matrix)  # Here we use the actual weights in the network as a reference
  k = unweighted_node_degree(matrix) # here we use the !max possible weights as reference
  
  return np.sum(2 * t) / np.sum(k * (k - 1))


def lattice_reference(G, n_iter=1, D=None, seed=np.random.seed(np.random.randint(0, 2**30))):
    """Latticize the given graph by swapping edges.

    Parameters
    ----------
    G : graph
        An undirected graph with 4 or more nodes.

    n_iter : integer (optional, default=1)
        An edge is rewired approximatively n_iter times.

    D : numpy.array (optional, default=None)
        Distance to the diagonal matrix.

    Returns
    -------
    G : graph
        The latticized graph.

    Notes
    -----
    The implementation is adapted from the algorithm by Sporns et al. [1]_.
    which is inspired from the original work by Maslov and Sneppen(2002) [2]_.

    References
    ----------
    .. [1] Sporns, Olaf, and Jonathan D. Zwi.
       "The small world of the cerebral cortex."
       Neuroinformatics 2.2 (2004): 145-162.
    .. [2] Maslov, Sergei, and Kim Sneppen.
       "Specificity and stability in topology of protein networks."
       Science 296.5569 (2002): 910-913.
    """
    from networkx.utils import cumulative_distribution, discrete_sequence

    # Instead of choosing uniformly at random from a generated edge list,
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    G = G.copy()
    #keys, degrees = zip(*G.degree())  # keys, degree
    keys = [i for i in range(len(G))]
    degrees = weighted_node_degree(G)
    cdf = cumulative_distribution(degrees)  # cdf of degree

    nnodes = len(G)
    nedges = nnodes *(nnodes - 1) // 2 # NOTE: assuming full connectivity
    #nedges = nx.number_of_edges(G)
    if D is None:
        D = np.zeros((nnodes, nnodes))
        un = np.arange(1, nnodes)
        um = np.arange(nnodes - 1, 0, -1)
        u = np.append((0,), np.where(un < um, un, um))

        for v in range(int(np.ceil(nnodes / 2))):
            D[nnodes - v - 1, :] = np.append(u[v + 1 :], u[: v + 1])
            D[v, :] = D[nnodes - v - 1, :][::-1]

    n_iter = n_iter * nedges
    ntries = int(nnodes * nedges / (nnodes * (nnodes - 1) / 2))
    swapcount = 0

    for i in range(n_iter):
        n = 0
        while n < ntries:
            # pick two random edges without creating edge list
            # choose source node indices from discrete distribution
            (ai, bi, ci, di) = discrete_sequence(4, cdistribution=cdf, seed=seed)
            if len(set((ai, bi, ci, di))) < 4:
                continue  # picked same node twice
            a = keys[ai]  # convert index to label
            b = keys[bi]
            c = keys[ci]
            d = keys[di]

            is_closer = D[ai, bi] >= D[ci, di]
            is_larger = G[ai, bi] >= G[ci, di]

            if (is_closer and is_larger) or (not is_closer and not is_larger):
                # only swap if we get closer to the diagonal

                ab = G[a, b]
                cd = G[c, d]
                G[a, b] = cd
                G[b, a] = cd
                G[c, d] = ab
                G[d, c] = ab

                swapcount += 1
                break
            n += 1
    return G


def random_reference(G, n_iter=1, D=None, seed=np.random.seed(np.random.randint(0, 2**30))):
    """Latticize the given graph by swapping edges.

    Parameters
    ----------
    G : graph
        An undirected graph with 4 or more nodes.

    n_iter : integer (optional, default=1)
        An edge is rewired approximatively n_iter times.

    D : numpy.array (optional, default=None)
        Distance to the diagonal matrix.

    Returns
    -------
    G : graph
        The latticized graph.

    Notes
    -----
    The implementation is adapted from the algorithm by Sporns et al. [1]_.
    which is inspired from the original work by Maslov and Sneppen(2002) [2]_.

    References
    ----------
    .. [1] Sporns, Olaf, and Jonathan D. Zwi.
       "The small world of the cerebral cortex."
       Neuroinformatics 2.2 (2004): 145-162.
    .. [2] Maslov, Sergei, and Kim Sneppen.
       "Specificity and stability in topology of protein networks."
       Science 296.5569 (2002): 910-913.
    """
    from networkx.utils import cumulative_distribution, discrete_sequence

    # Instead of choosing uniformly at random from a generated edge list,
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    G = G.copy()
    #keys, degrees = zip(*G.degree())  # keys, degree
    keys = [i for i in range(len(G))]
    degrees = weighted_node_degree(G)
    cdf = cumulative_distribution(degrees)  # cdf of degree

    nnodes = len(G)
    nedges = nnodes *(nnodes - 1) // 2 # NOTE: assuming full connectivity
    #nedges = nx.number_of_edges(G)
    if D is None:
        D = np.zeros((nnodes, nnodes))
        un = np.arange(1, nnodes)
        um = np.arange(nnodes - 1, 0, -1)
        u = np.append((0,), np.where(un < um, un, um))

        for v in range(int(np.ceil(nnodes / 2))):
            D[nnodes - v - 1, :] = np.append(u[v + 1 :], u[: v + 1])
            D[v, :] = D[nnodes - v - 1, :][::-1]

    n_iter = n_iter * nedges
    ntries = int(nnodes * nedges / (nnodes * (nnodes - 1) / 2))
    swapcount = 0

    for i in range(n_iter):
        n = 0
        while n < ntries:
            # pick two random edges without creating edge list
            # choose source node indices from discrete distribution
            (ai, bi, ci, di) = discrete_sequence(4, cdistribution=cdf, seed=seed)
            if len(set((ai, bi, ci, di))) < 4:
                continue  # picked same node twice
            a = keys[ai]  # convert index to label
            b = keys[bi]
            c = keys[ci]
            d = keys[di]


            # only swap if we get closer to the diagonal

            ab = G[a, b]
            cd = G[c, d]
            G[a, b] = cd
            G[b, a] = cd
            G[c, d] = ab
            G[d, c] = ab

            swapcount += 1
            break

    return G


def remove_self_edges(matrix):
  """Removes the self-connections of a network graph."""
  matrix = matrix.copy()
  for i in range(len(matrix)):
    matrix[i, i] = 0
  return matrix


def invert_matrix(matrix):
  """Invert a matrix from 0 to 1, dependent on whether dealing with distances or weight strengths."""
  new_matrix = 1 - matrix.copy()
  return remove_self_edges(new_matrix)


