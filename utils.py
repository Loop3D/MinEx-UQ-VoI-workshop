import igraph as ig
import numpy as np

node_decision_shape = "rectangle"
node_decision_color = "yellow"
node_event_shape = "circle"
node_event_color = "green"
node_end_shape = "rectangle"
node_end_color = "white"


def plot_decision_tree(g):   
    # g is a graph and it shall contain the following attributes :
    # vertices attributes: name, EV, vshape, vcolor
    # edges attributes: name, probability, val
    ne = len(g.es["probability"])
    lbl_array = (np.vstack((
        np.asarray(ne*['p = ']),np.asarray(g.es["probability"]),np.asarray(ne*['\n ']),np.asarray(g.es["name"]),np.asarray(ne*['\n val = ']),np.asarray(g.es["value"])))).T
    
    lbl_e = ne*['p = ']
    for i in range(ne):
        lbl_e[i] = lbl_array[i,0] + str(lbl_array[i,1]) + lbl_array[i,2]+ lbl_array[i,3]+ lbl_array[i,4] + str(lbl_array[i,5])
    
    nv = len(g.vs["EV"])
    
    lbl_array = (np.vstack((
        np.asarray(g.vs["name"]),np.asarray(nv*['\n EV: ']),np.asarray(g.vs["EV"])))).T
    
    lbl_v = nv*['p = ']
    for i in range(nv):
        lbl_v[i] = lbl_array[i,0] + lbl_array[i,1] + str(lbl_array[i,2])
    
    g.vs["shape"] = g.vs["vshape"]
    g.vs["color"] = g.vs["vcolor"]
    g.vs["label"] = lbl_v
    g.es["label"] = lbl_e
    return ig.plot(g,layout="rt",bbox=(0, 0, 1000, 600),margin=50,vertex_size=36)

def compute_EV(g,verb=False):
    print("***********************")
    print('compute_EV()')
    print("***********************")
    print('computing all the paths from the tree root')
    all_paths_from_root = g.get_shortest_paths(0, output="vpath")
    npaths = len(all_paths_from_root)
    if verb: print(all_paths_from_root)
    if verb: print(str(npaths)+' paths') 
    
    # For each end node/vertex, compute the cumulative sum of the values along the edges as Expected Value of the project
    print('retrieving leaves')

    # Find the leaves of the tree
    list_of_types = ["end"]
    res=g.vs.select(type_in=list_of_types)
    nres = len(res)
    vs_end_idx = res.indices
    
    # For each leave, find the shortest path to the root and sum the edges values to get the expected value at the leaf
    print('computing EV at leaves')
    for i in vs_end_idx: # [9]:#
        cur_val = 0
        path = g.get_shortest_paths(0, to=i, output="vpath")[0]
        lpath = len(path)
        for j in range(lpath-1):
            cur_es = g.es.select(_source=path[lpath-(j+2)], _target=path[lpath-(j+1)])[0]
            cur_val += cur_es["value"]
        g.vs[i]["EV"]=cur_val
        if verb: 
            print(path)
            print(g.vs[i])
            print(cur_val)# Find paths not containing leaves
    
    print('computing EV at other nodes')
    # Keep path that do not contain the leaves to compute expecte value backward on remaining nodes
    paths_2_keep = []
    for i in range(npaths):
        if set(all_paths_from_root[npaths-i-1]).isdisjoint(set(vs_end_idx)): paths_2_keep.append(all_paths_from_root[npaths-i-1])
        
    # print(all_paths_from_root)
    # print(paths_2_keep)
    # Find nodes on which to compute EV (last node of kept path, and order them from longest path to shortest path)
    vs_4_EV = np.zeros(len(paths_2_keep)).astype(int)
    for i in range(len(paths_2_keep)):
        vs_4_EV[i]=paths_2_keep[i][-1]
    if verb: print("vs_4_EV: "+str(vs_4_EV))
    
    # Compute EV
    for i in vs_4_EV: 
        cur_EV = 0
        # find downstream branch and nodes
        edges_downstream = g.es.select(_source=i)
        ned = len(edges_downstream)
        for j in range(ned):
            if verb: print("p="+str(edges_downstream[j]["probability"])+" target="+str(edges_downstream[j].target)+" value="+str(g.vs[edges_downstream[j].target]["EV"]))
            cur_EV+=edges_downstream[j]["probability"]*g.vs[edges_downstream[j].target]["EV"]
        g.vs[i]["EV"]=cur_EV
        if verb: print('vs index: ' +str(i)+" cur_EV="+str(cur_EV))
    print('finished')
    return g

def create_tree(root_name):
    tree = ig.Graph(directed=True)
    tree.add_vertices(1, attributes={"name":"0","type":"decision","EV":np.nan,"vshape":node_decision_shape,"vcolor":node_decision_color})
    return tree

def add_node_and_branch(tree,node_name,parent_name,ntype="end",branch_name="abandon",probability=0,value_gained=0):
    if ntype == "decision":
        vshape = node_decision_shape
        vcolor = node_decision_color
    elif ntype == "event":
        vshape = node_event_shape
        vcolor = node_event_color
    else:
        vshape = node_end_shape
        vcolor = node_end_color       
    tree.add_vertices(1, attributes={"name":node_name,"type":ntype,"EV":np.nan,"vshape":vshape,"vcolor":vcolor})
    tree.add_edges([(parent_name,node_name)], attributes={"name":branch_name, "probability":probability, "value":value_gained})
    return
    
# # Find the leaves of the tree
# list_of_types = ["end"]
# res=tree.vs.select(type_in=list_of_types)
# nres = len(res)
# vs_end_idx = res.indices

# # tree.vs[2].degree()
# print(tree.vs.select(_degree=1).indices)
# print(vs_end_idx)