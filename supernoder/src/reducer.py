from support_functions import *

class Reducer:
	def __init__(self, g, motifs, th, type):
		self.g = g
		self.reduced_g = self.g.copy()
		self.motifs = motifs
		self.th = th
		self.motif2label = {}
		self.type = type
		self.supernode2composition = {}
		
	def __do_motif2label(self):		
		for motif in self.motifs:
			labels = sorted([self.g.nodes[x]['label'] for x in motif])
			self.motif2label[motif] = '-'.join(labels)
	
	def __substitution(self):
		last_id = max(map(int, list(self.g.nodes())))
		for motif in self.motifs:
			last_id += 1
			self.supernode2composition[str(last_id)] = motif
			self.reduced_g.add_node(str(last_id))
			self.reduced_g.nodes[str(last_id)]['label'] = self.motif2label[motif]
			new_edges = []
			for n in motif:				
				if self.type == 'undirect':
					neighbors = self.reduced_g.neighbors(n)
					#print([x for x in neighbors])
					for neighbor in neighbors:
						new_edges += [(str(last_id), neighbor)]
						#self.reduced_g.add_edge(str(last_id), neighbor)
				else:
					neighbors = self.reduced_g.neighbors(n)
					out_edges = self.reduced_g.edges(n)
					for out_edge in out_edges:
						new_edges += [(str(last_id), out_edge[1])]
						#self.reduced_g.add_edge(str(last_id), out_edge[1])
					for neighbor in neighbors:
						if (neighbor, n) in self.reduced_g.edges():
							self.reduced_g.add_edge(neighbor, str(last_id))		
							new_edges += [(neighbor, str(last_id))]
			
			for (n1,n2) in new_edges:
				self.reduced_g.add_edge(n1,n2)	
			for n in motif:
				self.reduced_g.remove_node(n)
				
			self.reduced_g.remove_edges_from(self.reduced_g.selfloop_edges())	
		
	def get_reduction(self):
			return self.reduced_g
			
	def get_supernode2composition(self):
		return self.supernode2composition
			
	def run(self):
		self.__do_motif2label()
		self.__substitution()
