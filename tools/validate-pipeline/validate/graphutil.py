from collections import defaultdict

# Tarjan's SCC algorithm
# https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm
# modified from: https://rosettacode.org/wiki/Tarjan#Python:_As_function
def from_edges(edges):
    '''translate list of edges to list of nodes'''
 
    class Node:
        def __init__(self):
            # root is one of:
            #   None: not yet visited
            #   -1: already processed
            #   non-negative integer: what Wikipedia pseudo code calls 'lowlink'
            self.root = None
            self.succ = []
 
    nodes = defaultdict(Node)
    for v,w in edges:
        nodes[v].succ.append(nodes[w])
 
    for i,v in nodes.items(): # name the nodes for final output
        v.id = i
 
    return nodes
 
def tarjan(V):
    def strongconnect(v, S):
        v.root = pos = len(S)
        S.append(v)
 
        for w in v.succ:
            if w.root is None:  # not yet visited
                yield from strongconnect(w, S)
 
            if w.root >= 0:  # still on stack
                v.root = min(v.root, w.root)
 
        if v.root == pos:  # v is the root, return everything above
            res, S[pos:] = S[pos:], []
            for w in res:
                w.root = -1
            yield [r.id for r in res]
 
    for v in V.values():
        if v.root is None:
            yield from strongconnect(v, [])

# BFS for testing reachability
def bfs(graph, root):
    visited = []
    queue = []

    visited.append(root)
    queue.append(root)

    while queue:
        s = queue.pop(0)
        
        for successor in graph[s].succ:
            if successor.id not in visited:
                visited.append(successor.id)
                queue.append(successor.id)
    
    return visited