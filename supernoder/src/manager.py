import sys
import os
import networkx as nx
import itertools
import traceback

#supernoder imports
from enumerator import *
from disjoint_motifs_finder import *
from reducer import *
from counter import *

class Manager:
	TOOL_NAME = 'SUPERNODER 1.0'
	
	def __init__(self, argv):
		#general params
		self.nodes_string = ''
		self.edges_string = ''
		self.web_input = False
		self.argv = argv
		self.g = None
		self.reduced_g = None
		self.edges_file = None
		self.nodes_file = None
		self.type_of_network = 'direct'
		self.method = 'h1'
		self.motifs = set()
		self.motif2edges = {}
		self.motifs_size = 3
		self.th = 50
		self.n_levels = 1
		self.h1_times_repetitions = 1
		self.sample_size = 100
		self.supernoder_out_name = 'result/supernoder_output'
		self.node2motifs = {}
		self.disjoint_motifs = set()
		self.supernode2composition = {}
		self.number_of_repetitions = 1
		
		#components
		self.enumerator = None
		self.disjoint_motif_finder = None
		self.counter = None
		self.reducer = None
		
		
	def __manage_input(self):
		print('\n' + self.TOOL_NAME + ' Reading input')
		if len(self.argv) <= 1:
			print("No param has been provided. Please see: python supernoder.py --help")
			exit(1)
		else:
			i = 1
			while i < len(self.argv):
				if self.argv[i] == '--edges-file' or self.argv[i] == '-e':
					if os.path.exists(self.argv[i + 1]):
						self.edges_file = self.argv[i + 1]
						i += 2
					else:
						print('ERROR The file ' + self.argv[i + 1] + ' does not exist')
						exit(1)
						
				elif self.argv[i] == '--nodes-file' or self.argv[i] == '-n':
					if os.path.exists(self.argv[i + 1]):
						self.nodes_file = self.argv[i + 1]
						i += 2
					else:
						print('ERROR The file ' + self.argv[i + 1] + ' does not exist')
						exit(1)
						
				elif self.argv[i] == '--type-of-network' or self.argv[i] == '-tn':
					if self.argv[i + 1] in ['direct', 'undirect']:
						self.type_of_network = self.argv[i + 1]
						i += 2
					else:
						print("ERROR <type>: # " + str(self.argv[i + 1]) + " # Network can only be direct or indirect Please see: python supernoder.py --help")		
						exit(1)
					
				elif self.argv[i] == '--number-repetition' or self.argv[i] == '-nr':
					try:
						self.number_of_repetitions = int(self.argv[i + 1])
						i += 2
					except:
						print('ERROR <sample_size> must be a number')
						exit(1)
				
				elif self.argv[i] == '--threshold' or self.argv[i] == '-th':
					try:
						self.th = int(self.argv[i + 1])
						i += 2
					except:
						print('ERROR <threshold> must be a number')
						exit(1)
				elif self.argv[i] == '--motif-size' or self.argv[i] == '-ms':
					try:
						self.motifs_size = int(self.argv[i + 1])
						i += 2
					except:
						print('ERROR <motif_size> must be a number')
						exit(1)
				elif self.argv[i] == '--method' or self.argv[i] == '-m':
					if self.argv[i + 1] in ['h1', 'h2', 'h3', 'h4', 'h5']:
						self.method = self.argv[i + 1]
						i += 2
					else:
						print('ERROR Chosen method is not recognized')
						exit(1)
				
				elif self.argv[i] == '--h1-times-repetition' or self.argv[i] == '-h1tr':
					try:
						self.h1_times_repetitions = int(self.argv[i + 1])
						i += 2
					except:
						print('ERROR <times_repetitions> must be a number')
						exit(1)
				elif self.argv[i] == '--samples-size' or self.argv[i] == '-ss':
					try:
						self.sample_size = int(self.argv[i + 1])
						i += 2
					except:
						print('ERROR <sample_size> must be a number')
						exit(1)
				elif self.argv[i] == '--web-input' or self.argv[i] == '-w':
					try:
						if self.argv[i + 1] == '1' or self.argv[i + 1] == 'True':
							self.web_input = True
							i += 2
						else:
							print('WEB mode has not been recognized')
							exit(1)
					except:
						exit(1)
						
				elif self.argv[i] == '--help' or self.argv[i] == '-h':
					print("\n#####################################\nRelease 1.0 SUPERNODER\n")
					print("Usage: python xproject -t <input_text> \n LIST OF PARAMS:\n" \
					" -n,  --nodes-file \t\t<filename> \tMANDATORY \tThe list of nodes. Node id and label for each row separated by a space\n" \
					" -e,  --edges-file \t\t<filename> \tMANDATORY \tThe list of edges. One edge for each row.\n" \
					" -m,  --method \t\t\t<method> \tOPTIONAL \tThe heuristic to use in order to maximize motifs. DEFAULT: 3\n" \
					" -tn, --type-of-network \t<type> \t\tOPTIONAL 	The type of network. It can be chosen from [direct, undirect]. DEFAULT: direct.\n" \
					" -nr, --number-of-repetitions\t<number> \tOPTIONAL \tThe number of repetitions to build hierarchical levels. DEFAULT: 1\n" \
					" -th, --threshold \t\t<threshold> \tOPTIONAL \tThe threshold to hold over-represented motifs.\n" \
					" -ms, --motif-size \t\t<size> \t\tOPTIONAL \tThe size of motifs. It must be greater or equal to 3. DEFAULT: 3.\n"\
					" -h1tr, --h1-times-repetition \t<times> \tOPTIONAL \tThe number of repetition of h1. DEFAULT: 1.\n" \
					" -ss, --samples-size \t\t<sample_size> \tOPTIONAL \tThe size of samples for heuristics h4 and h5. DEFAULT: 100.\n")
					exit(1)
				else:
					print("\nERROR Param: # " + str(self.argv[i]) + " # Please see: python supernoder.py --help")
					exit(1)
		
	
	def __load_graph(self):	
		print ('# ' + (str(datetime.datetime.now()) + ' Loading graph'))
		if self.type_of_network == 'direct':
			self.g = nx.DiGraph()	
		elif self.type_of_network == 'undirect':
			self.g = nx.Graph()	
		try:							
			with open(self.nodes_file, 'r') as f:
				lines = f.read().splitlines()
				for line in lines:
					values = line.split(' ')
					if len(values) == 2:
						self.g.add_node(values[0], label=values[1])	
					elif len(values) > 2 or len(values) == 1:
						print('nodes are not well formatted')
						raise ValueError('nodes are not well formatted') 
			nodes_set = set(self.g.nodes())
			with open(self.edges_file, 'r') as f:
				lines = f.read().splitlines()
				for line in lines:
					values = line.split(' ')
					if len(values) == 2 and values[0] in nodes_set and values[1] in nodes_set:
						self.g.add_edge(values[0], values[1])
					elif len(values) > 2 or len(values) == 1:
						print('edges are not well formatted')
						raise ValueError('edges are not well formatted') 
			
			print ('#\tThe original network has ', len(self.g.edges()), ' nodes and ', len(self.g.edges()), ' edges')
		except:
			traceback.print_exc(file=sys.stdout)
			print("ERROR: nodes file or edges file is missing")
			exit(1)
					
	def __compile_node2motifs(self):
		for motif in self.motifs:
			for n in motif:
				if n not in self.node2motifs:
					self.node2motifs[n] = set()
				self.node2motifs[n].add(motif)
		
	
	
	def	__do_enumeration(self):
		print('# ' + str(datetime.datetime.now()) + ' Enumeration')
		self.motifs = Utils.enumerate_motifs(self.g, self.motifs_size)
		print ('#\tThe total number of motifs is ', len(self.motifs))
		self.motif2edges = {}
		for motif in self.motifs:
			if motif not in self.motif2edges:
				self.motif2edges[motif] = set()
			for v in itertools.combinations(motif, 2):
				if self.type_of_network == 'direct':
					if self.g.has_edge(v[0], v[1]):
						self.motif2edges[motif].add(v)
					if self.g.has_edge(v[1], v[0]):
						self.motif2edges[motif].add((v[1],v[0]))
				elif self.type_of_network == 'undirect':
					if self.g.has_edge(v[0], v[1]):
						self.motif2edges[motif].add(v)
		
	def __find_disjoint_motifs(self):
		print ('# ' + str(datetime.datetime.now()) + ' Disjointness computation' )
		self.disjoint_motif_finder = DisjointMotifsFinder(self.g, self.motifs, self.motif2edges, self.sample_size, self.node2motifs, self.h1_times_repetitions)
		self.disjoint_motif_finder.run(self.method)
		self.disjoint_motifs = self.disjoint_motif_finder.get_disjoint_motifs()
		print ('#\tThe number of disjoint motifs is ', len(self.disjoint_motifs))

	def __cut(self):
		print ('# ' + str(datetime.datetime.now()) + ' Threshold computation')
		self.counter = Counter(self.g, self.motifs, self.th, self.type_of_network, self.motif2edges)
		self.counter.run()
		self.motifs = self.counter.get_selected_motifs()
		print ('#\tThe number of motifs that occur more than', self.th, 'times is', len(self.motifs))
	
	def __reduction(self):
		print ('# ' + str(datetime.datetime.now()) + ' Reduction')
		self.reducer = Reducer(self.g, self.disjoint_motifs, self.th, self.type_of_network)
		self.reducer.run()
		self.reduced_g = self.reducer.get_reduction()
		self.supernode2composition = self.reducer.get_supernode2composition()
		print ('#\tThe resulting network has', len(self.reduced_g.nodes()), 'nodes and', len(self.reduced_g.edges()))
	
	def __save_result(self, c):
		name_result_file = 'result'
		if self.web_input:
			name_result_file = name_result_file + '_' + str(os.getpid())
		name_result_file = name_result_file + '.txt'
		
		with open(name_result_file, 'a') as f:
			f.write('Network after ' + str(c) + ' iteration(s)\nNODES\n')
			for node in list(self.reduced_g.nodes()):
				f.write(node + ' ' + self.reduced_g.nodes[node]['label'])
				if node in self.supernode2composition:
					f.write('&emsp;[' + ' - '.join(self.supernode2composition[node]) + ']&emsp;#supernode')
				f.write('\n')
			f.write('EDGES\n')
			for (n1,n2) in list(self.reduced_g.edges()):
				f.write(n1 + ' ' + n2 + '\n')
			f.write('\n')
		
		
	def run(self):
		self.__manage_input()
		self.__load_graph()
		c = 0
		while(c < self.number_of_repetitions):
			print ('\nRepetition ' + str(c + 1) + '/' + str(self.number_of_repetitions))
			self.__do_enumeration()
			self.__cut()
			self.__compile_node2motifs()
			self.__find_disjoint_motifs()
			self.__reduction()
			self.__save_result(c + 1)	
			c += 1
			self.g = self.reduced_g
		print ('SuperNoder execution has finished\n')
		
if __name__ == '__main__':
	m = Manager(sys.argv)
	m.run()
		
		
		
		
		