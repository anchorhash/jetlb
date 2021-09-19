"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib.ticker import FuncFormatter

os.system('python3 parse_fig4b.py > anchor_fig4b.csv')
data = pd.read_csv("anchor_fig4b.csv")

size = 18

markers = [">", "<", "^", "v", "o"]

data = data[data['lru_size'] <= 20000]

connection_rate = data['connection_target'][0]
data = data[data['connection_target'] == connection_rate]

total_connections = int(np.ceil((np.mean(data['total connections'])/10**6))*10**6)

fig, ax = plt.subplots(1, 1, figsize=(8, 4))

fct_mean = data.groupby('lru_size')['FCT broken connections'].mean()
lru_size_mean = data[data['num_horizon'] == 5]['lru_size']
ax.plot(lru_size_mean, fct_mean, label='Full CT', color='black', marker=markers[4],
        markevery=[0], markersize=12)

for mi, h in enumerate([5, 12, 24, 47]):
    cdata = data[data['num_horizon'] == h]
    ax.plot(cdata['lru_size'], cdata['JET broken connections'], label='JET ({})'.format(h),
            marker=markers[mi], markevery=[0], markersize=12)

ax.minorticks_on()

ax.set_xlabel("CT table size", fontsize=size)
ax.set_ylabel("PCC violations", fontsize=size)

ax.tick_params(axis='x', labelsize=size)
ax.tick_params(axis='y', labelsize=size)

ax.xaxis.set_major_formatter(FuncFormatter(lambda x,y: '{:,.0f}'.format(x)))
ax.yaxis.set_major_formatter(FuncFormatter(lambda x,y: '{:,.0f}'.format(x)))

ax.locator_params(axis='x', nbins=7)

plt.grid(color='lightgray', linestyle='-', linewidth=0.5, which='major')
plt.grid(color='lightgray', linestyle=':', linewidth=0.1, which='minor')

plt.tight_layout()
plt.legend(fontsize=size-3)
plt.show()
plt.savefig("fig4b.pdf", bbox_inches='tight')

