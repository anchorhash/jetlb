"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import numpy as np
import matplotlib.pyplot as plt
import argparse
import os
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
    
if __name__ == '__main__':
    
	parser = argparse.ArgumentParser(description="""
		run trace-based simulations and generate result txt files""",
									 formatter_class=argparse.RawTextHelpFormatter)

	### trace_path
	parser.add_argument('--trace_path', help='trace_path')
																								 
	### trace length 
	parser.add_argument('--trace_length', help='trace length')  
		
	args = parser.parse_args()   
	                           
	####################################################################
	####################################################################
	
	os.system("python3 parse_fig6a.py --trace_path {} --result_fn {} --trace_length {}".format(args.trace_path, path_leaf(args.trace_path), args.trace_length))
	
	size = 28
		   
	with open("{}_trace_hist.txt".format(path_leaf(args.trace_path))) as f:
			
		lines = f.readlines()[1:]
		hist_data = [int(line) for line in lines]

		hist, bin_edges = np.histogram([np.log10(f) for f in hist_data], density=False)
			
	edges = [10**x for x in bin_edges]
	plt.loglog([float((x*y)**0.5) for x,y in zip(edges[:-1], edges[1:])], [float(i) for i in hist], label=path_leaf(args.trace_path), marker='D', markevery=[0,-1], markersize=12)
	   
	plt.grid(color='lightgray', linestyle='-', linewidth=0.5, which='major')
	plt.grid(color='lightgray', linestyle=':', linewidth=0.1, which='minor')

	plt.xticks(size=size)
	plt.yticks(size=size)
	  
	plt.xlabel('Flow size', fontsize=size)
	plt.ylabel('Number of flows', fontsize=size)
	plt.legend(fontsize=size-6)
	plt.tight_layout()
	plt.savefig("fig6a.pdf", bbox_inches='tight')
	plt.show() 

	
 
