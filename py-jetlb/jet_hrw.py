"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

from pylru import lrucache
from xxhash import xxh64_intdigest


class BaselineHRW:

    def __init__(self, workers, lru_size, seed=42): 
        self.workers = list(workers)  
        self.connection_traking = lrucache(size=lru_size)
        self.seed = seed
            
    def score(self, server_id, connection_id):
        return xxh64_intdigest(server_id + connection_id, self.seed)
                
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None:
            _, server = max((self.score(w, connection_id), w) for w in self.workers)
            self.connection_traking[connection_id] = server 
            
        return server
                       
    def add_working_server(self, server):
        self.workers.append(server)
        
    def remove_working_server(self, server):
        self.workers.remove(server)
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def remove_connection(self, connection_id):
        del self.connection_traking[connection_id]
    

class JetHRW:

    def __init__(self, workers, horizon, lru_size, seed=42): 
        self.workers = list(workers)  
        self.horizon = list(horizon) 
        self.connection_traking = lrucache(size=lru_size)
        self.seed = seed
            
    def score(self, server_id, connection_id):
        return xxh64_intdigest(server_id + connection_id, self.seed)
                
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None:
            score, server = max((self.score(w, connection_id), w) for w in self.workers)
            if score < max(self.score(h, connection_id) for h in self.horizon):
                
                # unsafe connection - write to LRU
                self.connection_traking[connection_id] = server 
                
        return server
                       
    def add_working_server(self, server):
        self.horizon.remove(server)
        self.workers.append(server)
        
    def remove_working_server(self, server):
        self.workers.remove(server)
        self.horizon.append(server)
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def add_horizon_server(self, server):
        self.horizon.append(server)
   
    def remove_horizon_server(self, server):
        self.horizon.remove(server)

    def remove_connection(self, connection_id):
        try:
            del self.connection_traking[connection_id]
        except KeyError:
            pass
        
##############################################################################
##############################################################################
