"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import numpy as np
import matplotlib.pyplot as plt
import os


if __name__ == '__main__':

	os.system("python3 parse_fig6b.py")
	
	size = 28
		   
	trace_skewes = ['0.6', '0.8', '1.0', '1.2', '1.4']
	markers = ["<", ">", "^", "v", "d"]

	hists = [] 
	bin_edgess = []

	for skew in trace_skewes:

		with open("zipf_{}_trace_hist.txt".format(skew)) as f:
			
			lines = f.readlines()[1:]
			hist_data = [int(line) for line in lines]
			
			hist, bin_edges = np.histogram([np.log10(f) for f in hist_data], density=False)
			
			hists.append(hist)
			bin_edgess.append(bin_edges)


	m = 0
	for skew, hist, bin_edges in zip(trace_skewes, hists, bin_edgess):  
			
		edges = [10**x for x in bin_edges]
		plt.loglog([float((x*y)**0.5) for x,y in zip(edges[:-1], edges[1:])], [float(i) for i in hist], label=skew, marker=markers[m], markevery=[0,-1], markersize=12)
		m += 1
		
	plt.grid(color='lightgray', linestyle='-', linewidth=0.5, which='major')
	plt.grid(color='lightgray', linestyle=':', linewidth=0.1, which='minor')

	plt.xticks(size=size)
	plt.yticks(size=size)

		
	plt.xlabel('Flow size', fontsize=size)
	plt.ylabel('Number of flows', fontsize=size)
	plt.legend(fontsize=size-6)
	plt.tight_layout()
	plt.savefig("fig6b.pdf", bbox_inches='tight')
	plt.show()
	
