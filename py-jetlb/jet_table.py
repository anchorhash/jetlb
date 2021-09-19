"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

from pylru import lrucache
from xxhash import xxh64_intdigest


class BaselineTableHRW:

    def __init__(self, workers, lru_size, table_size=1000, seed=42): 
        self.workers = list(workers)
        self.connection_traking = lrucache(size=lru_size)
        self.table_size = table_size
        self.seed = seed
               
        self.table = []
        
        for i in range(self.table_size):
            _, worker = max((self.score(w, i), w) for w in self.workers)
            self.table.append(worker)
            
    def row(self, connection_id):
        return xxh64_intdigest(connection_id, self.seed) % self.table_size

    def score(self, server_id, row):
        return xxh64_intdigest(server_id + str(row), self.seed)
                
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None:
            row = self.row(connection_id)
            server = self.table[row]
            self.connection_traking[connection_id] = server
            
        return server
                       
    def add_working_server(self, server):
        self.workers.append(server)
        for i in range(self.table_size):
            _, worker = max((self.score(w, i), w) for w in [server, self.table[i]])
            self.table[i] = worker     
        
    def remove_working_server(self, server):
        self.workers.remove(server)
        for i in range(self.table_size):
            _, worker = max((self.score(w, i), w) for w in self.workers)
            self.table[i] = worker 
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def remove_connection(self, connection_id):
        del self.connection_traking[connection_id]
                

class JetTableHRW:

    def __init__(self, workers, horizon, lru_size, table_size=1000, seed=42): 
        self.workers = list(workers)
        self.horizon = list(horizon)
        self.connection_traking = lrucache(size=lru_size)
        self.table_size = table_size
        self.seed = seed
               
        self.workers_table = []
        self.horizon_table = []
        
        for i in range(self.table_size):
            score, worker = max((self.score(w, i), w) for w in self.workers)
            self.workers_table.append(worker)
            h_score, _ =  max((self.score(w, i), w) for w in self.horizon)
            self.horizon_table.append(h_score >= score)

    def row(self, connection_id):
        return xxh64_intdigest(connection_id, self.seed) % self.table_size

    def score(self, server_id, row):
        return xxh64_intdigest(server_id + str(row), self.seed)
                
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None:
            row = self.row(connection_id)
            server = self.workers_table[row]
            if self.horizon_table[row]:
                
                # unsafe connection - write to LRU
                self.connection_traking[connection_id] = server 
                
        return server
                       
    def add_working_server(self, server):
        self.horizon.remove(server)
        self.workers.append(server)

        for i in range(self.table_size):
            if self.horizon_table[i]:
                
                score, worker = max((self.score(w, i), w) for w in [server, self.workers_table[i]])
                self.workers_table[i] = worker
                
                if worker == server:
                    h_score =  max(self.score(w, i) for w in self.horizon)
                    self.horizon_table[i] = h_score >= score
        
    def remove_working_server(self, server):
        self.workers.remove(server)
        self.horizon.append(server)

        for i in range(self.table_size):
            if self.workers_table[i] == server:
                score, worker = max((self.score(w, i), w) for w in self.workers)
                self.workers_table[i] = worker
                self.horizon_table[i] = True
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
                        
    def add_horizon_server(self, server):
        self.horizon.append(server)

        for i in range(self.table_size):
            if not self.horizon_table[i]:
                if self.score(server, i) >= self.score(self.workers_table[i], i):
                    self.horizon_table[i] = True
                
    def remove_horizon_server(self, server):
        self.horizon.remove(server)

        for i in range(self.table_size):
            if self.horizon_table[i]:
                h_score = max(self.score(w, i) for w in self.horizon)
                self.horizon_table[i] = h_score >= self.score(self.workers_table[i], i)    

    def remove_connection(self, connection_id):
        try:
            del self.connection_traking[connection_id]
        except KeyError:
            pass
