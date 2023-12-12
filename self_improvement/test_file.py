from typing import List, Tuple

def miller_rabin(n: int, k: int=5) -> bool:
    """
    An implementation of the Miller-Rabin primality test.

    This is an improved Monte Carlo algorithm that determines whether
    a given number is prime with high probability. The accuracy can be
    adjusted with the parameter `k`.

    Parameters:
    n (int): The number to be tested for primality.
    k (int, optional): The number of iterations to perform. Default is 5.

    Returns:
    bool: True if `n` is probably prime, otherwise False.
    """
    from random import randrange
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    r, d = (0, n - 1)
    while d % 2 == 0:
        r += 1
        d //= 2

def check_composite(a: int, s: int, d: int, n: int) -> bool:
    x = pow(a, d, n)
    if x == 1 or x == n - 1:
        return False
    for _ in range(s):
        x = pow(x, 2, n)
        if x == n - 1:
            return False
    return True
    for _ in range(k):
        a = randrange(2, n - 1)
        if check_composite(a, r, d, n):
            return False
    return True

def all_even_degrees(graph):
    """
    Check if all vertices in the graph have even degree.

    Parameters:
    graph (defaultdict[deque]): The graph represented as an adjacency list.
    
    Returns:
    bool: True if all vertices have even degree, False otherwise.
    """
    return all((len(neighbors) % 2 == 0 for neighbors in graph.values()))

def is_connected(graph, n):
    """
    Check if the graph is connected. For the current purpose, we ensure all vertices are reached from
    a starting vertex using DFS.

    Parameters:
    graph (defaultdict[deque]): The graph represented as an adjacency list.
    n (int): Number of vertices in the graph.

    Returns:
    bool: True if the graph is connected, False otherwise.
    """
    visited = set()

def dfs(v):
    visited.add(v)
    for neighbor in graph[v]:
        if neighbor not in visited:
            dfs(neighbor)
    dfs(next(iter(graph)))
    return len(visited) == n

def advanced_cycle_detection(n: int, edges: List[Tuple[int, int, int]]) -> List[List[int]]:
    """
    Implement Hierholzer's algorithm for Eulerian circuits which can be adapted to find other cycles.
    
    This algorithm assumes the graph has an Eulerian circuit. For the current problem, we make sure to check the graph
    is connected and all the vertices have even degrees (for undirected graph).

    Parameters:
    n (int): Number of vertices in the graph.
    edges (List[Tuple[int, int, int]]): The edges in the graph, each with a weight.

    Returns:
    List[List[int]]: A list of paths, which represent Eulerian circuits if the graph satisfies the criteria.
    """
    from collections import defaultdict, deque
    graph = defaultdict(deque)
    for u, v, _ in edges:
        graph[u].append(v)
        graph[v].append(u)

def find_eulerian_circuit(start):
    circuit = []
    stack = [start]
    while stack:
        u = stack[-1]
        if graph[u]:
            next_vertex = graph[u].pop()
            graph[next_vertex].remove(u)
            stack.append(next_vertex)
        else:
            stack.pop()
            circuit.append(u)
    return circuit[::-1]
    start_vertex = next((v for v in graph if graph[v]), None)
    if start_vertex is None:
        return []
    if not is_connected(graph, n) or not all_even_degrees(graph):
        return []
    return [find_eulerian_circuit(start_vertex)]
def strongconnect(node, graph):
    index[node] = index_counter[0]
    lowlinks[node] = index_counter[0]
    index_counter[0] += 1
    stack.append(node)
    try:
        for neighbor in graph[node]:
            if neighbor not in lowlinks:
                strongconnect(neighbor, graph)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in stack:
                lowlinks[node] = min(lowlinks[node], index[neighbor])
        if lowlinks[node] == index[node]:
            connected_component = []
            while True:
                successor = stack.pop()
                connected_component.append(successor)
                if successor == node:
                    break
            component = sorted(connected_component)
            if len(component) > 1:
                result.append(component)
    except KeyError:
        pass
    graph = defaultdict(list)
    for u, v, w in edges:
        graph[u].append(v)
    for i in range(1, n + 1):
        if i not in lowlinks:
            strongconnect(i, graph)
    return result

def stress_test(prime_cycle_detection_func):
    """
    Perform stress tests on the prime_cycle_detection function.
    
    Parameters:
    prime_cycle_detection_func (Callable): The prime cycle detection function to be tested.
    """
    graph_sizes = [10, 100, 500, 1000]
    num_trials = 5
    for size in graph_sizes:
        times = []
        for trial in range(num_trials):
            edges = generate_random_graph(size, size * 3)
            start_time = timer()
            has_cycle = prime_cycle_detection_func(size, edges)
            end_time = timer()
            times.append(end_time - start_time)
            print(f"Trial {trial + 1} for graph size {size}: {('Has' if has_cycle else 'No')} prime cycle, Time taken: {times[-1]:.4f}s")
        avg_time = sum(times) / len(times)
        print(f'Average time for graph size {size}: {avg_time:.4f}s\n')

