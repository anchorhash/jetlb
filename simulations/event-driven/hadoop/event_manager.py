import math
import string
import numpy as np

from heapq import heappush, heappop


def get_random_string(length=24):
    letters = string.ascii_lowercase
    result_str = ''.join(np.random.choice([char for char in letters]) for _ in range(length))
    return result_str


def read(fn):
    s = open(fn, 'r').read()
    return eval(s)


def getCDFValue(cdf, key):
    for x in sorted(cdf.keys()):
        if key < float(x):
            return cdf[x]
    return None


def getCDFAverage(cdf):
    average = 0
    previous_x = 0
    for x in sorted(cdf.keys()):
        average += cdf[x]*(float(x)-previous_x)
        previous_x = float(x)
    return average


class EventsManager():

    def __init__(self, cdf_path='hadoop/', connection_target=10000, update_rate=10):
        
        self.connection_duration_cdf = read(cdf_path + 'data/hadoop_cdf.txt')
        self.server_updates_cdf = read(cdf_path + 'data/downtime_upgrade_cdf.txt')
        self.connection_size_cdf = read(cdf_path + 'data/hadoop_size_cdf.txt')
        
        # the default values by CHEETAH
        self.connection_target = connection_target
        self.update_rate = update_rate
        self.connection_rate = self.connection_target / getCDFAverage(self.connection_duration_cdf)
        
        # event heap
        self.events = [(0, "new-connection"), (0, "kil-server")]
        
        self.flows = set()
        self.flows_data = {}
        self.flows_spec = {}
        
    def next(self):
        
        time, event = heappop(self.events)
        
        if "new-connection" in event:
            conn_id = get_random_string()
            while conn_id in self.flows:
                conn_id = get_random_string()
            self.flows.add(conn_id)
                                    
            connection_duration = getCDFValue(self.connection_duration_cdf, np.random.random())
            heappush(self.events, (time + connection_duration, "del-connection" + " " + conn_id))
            
            # assume cdf in KB and we have ~100B in a packet
            connection_mass = int(10*getCDFValue(self.connection_size_cdf, np.random.random())) + 1.0
            self.flows_data[conn_id] = (connection_mass, time, time + connection_duration)
            self.flows_spec[conn_id] = (connection_mass, time, time + connection_duration)
            
            connection_next = -math.log(1-np.random.random(), math.e) / self.connection_rate
            heappush(self.events, (time + connection_next, "new-connection"))
            
            return time, "new-connection", conn_id
        
        if "del-connection" in event:
            
            conn_id = event.split(" ")[1]
                     
            try:  # use del_spec_coneciton to clean self.flows_spec[conn]
                self.flows.remove(conn_id)
                del self.flows_data[conn_id]
                return time, "del-connection", conn_id
            except:  # assosiated server is allready removed
                return self.next()
            
        if event == "kil-server":
            update_ends = getCDFValue(self.server_updates_cdf, np.random.random())
            heappush(self.events,(time + update_ends, "new-server"))
            update_next = -math.log(1 - np.random.random(), math.e)/(self.update_rate/60)
            heappush(self.events,(time + update_next, "kil-server"))
            return time, "kil-server", None
 
        if event == "new-server":
            return time, "new-server", None

        raise Exception("cannot arrive here: {}:{}".format(time, event))
 
    def get_params(self):
        return self.connection_target, self.update_rate
    
    def get_active_connections(self, time):
        
        active_flows = []
        for flow in self.flows:
            conn_mass, conn_start_time, conn_end_time = self.flows_data[flow]
            passed_time = time - conn_start_time
            if passed_time == 0:
                continue
            elif passed_time < 0:
                raise Exception("negative time")
            
            passed_conn_time_fraction = (time - conn_start_time) / (conn_end_time - conn_start_time)
            if passed_conn_time_fraction > 1 or passed_conn_time_fraction < 0:
                raise Exception("illegal time")                
            
            passed_conn_packets = np.random.binomial(n=conn_mass, p=passed_conn_time_fraction)
            if passed_conn_packets > 0:
                active_flows.append(flow)
            
            self.flows_data[flow] = conn_mass - passed_conn_packets, time, conn_end_time
            
        print("get_active_connections: sampled {} out of {}.".format(len(active_flows), len(self.flows)))
        
        return active_flows
    
    def del_stale_conecitons(self, conn_list):
        self.flows -= conn_list
        for f in conn_list:
            del self.flows_data[f]
            del self.flows_spec[f]

    def del_spec_coneciton(self, conn):
        del self.flows_spec[conn]                


if __name__ == "__main__":
    m = EventsManager()
    for i in range(1000):
        time, revent, misc = m.next()
        print(time, revent, misc)
