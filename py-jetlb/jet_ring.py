"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

from pylru import lrucache
from xxhash import xxh64_intdigest
from sortedcontainers import SortedDict


class BaselineRing:

    def __init__(self, workers, lru_size, replicas=100, seed=42): 
        self.workers = list(workers)
        self.connection_traking = lrucache(size=lru_size)
        self.seed = seed
        self.ring = SortedDict()
        self.replicas = replicas
                
        for server in workers:
            for replica in range(self.replicas):
                score = self.score(server, replica)
                self.ring[score] = server
            
    def score(self, key, replica=""):
        return xxh64_intdigest(key + str(replica), self.seed)
                
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None: 
            pos = self.ring.bisect(self.score(connection_id)) % len(self.ring)
            _, server = self.ring.peekitem(pos)
            self.connection_traking[connection_id] = server 
            
        return server
                       
    def add_working_server(self, server):
        self.workers.append(server)
        
        for replica in range(self.replicas):
            score = self.score(server, replica)
            self.ring[score] = server
        
    def remove_working_server(self, server):
        self.workers.remove(server)
        
        for replica in range(self.replicas):
            score = self.score(server, replica)
            try:
                del self.ring[score]
            except KeyError:
                print("BaselineRing: remove_working_server: replica {} does not exist".format(replica))
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def remove_connection(self, connection_id):
        del self.connection_traking[connection_id]
        

class JetRing:

    def __init__(self, workers, horizon, lru_size, replicas=100, seed=42):
        self.workers = list(workers)
        self.horizon = list(horizon) 
        self.connection_traking = lrucache(size=lru_size)
        self.seed = seed
        self.ring = SortedDict()
        self.replicas = replicas
        
        for server in workers:
            for replica in range(self.replicas):
                score = self.score(server, replica)
                self.ring[score] = (server, True)
                
        for server in horizon:
            for replica in range(self.replicas):
                score = self.score(server, replica)
                self.ring[score] = (self.get_working_successor(score), False)            
                            
    def score(self, key, replica=""):
        return xxh64_intdigest(key + str(replica), self.seed)
                           
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None: 
            pos = self.ring.bisect(self.score(connection_id)) % len(self.ring)
            _, (server, is_working) = self.ring.peekitem(pos)
            # Unsafe connection
            if not is_working:
                self.connection_traking[connection_id] = server 
        
        return server
                       
    def add_working_server(self, server):
        self.horizon.remove(server)
        self.workers.append(server)
 
        for replica in range(self.replicas):
            # locate and update
            score = self.score(server, replica)
            if score in self.ring: 
                # update to working server
                self.ring[score] = (server, True) 
                
                # update trailing horizon servers
                self.update_trailing_horizon(score, server)
                        
    def remove_working_server(self, server):
        self.workers.remove(server)
        self.horizon.append(server)
        
        for replica in range(self.replicas):
            score = self.score(server, replica)
            if score in self.ring: 
                # find the next working server
                next_working_server = self.get_working_successor(score)

                # move to horizon
                self.ring[score] = (next_working_server, False)
                
                # update trailing horizon servers 
                self.update_trailing_horizon(score, next_working_server) 
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def add_horizon_server(self, server):
        self.horizon.append(server)
        for replica in range(self.replicas):
            score = self.score(server, replica)
            if score not in self.ring:
                self.ring[score] = (self.get_working_successor(score), False)

    def remove_horizon_server(self, server):
        self.horizon.remove(server)
        for replica in range(self.replicas):
            score = self.score(server, replica)
            if score in self.ring:
                if not self.ring[score][1]: 
                    del self.ring[score]

    '''going 'counterclockwise' until reaching a working server and updating 
    all horizons on the way - does not includes the starting point'''
    def update_trailing_horizon(self, score, worker):
        pos = (self.ring.bisect(score) - 2) % len(self.ring)
        score, data = self.ring.peekitem(pos)
        while not data[1]:
            self.ring[score] = (worker, False)
            pos = (pos - 1) % len(self.ring)
            score, data = self.ring.peekitem(pos)        
    
    '''going 'clockwise' until reaching a working server 
    and returning it - does not includes the starting point'''
    def get_working_successor(self, score):
        pos = self.ring.bisect(score) % len(self.ring)
        score, data = self.ring.peekitem(pos)
        while not data[1]:
            pos = (pos + 1) % len(self.ring)
            score, data = self.ring.peekitem(pos)
        return self.ring.peekitem(pos)[1][0] 

    def remove_connection(self, connection_id):
        try:
            del self.connection_traking[connection_id]
        except KeyError:
            pass
        
##############################################################################
##############################################################################
