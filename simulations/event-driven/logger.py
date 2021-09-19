"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os
import numpy as np

from collections import Counter


def calculate_hist(l, n, prefix):
    res = {}
    
    try: 
        max_element = max(l)
        min_element = min(l)
        lin_step = (max_element - min_element) / n
        log_step = np.log2((max_element - min_element) + 1) / n
            
        lin_hist = [0]*n
        log_hist = [0]*n
        for element in l:    
            index = np.floor((element - min_element) / lin_step)
            lin_hist[min(int(index), n-1)] += 1
            index = np.floor(np.log2((element - min_element) + 1) / log_step)
            log_hist[min(int(index), n-1)] += 1

        res[prefix + '_' + 'hist_num_buckets'] = n                      
        res[prefix + '_' + 'lin_hist'] = lin_hist
        res[prefix + '_' + 'log_hist'] = log_hist
        res[prefix + '_' + 'hist_max_element'] = max_element
        res[prefix + '_' + 'hist_min_element'] = min_element
        res[prefix + '_' + 'hist_lin_step_size'] = lin_step
        res[prefix + '_' + 'hist_log_step_size'] = log_step
        
        return res
    
    except:
        res[prefix + '_' + 'hist_num_buckets'] = 0
        res[prefix + '_' + 'lin_hist'] = [0]*n 
        res[prefix + '_' + 'log_hist'] = [0]*n 
        res[prefix + '_' + 'hist_max_element'] = 0
        res[prefix + '_' + 'hist_min_element'] = 0
        res[prefix + '_' + 'hist_lin_step_size'] = 0
        res[prefix + '_' + 'hist_log_step_size'] = 0
    
    return res


class Logger:

    def __init__(self, simulation_params=None):
        
        self.simulation_params = simulation_params
        
        self.connection_tracking = {}
        
        self.broken_connections = {}
        self.broken_connections['jet'] = {}
        self.broken_connections['fct'] = {}
        
        self.removed_servers = {}
        self.added_servers = {}
        
        self.total_connetions = 0
        
    def remove_server(self, server, time):
        self.removed_servers[server] = time
        
    def add_server(self, server, time):
        self.added_servers[server] = time
        
    def add_new_connection(self, connection_id, destination):
        if connection_id not in self.connection_tracking:
            self.connection_tracking[connection_id] = destination
            self.total_connetions += 1

    def remove_connection(self, connection_id):
        del self.connection_tracking[connection_id]
            
    def del_broken_connections(self, destination):
        broken_connections = set()
        for connection_id in list(self.connection_tracking.keys()):
            if self.connection_tracking[connection_id] == destination:
                del self.connection_tracking[connection_id]
                broken_connections.add(connection_id)
        return broken_connections
    
    def get_destination(self, connection_id):
        if connection_id in self.connection_tracking:
            return self.connection_tracking[connection_id]
        else:
            return "new-connection"
    
    def record_broken_connection(self, model, key, mass, s_time, e_time):
        if key not in self.broken_connections[model]:
            flow_duration = e_time - s_time
            self.broken_connections[model][key] = (mass, flow_duration)
        else:
            pass
        
    def print_broken_connection_stats(self):
         
        print("JET broken connections: {}".format(len(self.broken_connections['jet'])))
        print("FCT broken connections: {}".format(len(self.broken_connections['fct'])))

    def get_server_loads(self):
        return list(Counter(self.connection_tracking.values()).values())

    def print_backend_stats(self):
        
        # print(self.removed_servers)
        # print(self.added_servers)
        
        print("removed server times: {}".format(list(self.removed_servers.values())))
        print("added server times: {}".format(list(self.added_servers.values())))    
    
    def write_results(self):
        
        fn = self.simulation_params.file_name
    
        if not os.path.isdir('results'):
            os.mkdir('results')

        with open('./results/' + fn + '.txt', 'a+') as filehandle:
            
            filehandle.write('*'*100)
            filehandle.write('\n')
            
            filehandle.write('Parameters: ')
            for arg in vars(self.simulation_params):
                filehandle.write("{}:{}, ".format(arg, getattr(self.simulation_params, arg)))
            filehandle.write('\n')   
                        
            filehandle.write("JET broken connections: {}\n".format(len(self.broken_connections['jet'])))
            filehandle.write("FCT broken connections: {}\n".format(len(self.broken_connections['fct'])))    
           
            filehandle.write("removed server times: {}\n".format(list(self.removed_servers.values())))
            filehandle.write("added server times: {}\n".format(list(self.added_servers.values())))     
            
            server_loads = self.get_server_loads()
            filehandle.write('maximum over-subscription is {:.3f}\n'.format(np.max(server_loads) / np.mean(server_loads)))   
            
            filehandle.write("total connections: {}\n".format(self.total_connetions))   
            
            filehandle.write('*'*100)
            filehandle.write('\n')

        with open('./results/' + fn + '_flow_data_jet.txt', 'a+') as filehandle:
            
            filehandle.write('*'*100)
            filehandle.write('\n')
            
            filehandle.write('Parameters: ')
            for arg in vars(self.simulation_params):
                filehandle.write("{}:{}, ".format(arg, getattr(self.simulation_params, arg)))
            filehandle.write('\n')   
                        
            for flow_datum_key in self.broken_connections['jet']:
                flow_datum =  self.broken_connections['jet'][flow_datum_key]
                filehandle.write('{}\t{}'.format(flow_datum[0], flow_datum[1])) 
                filehandle.write('\n')
            
            filehandle.write('*'*100)
            filehandle.write('\n')

        with open('./results/' + fn + '_flow_data_fct.txt', 'a+') as filehandle:
            
            filehandle.write('*'*100)
            filehandle.write('\n')
            
            filehandle.write('Parameters: ')
            for arg in vars(self.simulation_params):
                filehandle.write("{}:{}, ".format(arg, getattr(self.simulation_params, arg)))
            filehandle.write('\n')   
                        
            for flow_datum_key in self.broken_connections['fct']:
                flow_datum =  self.broken_connections['fct'][flow_datum_key]
                filehandle.write('{}\t{}'.format(flow_datum[0], flow_datum[1])) 
                filehandle.write('\n')
            
            filehandle.write('*'*100)
            filehandle.write('\n')
