from support_functions import *
from networkx.algorithms import isomorphism

class Counter:
	def __init__(self, g, motifs, th, type, motif2edges):
		self.g = g
		self.motifs = motifs
		self.th = th
		self.type = type
		self.motif2edges = motif2edges
		self.selected_motifs = []
		self.descriptor2motifs = {}
		
	def first_count(self):	
		motif2descriptor = {}
		for motif in self.motifs:
			g1 = self.g.subgraph(motif)
			g1 = nx.DiGraph(g1.edges())
			if self.type == 'undirect':
				g1 = nx.Graph(g1.edges())
			else:
				g1 = nx.DiGraph(g1.edges())
			labels_map = {}
			for node in motif:
				label = self.g.nodes[node]['label']#node2label[node]	
				if self.type == 'undirect':
					d = g1.degree[node]
					if label not in labels_map:
						labels_map[label] = (label, 1, d)
					else:
						labels_map[label] = (label, labels_map[label][1] + 1, labels_map[label][2] + d)
				else:
					in_degree = g1.in_degree(node)
					out_degree = g1.out_degree(node)
					if label not in labels_map:
						labels_map[label] = (label, 1, in_degree, out_degree)
					else:
						labels_map[label] = (label, labels_map[label][1] + 1, labels_map[label][2] + in_degree, labels_map[label][3] + out_degree)
				
			labels = sorted([v for k, v in labels_map.items()])

			descriptor = ''			
			for l in labels:
				string_l = '_'.join([str(value) for value in l]) + '_' 
				descriptor += string_l
			descriptor = descriptor[:-1]
			motif2descriptor[motif] = descriptor
			
			if descriptor not in self.descriptor2motifs:
				self.descriptor2motifs[descriptor] = []
			self.descriptor2motifs[descriptor] += [motif]	
	
		#keep only motifs that meet the threshold
		keys = list(self.descriptor2motifs.keys())
		for descriptor in keys:
			if len(self.descriptor2motifs[descriptor]) >= self.th:
				self.selected_motifs += self.descriptor2motifs[descriptor]
			else:
				self.descriptor2motifs.pop(descriptor, None)
			
		
	#This function is used to compute the isomorphism between two undirect graphs.
	def isomorphism_undirect(self, g1, g2):	
		matcher = isomorphism.GraphMatcher(g1, g2, node_match = self.__node_equals)	
		return matcher.is_isomorphic()
		

	#This function is used to compute the isomorphism between two directed graphs
	def isomorphism_directed(self, g1, g2):
		matcher = isomorphism.DiGraphMatcher(g1, g2, node_match = self.__node_equals)
		return matcher.is_isomorphic()	
		
	def __node_equals(self, attributes_n1, attributes_n2):	
		return attributes_n1 == attributes_n2

	def check_real_isomorphisms(self):
		iso = {}		
		key_generator = 0
		for descriptor in self.descriptor2motifs:
			for motif in self.descriptor2motifs[descriptor]:
				
				if type == 'direct':
					g1 = nx.DiGraph()
				else:
					g1 = nx.Graph()
				g1.add_nodes_from(motif)
				g1.add_edges_from(self.motif2edges[motif])
				
				for node in motif:
					g1.nodes[node]['label'] = self.g.nodes[node]['label']#node2label[node]
				
				f_iso = False
				for k in iso:
					if type == 'direct':
						f_iso = self.isomorphism_directed(iso[k][0], g1)
					else:
						f_iso = self.isomorphism_undirect(iso[k][0], g1)						
					if f_iso:
						iso[k] += [g1]
						break
				
				if not f_iso:
					iso[key_generator] = [g1]
					key_generator += 1	
		self.selected_motifs = set([tuple(x.nodes()) for k,v in iso.items() for x in v if len(v) >= self.th])

	def get_selected_motifs(self):
		return self.selected_motifs
		
	def run(self):
		self.first_count()
		self.check_real_isomorphisms()
		