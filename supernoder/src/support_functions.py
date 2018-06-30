import networkx as nx
import random
import datetime

class Utils:
	#See reference [8]	
	@staticmethod
	def ramsey(g):
		if len(g.nodes()) == 0:
			return set([]), set([])
			
		random.shuffle(list(g.nodes()))
		v = list(g.nodes())[0]
		
		neighbors = set(g.neighbors(v))
		#print(v, neighbors)
		noneighbors = (set(g.nodes()) - neighbors) - set([v])
		c1, i1 = Utils.ramsey(g.subgraph(neighbors))
		c2, i2 = Utils.ramsey(g.subgraph(noneighbors))
		
		c1.add(v)
		i2.add(v)
		c = set([])
		i = set([])
		
		if len(c1) >= len(c2):
			c = c1
		else:
			c = c2
			
		if len(i1) >= len(i2):
			i = i1
		else:
			i = i2
		
		return c,i
	
	#See reference [8]	
	@staticmethod
	def clique_removal(g):
		g1 = g.copy()
		index = 1
		c = {}
		i = {}	
		
		c[index], i[index] = Utils.ramsey(g1)
		while len(g1.nodes()) > 0:
			g1.remove_nodes_from(c[index])
			index += 1
			c[index], i[index] = Utils.ramsey(g1) 
			
		max_mis = set([])
		for key in i:
			if len(i[key]) > len(max_mis):
				max_mis = i[key]
		return max_mis, c
		
	@staticmethod	
	def enumerate_motifs(g,k):
		vext = []
		motifs = set()
		
		for node in sorted(g.nodes()):   # For each vertex , make a list of its neighbours
			neighbors = sorted(g.neighbors(node))
			
			neighbors_tmp = []
			for neighbor in neighbors:
				if neighbor > node:
					neighbors_tmp.append(neighbor)
			
			while len(neighbors_tmp) > 0: 

				vext = list(sorted(neighbors_tmp))
				Utils.extend_motif([node],vext,k,g,motifs)
				
				if neighbors_tmp:
					neighbors_tmp.pop(0)
		
		return motifs
	@staticmethod
	def extend_motif(vsub, vextension, k, g, realsub):
		
		if len(vsub) == int(k):
			vsub_ordered =  sorted(vsub, key=lambda x: int(x))
			t_vsub = tuple(vsub_ordered)
			realsub.add(t_vsub)
			return	
		
		while len(vextension) > 0:
			
			ele = vextension.pop(0)
			vextension_first = vextension[:]
			
			for n in sorted(g.neighbors(ele)):
				if Utils.nexclusive(g,n,vsub) and n not in vextension_first and n > vsub[0]:
					vextension_first.append(n)
			
			if ele not in vsub:
				vsub.append(ele)
			Utils.extend_motif(vsub,vextension_first,k,g,realsub)
			if ele in vsub:
				vsub = vsub[:-1]
			
	@staticmethod		
	def nexclusive (g, n, vsub):
		for e in vsub:
			if n in g.neighbors(e):
				return False
		return True