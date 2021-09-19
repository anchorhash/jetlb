"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import os

seed = 12345
num_servers = 468  # CHEETAH: 468 backend servers
simulation_time = 1000  # sec

update_rate_list = [10]  # fixed
connection_target_list = [100*10**3]  # fixed to 100K. Use 10K or even 1K for a shorter run

lru_size_to_connection_target_ratio_list = [0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
num_horizon_list = [5, 12, 24, 47]
ch_type_list = ['anchor']

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
                    command += ' --lru_size {}'.format(int(lru_size_to_connection_target_ratio*connection_target))
                    command += ' --ch_type {}'.format(ch_type)
                    command += ' --num_horizon {}'.format(num_horizon)
                    command += ' --seed {}'.format(seed)
                    command += ' --file_name {}_fig_4a'.format(ch_type)

                    with open('./results/'
                              + '{}_fig_4a.logger.txt'.format(ch_type), 'a+') as filehandle:
                        filehandle.write('stated simulation {}/{}\n'.format(
                            finished_sim+1, total_sim))
                        filehandle.write('running: ' + command + '\n')

                    os.system(command)

                    with open('./results/'
                              + '{}_fig_4a.logger.txt'.format(ch_type), 'a+') as filehandle:
                        filehandle.write('finished simulation {}/{}\n'.format(
                            finished_sim+1, total_sim))

                    finished_sim += 1
                    print("finished sim {}/{}".format(finished_sim, total_sim))
