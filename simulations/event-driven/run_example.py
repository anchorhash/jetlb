"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os

seed = 12345
num_servers = 468  # CHEETAH: 468 backend servers
simulation_time = 1000  # sec

# connection_target_list = [20*10**3*i for i in range(1,12,2)]
connection_target_list = [100*10**3]  # CHEETAH: 20K-200K connections

# update_rate_list = [1, 2, 5, 10, 20, 40]  # CHEETAH: 1.5-80 backend updates per minute
update_rate_list = [10]

# lru_size_to_connection_target_ratio_list = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
lru_size_to_connection_target_ratio_list = [0.25]

# ch_type_list = ['anchor', 'hrw_table', 'ring', 'hrw']
ch_type_list = ['anchor']

# num_horizon_list = [5, 12, 24, 47]
num_horizon_list = [int(num_servers*0.15)]

total_sim = len(connection_target_list) \
            * len(update_rate_list) \
            * len(lru_size_to_connection_target_ratio_list) \
            * len(ch_type_list) \
            * len(num_horizon_list)

finished_sim = 0
for ch_type in ch_type_list:
    for connection_target in connection_target_list:
        for update_rate in update_rate_list:
            for lru_size_to_connection_target_ratio in lru_size_to_connection_target_ratio_list:
                for num_horizon in num_horizon_list:
                    command = 'python3 hadoop_test.py'
                    command += ' --simulation_time {}'.format(simulation_time)
                    command += ' --num_servers {}'.format(num_servers)
                    command += ' --connection_target {}'.format(connection_target)
                    command += ' --update_rate {}'.format(update_rate)
                    command += ' --lru_size {}'.format(
                        int(lru_size_to_connection_target_ratio*connection_target))
                    command += ' --ch_type {}'.format(ch_type)
                    command += ' --num_horizon {}'.format(num_horizon) 
                    command += ' --seed {}'.format(seed)
                    command += ' --file_name {}_example'.format(ch_type)

                    with open('./results/' +
                              '{}_example.logger.txt'.format(ch_type), 'a+') as filehandle:
                        filehandle.write('started simulation {}/{}\n'.format(
                            finished_sim+1, total_sim))
                        filehandle.write('running: ' + command + '\n')
                    os.system(command)

                    with open('./results/' +
                              '{}_example.logger.txt'.format(ch_type), 'a+') as filehandle:
                        filehandle.write('finished simulation {}/{}\n'.format(
                            finished_sim+1, total_sim))
                                
                    finished_sim += 1
                    print("finished sim {}/{}".format(finished_sim, total_sim))
