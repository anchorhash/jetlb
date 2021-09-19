"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import pandas as pd
import argparse

##############################################################################
##############################################################################

if __name__ == '__main__':
    
	parser = argparse.ArgumentParser(description="""
		run trace-based simulations and generate result txt files""",
									 formatter_class=argparse.RawTextHelpFormatter)

	### result file name
	parser.add_argument('--result_fn', help='result file name')
																								 
	### trials (i.e., seeds)
	parser.add_argument('--trials', default=10, type=int, help='number of different seeds')     
   
	args = parser.parse_args()    
							   
	####################################################################
	####################################################################

	nruns = args.trials
	result_fn = args.result_fn
		
	data = []

	for result_file_index in range(nruns):

		with open("{}_results_{}.txt".format(result_fn,result_file_index)) as f:
			
			lines = f.readlines()
			
			simulation = {"result_file_index": result_file_index}
			
			for line in lines: 
				
				sline = line.split()
					
				### starting new sim
				if '%%%%%%%%%%%%%%%%%' in line:
					if simulation:
						data.append(simulation)
					simulation = {"result_file_index": result_file_index}
					continue
				
				if 'hash_type:' in line:
					simulation.update(dict(word.split(":") for word in sline))
					
					for key in simulation: 
						try:
							simulation[key] = float(simulation[key]) 
						except:
							pass
						
					continue
		
				if line.startswith('HRW load factor'):
					simulation['hrw_load'] = float(sline[-1])
					continue      
				
				if line.startswith('HRW table size'):
					simulation['hrw_table_size'] = float(sline[-1])
					continue           
		 
				if line.startswith('Execution time'):
					simulation['time'] = float(sline[-1])
					continue  
				
				if line.startswith('MKPS'):
					simulation['rate_mkps'] = float(sline[-1])
					continue  
		
				if line.startswith('load factor'):
					simulation['oversubscription_ratio'] = float(sline[-1])
					continue  
		
				if line.startswith('CT table size'):
					simulation['ct_table_size'] = float(sline[-1])
					continue  
		
				if line.startswith('Number of disctinct flows'):
					simulation['disctinct_flows'] = float(sline[-1])
					continue  
								
	data_df = pd.DataFrame.from_dict(data)        
	data_df.to_pickle("./{}_simulations_{}_runs.pkl".format(result_fn, nruns)) 
	
	print(data_df)
	print()
	print()
	print()
	print()
	print()
	print()
	
	for hash_type in ['hrw', 'anchor']:
		for num_servers in [50, 500]:
			for alg, horizon in zip(['full-CT', 'JET'], [0, num_servers//10]):
				
				current_df = data_df.loc[(data_df['hash_type']==hash_type) & (data_df['num_servers']==num_servers) & (data_df['horizon']==horizon)]
				
				print()
				print()
				print('hash type: {}; servers: {}; {}'.format(hash_type, num_servers, alg))
				print()	
				print(current_df.drop(columns=['result_file_index']).mean())
		
	##############################################################################
	##############################################################################

