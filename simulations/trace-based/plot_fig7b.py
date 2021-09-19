"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os.path

if __name__ == '__main__':
    
	parser = argparse.ArgumentParser(description="""
		parse trace-based simulation results and generate plots""",
									 formatter_class=argparse.RawTextHelpFormatter)
																 
	### number of result files (seeds)
	parser.add_argument('--trials', default=10, type=int, help='number of different seeds')     

	args = parser.parse_args()   
	                           
	####################################################################
	####################################################################

	nruns = args.trials  
	file_path = "./zipf_simulations_{}_runs.pkl".format(nruns)
	
	if not os.path.isfile(file_path):
		
		data = []
			
		for result_file_index in range(nruns):
		
			with open("zipf_results_{}.txt".format(result_file_index)) as f:
				
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
		data_df.to_pickle(file_path)        

	####################################################################
	####################################################################

	markers = ['s', '.', 'X', 'o'] 
	colors = ['purple', 'darkblue', 'brown', 'darkgreen']

	size = 14

	hash_type = 'anchor'

	fig, ax = plt.subplots(1,4, figsize=(16,3.2), gridspec_kw={'width_ratios': [4, 4, 4, 1]})
		
	####################################################################
	####################################################################

	y = 'oversubscription_ratio'

	data_df = pd.read_pickle("./zipf_simulations_{}_runs.pkl".format(nruns))   
	data_df = data_df[data_df['hash_type'] == hash_type]
		
	m = 0
	for ns in [50, 500]:
		
		ns_data = data_df[data_df['num_servers'] == ns]
		
		baseline_ns_data = ns_data[ns_data['horizon'] == 0]
		baseline_ns_data_mean = baseline_ns_data.groupby(['zipf_skew']).mean().reset_index()
		baseline_ns_data_std = baseline_ns_data.groupby(['zipf_skew']).std().reset_index()
		
		jet_ns_data = ns_data[ns_data['horizon'] != 0]
		jet_ns_data_mean = jet_ns_data.groupby(['zipf_skew']).mean().reset_index()
		jet_ns_data_std = jet_ns_data.groupby(['zipf_skew']).std().reset_index()
			
		ax[0].errorbar(baseline_ns_data_mean['zipf_skew'], 
				   baseline_ns_data_mean[y], 
				   baseline_ns_data_std[y], 
				   label='Full CT (n={})'.format(ns), 
				   marker=markers[m],
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2, 
				   ecolor='k', 
				   capthick=1.5)
		m += 1
		
		ax[0].errorbar(jet_ns_data_mean['zipf_skew'], 
				   jet_ns_data_mean[y], 
				   jet_ns_data_std[y], 
				   label='JET (n={})'.format(ns), 
				   marker=markers[m], 
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2,
				   ecolor='k', 
				   capthick=1.5)
		m += 1

	ax[0].tick_params(axis='x', labelsize=size)
	ax[0].tick_params(axis='y', labelsize=size)

	ax[0].set_ylim(bottom=1, top=1.18)

	ax[0].set_xlabel("Skew", fontsize=size)
	ax[0].set_ylabel("Maximum \n oversubscription", fontsize=size)
		
	ax[0].grid(color='gray', linestyle='--', linewidth=0.5, which='major', axis='y')
	ax[0].grid(color='gray', linestyle=':', linewidth=0.05, which='minor', axis='y')
		
	##############################################################################
	##############################################################################

	y = 'ct_table_size'

	data_df = pd.read_pickle("./zipf_simulations_{}_runs.pkl".format(nruns))   
	data_df = data_df[data_df['hash_type'] == hash_type]

	m = 0
	for ns in [50, 500]:

		ns_data = data_df[data_df['num_servers'] == ns]
		
		baseline_ns_data = ns_data[ns_data['horizon'] == 0]
		baseline_ns_data_mean = baseline_ns_data.groupby(['zipf_skew']).mean().reset_index()
		baseline_ns_data_std = baseline_ns_data.groupby(['zipf_skew']).std().reset_index()
		
		jet_ns_data = ns_data[ns_data['horizon'] != 0]
		jet_ns_data_mean = jet_ns_data.groupby(['zipf_skew']).mean().reset_index()
		jet_ns_data_std = jet_ns_data.groupby(['zipf_skew']).std().reset_index()
				
		ax[1].errorbar(baseline_ns_data_mean['zipf_skew'], 
				   baseline_ns_data_mean[y], 
				   baseline_ns_data_std[y], 
				   label='Full CT (n={})'.format(ns), 
				   marker=markers[m],
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2, 
				   ecolor='k', 
				   capthick=1.5)
		m += 1
		
		ax[1].errorbar(jet_ns_data_mean['zipf_skew'], 
				   jet_ns_data_mean[y], 
				   jet_ns_data_std[y], 
				   label='JET (n={})'.format(ns), 
				   marker=markers[m],
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2, 
				   ecolor='k', 
				   capthick=1.5)
		m += 1
		

	ax[1].tick_params(axis='x', labelsize=size)
	ax[1].tick_params(axis='y', labelsize=size, which='both', width=1)

	ax[1].set_yscale("log")

	ax[1].set_xlabel("Skew", fontsize=size)
	ax[1].set_ylabel("Tracked\n connections", fontsize=size)
		
	ax[1].grid(color='gray', linestyle='--', linewidth=0.5, which='major', axis='y')
	ax[1].grid(color='gray', linestyle=':', linewidth=0.05, which='minor', axis='y')

	##############################################################################
	##############################################################################

	y = 'rate_mkps'

	data_df = pd.read_pickle("./zipf_simulations_{}_runs.pkl".format(nruns))   
	data_df = data_df[data_df['hash_type'] == hash_type]

	m = 0
	for ns in [50, 500]:
		
		ns_data = data_df[data_df['num_servers'] == ns]
		
		baseline_ns_data = ns_data[ns_data['horizon'] == 0]
		baseline_ns_data_mean = baseline_ns_data.groupby(['zipf_skew']).mean().reset_index()
		baseline_ns_data_std = baseline_ns_data.groupby(['zipf_skew']).std().reset_index()
		
		jet_ns_data = ns_data[ns_data['horizon'] != 0]
		jet_ns_data_mean = jet_ns_data.groupby(['zipf_skew']).mean().reset_index()
		jet_ns_data_std = jet_ns_data.groupby(['zipf_skew']).std().reset_index()
				
		ax[2].errorbar(baseline_ns_data_mean['zipf_skew'], 
				   baseline_ns_data_mean[y], 
				   baseline_ns_data_std[y], 
				   label='Full CT (n={})'.format(ns), 
				   marker=markers[m],
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2, 
				   ecolor='k', 
				   capthick=1.5)
		m += 1
		
		ax[2].errorbar(jet_ns_data_mean['zipf_skew'], 
				   jet_ns_data_mean[y], 
				   jet_ns_data_std[y], 
				   label='JET (n={})'.format(ns), 
				   marker=markers[m],
				   markerfacecolor='None',
				   color=colors[m], 
				   markersize=12,
				   capsize=12, 
				   elinewidth=2, 
				   ecolor='k', 
				   capthick=1.5)
		m += 1

	ax[2].tick_params(axis='x', labelsize=size)
	ax[2].tick_params(axis='y', labelsize=size)

	ax[2].set_ylim(bottom=0, top=59)

	ax[2].set_xlabel("Skew", fontsize=size)
	ax[2].set_ylabel("Rate [MKPS]", fontsize=size)
		
	ax[2].grid(color='gray', linestyle='--', linewidth=0.5, which='major', axis='y')
	ax[2].grid(color='gray', linestyle=':', linewidth=0.05, which='minor', axis='y')
		
	##############################################################################
	##############################################################################

	bb = (fig.subplotpars.left+0.1, fig.subplotpars.top+0.03, 
		  fig.subplotpars.right-fig.subplotpars.left-0.1,.1)

	handles, labels = ax[0].get_legend_handles_labels()
	ax[3].legend(handles, labels, ncol=1, fontsize=size-2, loc='center')
	ax[3].set_axis_off()

	plt.tight_layout()

	fig.subplots_adjust(top=0.91,
	bottom=0.225,
	left=0.195,
	right=0.95,
	hspace=0.195,
	wspace=0.485)

	plt.show()

	fig.savefig("fig7b.pdf".format(hash_type), bbox_inches='tight')

