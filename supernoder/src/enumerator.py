import networkx as nx

class Enumerator:
	def __init__(self, g, k):
		self.vext = []
		self.motifs = set()
		self.g = g.to_undirected()
		self.k = k
	
	def __enumerate_motifs(self):
		for node in sorted([int(x) for x in self.g.nodes()]):   # For each vertex , make a list of its neighbours
			neighbors = sorted(self.g.neighbors(str(node)))
			
			neighbors_tmp = []
			for neighbor in neighbors:
				if int(neighbor) > node:
					neighbors_tmp.append(int(neighbor))
			
			while len(neighbors_tmp) > 0:
				self.vext = list(sorted(neighbors_tmp))
				self.__extend_motif([node])
				
				if neighbors_tmp:
					neighbors_tmp.pop(0)
					
	def __extend_motif(self, vsub):
		if len(vsub) == int(self.k):
			vsub_ordered =  sorted(vsub, key=lambda x: int(x))
			t_vsub = tuple(vsub_ordered)
			self.motifs.add(t_vsub)
			return	
		
		while len(self.vext) > 0:
			
			ele = self.vext.pop(0)
			vextension_first = self.vext[:]
			
			for n in sorted(self.g.neighbors(str(ele))):
				if self.__nexclusive(n,vsub) and n not in vextension_first and int(n) > vsub[0]:
					vextension_first.append(n)
					
			if ele not in vsub:
				vsub.append(ele)
			self.__extend_motif(vsub)
			if ele in vsub:
				vsub = vsub[:-1]
				
	def __nexclusive (self, n, vsub):
		#print(n, type(n), self.g.nodes())
		
		for e in vsub:
			if n in self.g.neighbors(str(e)):
				return False
		return True

	def run(self):
		self.__enumerate_motifs()
		
	def get_motifs(self):
		return self.motifs
		
		