# Karoo GP (desktop + server combined)
# Use Genetic Programming for Classification and Symbolic Regression
# by Kai Staats, MSc; see LICENSE.md
# version 2.1

'''
A word to the newbie, expert, and brave--
Even if you are highly experienced in Genetic Programming, it is recommended that you review the 'Karoo User Guide' 
before running this application. While your computer will not burst into flames nor will the sun collapse into a black 
hole if you do not, you will likely find more enjoyment of this particular flavour of GP with a little understanding 
of its intent and design.

Without any command line arguments, Karoo GP relies upon user settings and the datasets located in karoo_gp/files/.

	$ python karoo_gp_main.py
	

If you include the path to an external dataset, it will auto-load at launch:

	$ python karoo_gp_main.py /[path]/[to_your]/[filename].csv
	

If you include one or more additional arguments, they will override the default values, as follows:

	-ker [r,c,m]									fitness function: (r)egression, (c)lassification, or (m)atching
	-typ [f,g,r]									Tree type: (f)ull, (g)row, or (r)amped half/half
	-bas [3...10]									maximum Tree depth for initial population
	-max [3...10]									maximum Tree depth for entire run
	-min [3 to 2^(bas +1) - 1]		minimum number of nodes
	-pop [10...1000]							number of trees in each generational population
	-gen [1...100]								number of generations
	-tor [7 per 100]							number of trees selected for tournament
	-evr [0.0...1.0]  						decimal percent of pop generated through Reproduction
	-evp [0.0...1.0]  						decimal percent of pop generated through Point Mutation
	-evb [0.0...1.0]  						decimal percent of pop generated through Branch Mutation
	-evc [0.0...1.0]  						decimal percent of pop generated through Crossover
	
If you include any of the above flags, then you *must* also include a flag to load an external dataset.

	-fil [path]/[to]/[data].csv		an external dataset


An example is given, as follows:

	$ python karoo_gp_server.py -ker c -typ r -bas 4 -fil [path]/[to]/[data].csv

'''

import os
import sys; sys.path.append('modules/') # add directory 'modules' to the current path
import argparse
import karoo_gp_base_class; gp = karoo_gp_base_class.Base_GP()

os.system('clear')
print '\n\033[36m\033[1m'
print '\t **   **   ******    *****    ******    ******       ******    ******'
print '\t **  **   **    **  **   **  **    **  **    **     **        **    **'
print '\t ** **    **    **  **   **  **    **  **    **     **        **    **'
print '\t ****     ********  ******   **    **  **    **     **   ***  *******'
print '\t ** **    **    **  ** **    **    **  **    **     **    **  **'
print '\t **  **   **    **  **  **   **    **  **    **     **    **  **'
print '\t **   **  **    **  **   **  **    **  **    **     **    **  **'
print '\t **    ** **    **  **    **  ******    ******       ******   **'
print '\033[0;0m'
print '\t\033[36m Genetic Programming in Python - by Kai Staats, version 2.1\033[0;0m'
print ''


#++++++++++++++++++++++++++++++++++++++++++
#   User Interface for Configuation       |
#++++++++++++++++++++++++++++++++++++++++++

