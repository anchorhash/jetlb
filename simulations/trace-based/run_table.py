"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os
import argparse

##############################################################################
##############################################################################

'''	

	c++ main file simulation parameters:
	
	1. trace: path to binary of 5-tuples (e.g., "G:/traces/my_trace")
	2. trace length: number of 5-tuples (13 bytes) to read from binary
	3. number of servers (e.g., 100)
	4. horizon size (0 means zero -> for full CT)
	5. hash type: "anchor" or "hrw"
	6. print trace historgram and exit: 0 (false) or 1 (true)
	7. random seed
	
'''

if __name__ == '__main__':
    
	parser = argparse.ArgumentParser(description="""
		run trace-based simulations and generate result txt files""",
									 formatter_class=argparse.RawTextHelpFormatter)

	### path
	parser.add_argument('--trace_path', help='trace path')

	### result file name
	parser.add_argument('--result_fn', help='result file name')
																								 
	### trials (i.e., seeds)
	parser.add_argument('--trials', default=10, type=int, help='number of different seeds')     

	### trace length (100M at most)
	parser.add_argument('--trace_length', default=10**7, type=int, help='trace length')  
	
	args = parser.parse_args()   
	                           
	####################################################################
	####################################################################
	
	trace_path = args.trace_path
	trace_length = args.trace_length
	result_fn = args.result_fn

	hash_types = ['hrw', 'anchor']
	num_servers = [50, 500]
	

	for random_trial in range(args.trials):
		
		print("*** started trial {}/{}".format(random_trial + 1,args.trials))
			
		total_sim = len(hash_types) * len(num_servers) * 2
		
		finished_sim = 0
		for hash_type in hash_types:
			for ns in num_servers:
				for horizon in [0, int(0.1*ns)]:
				
					command = '"./main"' 
					
					command += ' ' + trace_path
					command += ' ' + str(trace_length)
					command += ' ' + str(ns)
					command += ' ' + str(horizon)
					command += ' ' + hash_type
					command += ' ' + '0'
					command += ' ' + str(42 + 7*random_trial)
					
					command += ' >> {}_results_{}.txt'.format(result_fn, random_trial)
					
					python_args = 'trace_len:{} num_servers:{} horizon:{} hash_type:{}'.format(trace_length, ns, horizon, hash_type)
					os.system('echo ' + python_args + ' >> {}_results_{}.txt'.format(result_fn, random_trial))
					
					os.system(command) 
					
					finished_sim += 1
					print("finished {}/{}".format(finished_sim,total_sim))
    
