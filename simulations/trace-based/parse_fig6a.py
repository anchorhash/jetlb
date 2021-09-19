"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os
import argparse

if __name__ == '__main__':
    
	parser = argparse.ArgumentParser(description="""
		run trace-based simulations and generate result txt files""",
									 formatter_class=argparse.RawTextHelpFormatter)

	### path
	parser.add_argument('--trace_path', help='trace path')

	### result file name
	parser.add_argument('--result_fn', help='result file name')
																								 
	### trace length 
	parser.add_argument('--trace_length', help='trace length')  
	
	args = parser.parse_args()   
	                           
	####################################################################
	####################################################################
					
	command = '"./main"'             
	command += ' ' + args.trace_path
	command += ' ' + args.trace_length
	command += ' ' + str(50)
	command += ' ' + str(0)
	command += ' ' + 'hrw'
	command += ' ' + '1'
	command += ' ' + str(42)            
	command += ' > {}_trace_hist.txt'.format(args.result_fn)
	os.system(command)  
	print(command)                             
                        