if len(sys.argv) < 3: # either no command line argument (1) or a filename (2) is provided

	while True:
		try:
			query = raw_input('\t Select (c)lassification, (r)egression, (m)atching, or (p)lay (default m): ')
			if query not in ['c','r','m','p','']: raise ValueError()
			else: kernel = query or 'm'; break
		except ValueError: print '\t\033[32m Select from the options given. Try again ...\n\033[0;0m'
		except KeyboardInterrupt: sys.exit()
		
	if kernel == 'p': # play mode
		while True:
			try:
				query = raw_input('\t Select (f)ull or (g)row (default g): ')
				if query not in ['f','g','']: raise ValueError()
				else: tree_type = query or 'f'; break
			except ValueError: print '\t\033[32m Select from the options given. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		while True:
			try:
				query = raw_input('\t Enter the depth of the Tree (default 1): ')
				if query not in str(range(1,11)) or query == '0': raise ValueError()
				elif query == '': tree_depth_base = 1; break
				else: tree_depth_base = int(query); break
			except ValueError: print '\t\033[32m Enter a number from 1 including 10. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		tree_depth_max = tree_depth_base
		tree_depth_min = 3
		tree_pop_max = 1
		gen_max = 1
		tourn_size = 0
		display = 'm'
		#	evolve_repro, evolve_point, evolve_branch, evolve_cross, tourn_size, precision, filename are not required
	
	else: # if any other kernel is selected
		
		while True:
			try:
				query = raw_input('\t Select (f)ull, (g)row, or (r)amped 50/50 method (default r): ')
				if query not in ['f','g','r','']: raise ValueError()
				else: tree_type = query or 'r'; break
			except ValueError: print '\t\033[32m Select from the options given. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		while True:
			try:
				query = raw_input('\t Enter depth of the \033[3minitial\033[0;0m population of Trees (default 3): ')
				if query not in str(range(1,11)) or query == '0': raise ValueError()
				elif query == '': tree_depth_base = 3; break
				else: tree_depth_base = int(query); break
			except ValueError: print '\t\033[32m Enter a number from 1 including 10. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		while True:
			try:
				query = raw_input('\t Enter maximum Tree depth (default %s): ' %str(tree_depth_base))
				if query not in str(range(tree_depth_base,11)) or query == '0': raise ValueError()
				elif query == '': tree_depth_max = tree_depth_base; break
				else: tree_depth_max = int(query); break
			except ValueError: print '\t\033[32m Enter a number > or = the initial Tree depth. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		max_nodes = 2**(tree_depth_base+1)-1 # calc the max number of nodes for the given depth
		
		while True:
			try:
				query = raw_input('\t Enter minimum number of nodes for any given Tree (default 3; max %s): ' %str(max_nodes))
				if query not in str(range(3,max_nodes + 1)) or query == '0' or query == '1' or query == '2': raise ValueError()
				elif query == '': tree_depth_min = 3; break
				else: tree_depth_min = int(query); break
			except ValueError: print '\t\033[32m Enter a number from 3 including %s. Try again ...\n\033[0;0m' %str(max_nodes)
			except KeyboardInterrupt: sys.exit()
			
		#while True:
			#try:
				#swim = raw_input('\t Select (p)artial or (f)ull operator inclusion (default p): ')
				#if swim not in ['p','f','']: raise ValueError()
				#swim = swim or 'p'; break
			#except ValueError: print '\t\033[32m Select from the options given. Try again ...\n\033[0;0m'
			#except KeyboardInterrupt: sys.exit()
			
		while True:
			try:
				query = raw_input('\t Enter number of Trees in each population (default 100): ')
				if query not in str(range(1,10001)) or query == '0': raise ValueError()
				elif query == '': tree_pop_max = 100; break
				else: tree_pop_max = int(query); break
			except ValueError: print '\t\033[32m Enter a number from 1 including 10000. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		# calculate the tournament size
		tourn_size = int(tree_pop_max * 0.07) # default 7% can be changed by selecting (g)eneration and then 'ts'
		if tourn_size < 2: tourn_size = 2 # forces some diversity for small populations
		if tree_pop_max == 1: tourn_size = 1 # in theory, supports the evolution of a single Tree - NEED TO FIX 2018 04/19
		
		while True:
			try:
				query = raw_input('\t Enter max number of generations (default 10): ')
				if query not in str(range(1,1001)) or query == '0': raise ValueError()
				elif query == '': gen_max = 10; break
				gen_max = int(query); break
			except ValueError: print '\t\033[32m Enter a number from 1 including 1000. Try again ...\n\033[0;0m'
			except KeyboardInterrupt: sys.exit()
			
		if gen_max > 1:
			while True:
				try:
					query = raw_input('\t Display (i)nteractive, (g)eneration, (m)iminal, (s)ilent, or (d)e(b)ug (default m): ')
					if query not in ['i','g','m','s','db','']: raise ValueError()
					display = query or 's'; break  ## andrew@bytesumo.com defaulted this to silent. 
				except ValueError: print '\t\033[32m Select from the options given. Try again ...\n\033[0;0m'
				except KeyboardInterrupt: sys.exit()
				
		else: display = 's' # display mode is not used, but a value must be passed
				
	### additional configuration parameters ###
	
	evolve_repro = int(0.1 * tree_pop_max) # quantity of a population generated through Reproduction
	evolve_point = int(0.02 * tree_pop_max) # quantity of a population generated through Point Mutation
	evolve_branch = int(0.2 * tree_pop_max) # quantity of a population generated through Branch Mutation
	evolve_cross = int(0.69 * tree_pop_max) # quantity of a population generated through Crossover
	filename = '' # not required unless an external file is referenced
	precision = 10 # number of floating points for the round function in 'fx_fitness_eval'
	swim = 'p' # require (p)artial or (f)ull set of features (operators) for each Tree entering the gene_pool
	mode = 'd' # pause at the (d)esktop when complete, awaiting further user interaction; or terminate in (s)erver mode
	

