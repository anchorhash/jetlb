"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os
import sys

# sample without repetitions
from random import sample

import numpy as np
import numpy.random as random

# add parent folder to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
jetlb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir, 'py-jetlb')
sys.path.insert(0, os.path.abspath(jetlb_dir))

# JET
from jet_utils import parse_args, gen_jets, get_random_string

# Logger
from logger import Logger

# Trace
from hadoop.event_manager import EventsManager


if __name__ == "__main__":
    params = parse_args()
    random.seed(params.seed)
    test_jet, test_baseline, workers, horizon = gen_jets()
        
    # trace
    em = EventsManager(connection_target=params.connection_target, update_rate=params.update_rate)
    
    # logger
    logger = Logger(params)

    # sim time
    T = params.simulation_time
    
    # initial time
    time = 0
    update_time = T//100
    
    # print stats
    print_stat = False
    
    # possible events:
    # 1. time, "new-connection", conn_id
    # 2. time, "del-connection", conn_id
    # 3. time, "new_server", None
    # 4. time, "kil_server", None

    # complete pass over keys
    while time < T:
        res = em.next()
        try:
            time, event, key = res
        except:
            print(res)
            raise Exception("failed to unpack event")

        if time > update_time:
            print('sim progress is {}%.'.format(int(100 * time / T)))
            update_time += T//100
            print_stat = True
                       
        if event == "new-connection":
            jet_server = test_jet.get_destination(key)
            baseline_server = test_baseline.get_destination(key)
            
            if jet_server != baseline_server:
                print("Destination by JET: {}".format(jet_server))
                print("Destination by FCT: {}".format(baseline_server))
                print("Destination by LOG: {}".format(logger.get_destination(key)))
                connection_mass, start_time, end_time = em.flows_spec[key]
                raise Exception("server mismatch: connection_mass {} start_time {} end_time {}".format(connection_mass, start_time, end_time))                
            
            logger.add_new_connection(key, baseline_server)

        elif event == "del-connection":
            jet_server = test_jet.get_destination(key)
            baseline_server = test_baseline.get_destination(key)
            log_server = logger.get_destination(key)
            
            if baseline_server != log_server or jet_server != log_server:
                connection_mass, start_time, end_time = em.flows_spec[key]
                print("#"*30)
                print("Server mismatch: connection_mass {} start_time {} end_time {}".format(connection_mass, start_time, end_time))
                print("Destination by FCT: {}".format(baseline_server))
                print("Destination by JET: {}".format(jet_server))
                print("Destination by LOG: {}".format(log_server))
                print("#"*30)             
                
                if baseline_server != log_server:                                
                    logger.record_broken_connection('fct', key, connection_mass, start_time, end_time)                
                if jet_server != log_server:                                
                    logger.record_broken_connection('jet', key, connection_mass, start_time, end_time)  
                                            
            test_jet.remove_connection(key)
            test_baseline.remove_connection(key)
            
            em.del_spec_coneciton(key)
            
            logger.remove_connection(key)

        elif event == "new-server":
            server_to_add = horizon[0]
            
            horizon.remove(server_to_add)
            workers.append(server_to_add)
            
            test_jet.add_working_server(server_to_add)
            test_baseline.add_working_server(server_to_add)
            
            logger.add_server(server_to_add, time)

            if len(horizon) < params.num_horizon:
                horizon_to_add = get_random_string(16)
                horizon.append(horizon_to_add)
                test_jet.add_horizon_server(horizon_to_add)

            print("added server {}".format(server_to_add))
            
            # perform pcc check for all active keys after server addition
            active_connections = em.get_active_connections(time)
            
            # random shuffle to avoid patterns
            np.random.shuffle(active_connections)
            
            for key in active_connections:
                jet_server = test_jet.get_destination(key)
                baseline_server = test_baseline.get_destination(key)
                log_server = logger.get_destination(key)
                
                if baseline_server != log_server or jet_server != log_server:
                    connection_mass, start_time, end_time = em.flows_spec[key]
                    
                    print("#"*30)
                    print("Server mismatch: connection_mass {} start_time {} end_time {}".format(connection_mass, start_time, end_time))
                    print("Destination by FCT: {}".format(baseline_server))
                    print("Destination by JET: {}".format(jet_server))
                    print("Destination by LOG: {}".format(log_server))
                    print("#"*30)             
                    
                    if baseline_server != log_server:                                
                        logger.record_broken_connection('fct', key, connection_mass, start_time, end_time)                
                    if jet_server != log_server:                                
                        logger.record_broken_connection('jet', key, connection_mass, start_time, end_time)              

        elif event == "kil-server":
            server_to_remove = sample(workers, 1)[0]
            
            workers.remove(server_to_remove)

            test_jet.remove_working_server(server_to_remove)
            test_baseline.remove_working_server(server_to_remove)
            
            logger.remove_server(server_to_remove, time)
            broken_connections = logger.del_broken_connections(server_to_remove)

            if not params.no_server_tag_recycling:
                horizon.append(server_to_remove)
                if len(horizon) > params.num_horizon:
                    horizon.remove(server_to_remove)
                    test_jet.remove_horizon_server(server_to_remove)
            else:
                test_jet.remove_horizon_server(server_to_remove)
                new_horizon = get_random_string(16)
                if len(horizon) < params.num_horizon:
                    horizon.append(server_to_remove)
                    test_jet.add_horizon_server(new_horizon)

            print("removed server {}".format(server_to_remove))
            
            try:
                print("it received {} connections.".format(len(broken_connections)))
                em.del_stale_conecitons(broken_connections)            
            except:
                print("it received 0 connections.")
            
            # perform pcc check for all active keys after server removal
            active_connections = em.get_active_connections(time)

            # random shuffle to avoid patterns
            np.random.shuffle(active_connections)
            
            for key in active_connections:
                jet_server = test_jet.get_destination(key)
                baseline_server = test_baseline.get_destination(key)
                log_server = logger.get_destination(key)
                
                if baseline_server != log_server or jet_server != log_server:
                    connection_mass, start_time, end_time = em.flows_spec[key]
                    print("#"*30)
                    print("Server mismatch: connection_mass {} start_time {} end_time {}".format(connection_mass, start_time, end_time))
                    print("Destination by FCT: {}".format(baseline_server))
                    print("Destination by JET: {}".format(jet_server))
                    print("Destination by LOG: {}".format(log_server))
                    print("#"*30)             
                    
                    if baseline_server != log_server:                                
                        logger.record_broken_connection('fct', key, connection_mass, start_time, end_time)                
                    if jet_server != log_server:                                
                        logger.record_broken_connection('jet', key, connection_mass, start_time, end_time)  

        else:
            raise Exception("unknown event")

        # stats every 1%
        if print_stat:
            print_stat = False
            
            server_loads = logger.get_server_loads()
            print('sim with app. {} commenctions. maximum over-subscription is {:.3f}'.format(
                em.get_params()[0], np.max(server_loads) / np.mean(server_loads)))

    # print broken connection stats
    logger.print_broken_connection_stats()
    
    # print backend stats
    logger.print_backend_stats()

    # write results to file
    logger.write_results()
