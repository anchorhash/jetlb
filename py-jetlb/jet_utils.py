"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import numpy as np
import argparse
import string

from numpy import random

from jet_hrw import BaselineHRW, JetHRW
from jet_ring import BaselineRing, JetRing
from jet_anchorhash import BaselineAnchorHash, JetAnchorHash
from jet_table import BaselineTableHRW, JetTableHRW


def get_random_string(length, seed=None):
    # store random generator statically so repeated calls return new strings
    if not hasattr(get_random_string, 'rnd'):
        get_random_string.rnd = random.RandomState(seed)
    rnd = get_random_string.rnd
    letters = string.ascii_lowercase
    result_str = ''.join(rnd.choice([char for char in letters]) for _ in range(length))
    return result_str


def parse_args():
    """parse command line"""
    parser = argparse.ArgumentParser(description='Jet test') 

    parser.add_argument('-p', '--ch_type', choices=['anchor', 'hrw', 'ring', 'hrw_table'],
                        default='anchor')
    parser.add_argument('-z', '--num_horizon', type=int,
                        help="horizon size")
    parser.add_argument('-a', '--no_server_tag_recycling', action='store_true',
                        help="use new tags for new servers")
    parser.add_argument('-n', '--num_servers', type=int, default=100,
                        help="number of servers")
    parser.add_argument('-m', '--lru_size', type=int, default=100000,
                        help="size of lru connection tracking map")
    parser.add_argument('-s', '--seed', type=int, default=42,
                        help="seed for random hashing and sampling")
    parser.add_argument('-c', '--capacity', type=int,
                        help="some implementations require capacity")
    parser.add_argument('-r', '--replicas', type=int, default=300,
                        help="some implementations require virtual node replicas, default is 100")
    parser.add_argument('-k', '--num_keys', type=int, default=1000000,
                        help="number of keys to run in NON-EM simulations")
    parser.add_argument('-l', '--connection_target', type=int, default=100000,
                        help="expected number of connections in EM simulation")
    parser.add_argument('-u', '--update_rate', type=float, default=2.0,
                        help="expected number of server updates per-minute in EM simulation")
    parser.add_argument('-t', '--simulation_time', type=int, default=1000,
                        help="simulation time in seconds - EM simulation")
    parser.add_argument('-f', '--file_name', type=str, default='fn',
                        help="result file name")
    
    params = parser.parse_args()
    
    if params.num_horizon is None:
        params.num_horizon = int(np.ceil(0.1*params.num_servers))
    if params.capacity is None:
        params.capacity = 2*params.num_servers
                
    return params


def gen_jets():
    params = parse_args()
        
    workers = [get_random_string(16, params.seed) for _ in range(params.num_servers)]
    horizon = [get_random_string(16, params.seed) for _ in range(params.num_horizon)]  
    
    if params.ch_type == 'anchor':
        baseline = BaselineAnchorHash(workers, params.lru_size, params.capacity, params.seed)
        jet = JetAnchorHash(workers, horizon, params.lru_size, params.capacity, params.seed)
    
    elif params.ch_type == 'hrw_table': 
        baseline = BaselineTableHRW(workers, params.lru_size, params.capacity*params.replicas, params.seed)
        jet = JetTableHRW(workers, horizon, params.lru_size, params.capacity*params.replicas, params.seed)

    elif params.ch_type == 'hrw': 
        baseline = BaselineHRW(workers, params.lru_size, params.seed)
        jet = JetHRW(workers, horizon, params.lru_size, params.seed)

    elif params.ch_type == 'ring': 
        baseline = BaselineRing(workers, params.lru_size, params.replicas, params.seed)
        jet = JetRing(workers, horizon, params.lru_size, params.replicas, params.seed)
        
    return jet, baseline, workers, horizon