#++++++++++++++++++++++++++++++++++++++++++
#   Command Line for Configuation         |
#++++++++++++++++++++++++++++++++++++++++++

else: # two or more command line arguments provided

	ap = argparse.ArgumentParser(description = 'Karoo GP Server')
	ap.add_argument('-ker', action = 'store', dest = 'kernel', default = 'c', help = '[c,r,m] fitness function: (r)egression, (c)lassification, or (m)atching')
	ap.add_argument('-typ', action = 'store', dest = 'type', default = 'r', help = '[f,g,r] Tree type: (f)ull, (g)row, or (r)amped half/half')
	ap.add_argument('-bas', action = 'store', dest = 'depth_base', default = 4, help = '[3...10] maximum Tree depth for the initial population')
	ap.add_argument('-max', action = 'store', dest = 'depth_max', default = 4, help = '[3...10] maximum Tree depth for the entire run')
	ap.add_argument('-min', action = 'store', dest = 'depth_min', default = 3, help = 'minimum nodes, from 3 to 2^(base_depth +1) - 1')
	ap.add_argument('-pop', action = 'store', dest = 'pop_max', default = 100, help = '[10...10000] number of trees per generation')
	ap.add_argument('-gen', action = 'store', dest = 'gen_max', default = 10, help = '[1...100] number of generations')
	ap.add_argument('-tor', action = 'store', dest = 'tor_size', default = 7, help = '[7 for each 100] recommended tournament size')
	ap.add_argument('-evr', action = 'store', dest = 'evo_r', default = 0.1, help = '[0.0-1.0] decimal percent of pop generated through Reproduction')
	ap.add_argument('-evp', action = 'store', dest = 'evo_p', default = 0.0, help = '[0.0-1.0] decimal percent of pop generated through Point Mutation')
	ap.add_argument('-evb', action = 'store', dest = 'evo_b', default = 0.2, help = '[0.0-1.0] decimal percent of pop generated through Branch Mutation')
	ap.add_argument('-evc', action = 'store', dest = 'evo_c', default = 0.7, help = '[0.0-1.0] decimal percent of pop generated through Crossover')
	ap.add_argument('-fil', action = 'store', dest = 'filename', default = '', help = '/path/to_your/[data].csv')
	
	args = ap.parse_args()

	# pass the argparse defaults and/or user inputs to the required variables
	kernel = str(args.kernel)
	tree_type = str(args.type)
	tree_depth_base = int(args.depth_base)
	tree_depth_max = int(args.depth_max)
	tree_depth_min = int(args.depth_min)
	tree_pop_max = int(args.pop_max)
	gen_max = int(args.gen_max)
	tourn_size = int(args.tor_size)
	evolve_repro = int(float(args.evo_r) * tree_pop_max)
	evolve_point = int(float(args.evo_p) * tree_pop_max)
	evolve_branch = int(float(args.evo_b) * tree_pop_max)
	evolve_cross = int(float(args.evo_c) * tree_pop_max)
	filename = str(args.filename)
	
	display = 's' # display mode is set to (s)ilent
	precision = 6 # number of floating points for the round function in 'fx_fitness_eval'
	swim = 'p' # require (p)artial or (f)ull set of features (operators) for each Tree entering the gene_pool
	mode = 's' # pause at the (d)esktop when complete, awaiting further user interaction; or terminate in (s)erver mode
	

