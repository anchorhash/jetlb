"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

from pylru import lrucache
from xxhash import xxh64_intdigest


class AnchorHash:

    def __init__(self, size, horizon, capacity, seed):
        if size + horizon > capacity:
            raise Exception("num_bucket plus num_horizon must not be greater than capacity")

        self.size = size
        self.horizon = horizon
        self.capacity = capacity
        self.seed = seed

        # removal size - 0 if working
        self.removal_size = [0 for _ in range(capacity)]

        # working set
        self.buckets = [x for x in range(capacity)]

        # last bucket location
        self.last_location = [x for x in range(capacity)]

        # successor
        self.successor = [x for x in range(capacity)]

        # removed buckets stack
        self.removed_buckets = []

        # initial ordered removals
        for i in range(size, capacity):
            bucket = capacity + size - i - 1
            self.removal_size[bucket] = bucket
            self.buckets[self.last_location[bucket]] = self.buckets[bucket]
            self.last_location[self.buckets[bucket]] = self.last_location[bucket]
            self.successor[bucket] = self.buckets[bucket]
            self.removed_buckets.append(bucket)   
            
    def get_bucket(self, key):
        track = False
        bucket, hashkey = self.modhash(key, self.capacity)
        while self.removal_size[bucket] > 0:  # b is removed
            if self.removal_size[bucket] < self.size + self.horizon:
                track = True
            candidate, hashkey = self.modhash(hashkey, self.removal_size[bucket], bucket)
            while self.removal_size[candidate] >= self.removal_size[bucket]:
                # bucket removed prior to candidate
                candidate = self.successor[candidate]
            bucket = candidate
        return bucket, track

    def add_bucket(self):
        if self.size + self.horizon >= self.capacity:
            raise OverflowError("reached maximum capacity")

        bucket = self.removed_buckets.pop()
        self.removal_size[bucket] = 0
        self.last_location[self.buckets[self.size]] = self.size
        self.buckets[self.last_location[bucket]] = bucket
        self.successor[bucket] = bucket
        self.size += 1
        self.horizon -= 1
        
        return bucket

    def remove_bucket(self, bucket):
        self.size -= 1
        self.removal_size[bucket] = self.size
        self.buckets[self.last_location[bucket]] = self.buckets[self.size]
        self.last_location[self.buckets[self.size]] = self.last_location[bucket]
        self.successor[bucket] = self.buckets[self.size]
        self.removed_buckets.append(bucket)
        self.horizon += 1

    def modhash(self, key, size, bucket=-1):
        h = xxh64_intdigest(str(key) + str(bucket), self.seed)
        return h % size, h
    
    def add_horizon(self):
        self.horizon += 1
        
    def remove_horizon(self):
        self.horizon -= 1
        

class BaselineAnchorHash:

    def __init__(self, workers, lru_size, capacity=100, seed=42): 
        
        self.capacity = capacity
        self.seed = seed
        
        self.connection_traking = lrucache(size=lru_size)
        self.anchorhash = AnchorHash(len(workers), 0, self.capacity, self.seed)
        
        self.bijection = {}
        for i, server in enumerate(workers):
            self.bijection[i] = server
                                   
    def get_destination(self, connection_id):
        
        # check if connection_id is tracked (return None if not)
        server = self.connection_traking.get(connection_id)
        
        # untracked connection
        if server is None: 
            bucket, _ = self.anchorhash.get_bucket(connection_id)
            server = self.bijection[bucket]
            self.connection_traking[connection_id] = server
            
        return server
                       
    def add_working_server(self, server):
        bucket = self.anchorhash.add_bucket()
        self.bijection[bucket] = server
        
    def remove_working_server(self, server):
        bucket = list(self.bijection.keys())[list(self.bijection.values()).index(server)]
        self.anchorhash.remove_bucket(bucket)
        del self.bijection[bucket]
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def remove_connection(self, connection_id):
        del self.connection_traking[connection_id]
                

class JetAnchorHash:

    def __init__(self, workers, horizon, lru_size, capacity=100, seed=42):
        
        self.workers = list(workers)
        self.horizon = list(horizon)
               
        self.capacity = capacity
        self.seed = seed
        
        self.connection_tracking = lrucache(size=lru_size)
        self.anchorhash = AnchorHash(len(workers), len(horizon), self.capacity, self.seed)
        
        self.bijection = {}
        for i, server in enumerate(workers):
            self.bijection[i] = server
                                   
    def get_destination(self, connection_id):
        # check if connection_id is tracked (return None if not)
        server = self.connection_tracking.get(connection_id)
        
        # untracked connection
        if server is None: 
            bucket, track = self.anchorhash.get_bucket(connection_id)
            server = self.bijection[bucket]
            if track:
                self.connection_tracking[connection_id] = server
            
        return server
                       
    def add_working_server(self, server):
        self.workers.append(server)
        self.horizon.remove(server)
        bucket = self.anchorhash.add_bucket()
        self.bijection[bucket] = server
        
    def remove_working_server(self, server):
        self.horizon.append(server)
        self.workers.remove(server)
        bucket = list(self.bijection.keys())[list(self.bijection.values()).index(server)]
        self.anchorhash.remove_bucket(bucket)
        del self.bijection[bucket]
        
        '''
        for connection_id in list(self.connection_traking.keys()):
            if self.connection_traking[connection_id] == server:
                del self.connection_traking[connection_id]
        '''
        
    def add_horizon_server(self, server):
        self.horizon.append(server)
        self.anchorhash.add_horizon()
    
    def remove_horizon_server(self, server):
        self.horizon.remove(server)
        self.anchorhash.remove_horizon()

    def remove_connection(self, connection_id):
        try:
            del self.connection_tracking[connection_id]
        except KeyError:
            pass