def generate_random_graph(num_vertices: int, num_edges: int) -> List[Tuple[int, int, int]]:
    """
    Generate a random graph represented as an edge list.

    Parameters:
    num_vertices (int): The number of vertices in the graph.
    num_edges (int): The number of edges in the graph.

    Returns:
    A list of edges where each edge is represented as a tuple (u, v, w).
    """
    from random import randint
    edges = []
    for _ in range(num_edges):
        u = randint(1, num_vertices)
        v = randint(1, num_vertices)
        w = randint(1, 100)
        edges.append((u, v, w))
    return edges
def add_parallel_processing():
    """
    Add parallel processing to the cycle detection algorithm to improve performance.
    """
    from multiprocessing import Pool
    from itertools import product, starmap

def worker(u, graph):
    """
        Worker function for multiprocessing that runs the DFS from vertex u.
        This function will run in pool of processes for parallelism.
        
        Parameters:
        u (int): The start vertex for DFS.
        graph (defaultdict): The adjacency list representation of the graph.
        
        Returns:
        list: List of cycles starting from vertex u.
        """
    cycles = []
    stack = []
    visited = set()

def dfs(start, current, graph, visited, path, prime_cycles):
    """
    Depth-first search algorithm for detecting cycles in an undirected graph.
    Updates prime_cycles with cycles found that begin at the start node.

    Parameters:
    start (int): The starting node for searching cycles.
    current (int): The current node in DFS traversal.
    graph (defaultdict[list]): Graph represented as an adjacency list.
    visited (set): Set of visited nodes.
    path (list): Current path of nodes visited.
    prime_cycles (list): List to store found prime cycles.
    """
    path.append(current)
    visited.add(current)
    for neighbor in graph[current]:
        if neighbor == start and len(path) > 2:
            prime_cycles.append(path + [start])
        elif neighbor not in visited:
            dfs(start, neighbor, graph, visited, path.copy(), prime_cycles)
    path.pop()
    visited.remove(current)
def find_cycles_parallel(n, edges):
    """
        Main function to detect all cycles in the graph using parallel DFS.
        
        Parameters:
        n (int): The number of vertices in the graph.
        edges (List[Tuple[int, int, int]]): The edge list of the graph.
        
        Returns:
        List[Tuple]: List of all cycles found in the graph.
        """
    graph = defaultdict(list)
    for u, v, _ in edges:
        graph[u].append(v)
        graph[v].append(u)
    cycle_set = set()
    with Pool() as pool:
        results = pool.starmap(worker, product(range(1, n + 1), [graph]))
    for result in results:
        for cycle in result:
            if len(cycle) > 2:
                normalized_cycle = tuple(sorted(cycle))
                cycle_set.add(normalized_cycle)
    return list(cycle_set)
def has_prime_cycle(n: int, edges: List[Tuple[int, int, int]]) -> bool:
    """
    Check if the undirected graph has a cycle such that the sum of the weights
    of the edges in the cycle is a prime number using the Miller-Rabin test.

    Parameters:
    n (int): The number of vertices in the graph.
    edges (List[Tuple[int, int, int]]): The edge list of the graph.

    Returns:
    True if there is a prime cycle, False otherwise.
    """
    from collections import defaultdict
    graph = defaultdict(list)
    for u, v, _ in edges:
        graph[u].append(v)
        graph[v].append(u)
    prime_cycles = []
    for start in range(1, n + 1):
        visited = set()
        dfs(start, start, graph, visited, [], prime_cycles)
    weight_map = {(min(u, v), max(u, v)): w for u, v, w in edges}
    for cycle in prime_cycles:
        cycle_weight_sum = sum((weight_map[min(cycle[i], cycle[(i + 1) % len(cycle)]), max(cycle[i], cycle[(i + 1) % len(cycle)])] for i in range(len(cycle))))
        if miller_rabin(cycle_weight_sum):
            return True
    return False
def comment_code_for_readability():
    """
    Add comments to the existing code for improved readability and understanding.
    Placeholder function, no implementation yet.
    """
    pass
def optimize_is_prime(number: int) -> bool:
    """
    Optimize the prime number checking mechanism for larger integers utilizing 6k+-1 optimization.
    Placeholder function, no implementation yet.
    """
    pass
def test_has_prime_cycle():
    """
    Test the prime cycle detection with predefined graph configurations.
    Placeholder function, no implementation yet.
    """
    pass
def optimize_is_prime(number: int) -> bool:
    """Optimized check if a number is a prime number for larger integers."""
    if number < 2:
        return False
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
    return True

def dfs(current, path, graph, start, visited):
    visited.add(current)
    path.append(current)
    for neighbor in graph[current]:
        if neighbor == start and len(path) > 2:
            yield path[:]
        elif neighbor not in visited:
            yield from dfs(neighbor, path, graph, start, visited)
    path.pop()
    visited.remove(current)
def is_prime(number: int) -> bool:
    """
    Check if a number is a prime number using 6k+-1 optimization.
    
    Parameters:
    number (int): The number to check for primality.
    
    Returns:
    True if number is prime, otherwise False.
    """
    if number <= 1:
        return False
    if number <= 3:
        return True
    if number % 2 == 0 or number % 3 == 0:
        return False
    i = 5
    while i * i <= number:
        if number % i == 0 or number % (i + 2) == 0:
            return False
        i += 6
    return True
