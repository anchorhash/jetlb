"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

from matplotlib.ticker import FuncFormatter

os.system('python3 parse_fig5.py > anchor_fig5.csv')
data = pd.read_csv("anchor_fig5.csv")
size = 18

markers = ["s", "P", "h", "X"]
colors = ["teal", "darkorchid", "maroon", "navy"]

lru_size = 100000
update_rates = np.unique(data.update_rate.values)
total_connections = int(np.ceil((np.mean(data['total connections'])/10**6))*10**6)

fig, ax = plt.subplots(1,1, figsize=(8,4))

mi = 0
for update_rate in update_rates:
    if update_rate in [2,5]:
        continue
    cdata = data[data['update_rate'] == update_rate]
    yvalue = cdata.groupby(['connection_target'])['maximum over-subscription'].mean()
    xvalue = np.unique(data.connection_target.values)
    ax.plot(xvalue, yvalue, label='Update rate {}'.format(update_rate),
            marker=markers[mi], markevery=[0,-1], markersize=12, color=colors[mi])
    mi += 1

ax.minorticks_on()

ax.set_xlabel("Connection rate", fontsize=size)
ax.set_ylabel("Maximum \nover-subscription", fontsize=size)

ax.tick_params(axis='x', labelsize=size)
ax.tick_params(axis='y', labelsize=size)

ax.xaxis.set_major_formatter(FuncFormatter(lambda x,y : '{:,.0f}'.format(x)))

plt.grid(color='lightgray', linestyle='-', linewidth=0.5, which='major')
plt.grid(color='lightgray', linestyle=':', linewidth=0.1, which='minor')

ax.locator_params(axis='x', nbins=6)

plt.tight_layout()
plt.legend(fontsize=size-4)
plt.show()
plt.savefig("fig5.pdf", bbox_inches='tight')