#++++++++++++++++++++++++++++++++++++++++++
#   Conduct the GP run                    |
#++++++++++++++++++++++++++++++++++++++++++

### I propose changing the way that this function is called to implement running evolution in Islands, where Elites jetset between islands.
### this should parallelise the code and improve learning rates too. (I hope)

### How:

### The calls will be done to kickoff many parallel runs - to simulate many Islands evolving separately
### the population files for all islands will all reside in a single directory, and all current files to be suffixed with the island's identfier.

### On each island, the Elite found via populationwide tournament (Elite implemented now) will be written to a "jetsetter" group, called population_j_<IslandID>_.txt
### on evolution, members of population_j will be read in using a file glob, be shuffled, and one randomly selected to join this island's next generation.
### this jetsetter tournament ensures all islands have a stable population size, and they can even evolve at different rates of speed... 
### i.e. a slow island may drop off jetsetters late... but it doesn't matter as long as population_j is randomly initialised on startup with a random initial 
### jetsetter, done possibly before the islands are even activated if and only if the needed population_j file is missing.
### This initialisation, and flexible selection, ensures integrity of migration even if the timing is a bit hotspotty in parallelisation, which can happen.

### The effect will be parallel decoupled jetsetter tournament, sharing best genetic material across N independently evolving islands. PopJ becomes a waiting room.
### last minute flights assigned randomly. Option to have X number of jetsetters per island sent/received.

### Note, on request for jetsetter, all jetsetters in the "waiting room" are collected and shuffled and one chosen - no waiting for all to be there, or all to be latest gen.
### On parallel runnning, I notice my CPUs (12 cores) hardly get used - so a island per thread sounds good. Also my GPU barely notices karoo is running, so 
### a island per thread is unlikely to hammer the machine. 
### Only ram on GPU card is be to watched for large file inputs, or very very large populations with big depth. 
### Note Each island has a full copy of the test/train file. All statistics need to be collected for each island, and centrally collected
### across all islands in a global log ideally.

### on completion of a island's full run, a final best indivudal winner is found and pushed to a Hall of Fame, with test/train validation metrics, 
### Then we rite it out to a hall of fame HOF file. When written all indivuals in the HOF can be compared to see the very
### very best indivual discovered across all islands (note it could be that many tie in this race - so a list of the best produced)

### to accomplish all this logic with the least amount of work, I will try and submit a commandline job via the OS for each island instantiated,
###  passing the directory details and island id's to use.

### lastly - nice to have -- if I point a new run at an old directory, ideally the jetsetters aren't overwritten...
### it means island genetics are jumpstarted with the best genes of the old run, offering a way to kickstart evolution and continue
### the learning cycle from an advanced stage ... which while not perfect, may be just good enough to work in practice for now to effect a "continue" option.

gp.fx_karoo_gp(kernel, tree_type, tree_depth_base, tree_depth_max, tree_depth_min, tree_pop_max, gen_max, tourn_size, filename, evolve_repro, evolve_point, evolve_branch, evolve_cross, display, precision, swim, mode)

# parameters to add: islandID, common run directory
# then karoo can decide right here if this code is being run as a child - island - or as the launcher ... if a launcher, iterate through islandIDs kicking off the jobs.
### be sure to allow an island count of 1, to be able to do comparisons of performance (quality of prediction/evolution, compute wall times)
# if an launcher - launch a commandline run of children processes, with the needed new aurguments, via a loop, to kickstart islands running...


# conditionally print this if not an island run
print '\n\033[3m "It is not the strongest of the species that survive, nor the most intelligent,\033[0;0m'
print '\033[3m  but the one most responsive to change."\033[0;0m --Charles Darwin\n'
print '\033[3m Congrats!\033[0;0m Your Karoo GP run is complete.\n'

# conditionally print a kicked off island print statement with details of island.

sys.exit()


