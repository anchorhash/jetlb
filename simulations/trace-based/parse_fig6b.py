"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os
import os.path

traces = ['0.6', '0.8', '1.0', '1.2', '1.4']
traces_paths = ['./zipf_traces/zipf{}'.format(i) for i in traces]
        
for trace_path, skew in zip(traces_paths, traces):
	
	file_path = "zipf_{}_trace_hist.txt".format(skew)
	if not os.path.isfile(file_path):
			
		command = '"./main"'             
		command += ' ' + trace_path
		command += ' ' + str(100000000)
		command += ' ' + str(50)
		command += ' ' + str(0)
		command += ' ' + 'hrw'
		command += ' ' + '1'
		command += ' ' + str(42)            
		command += ' > zipf_{}_trace_hist.txt'.format(skew)
		os.system(command)  
		print(command) 
	
	else:
		
		print("result file allready exists: {}".format(file_path))                            
                        
