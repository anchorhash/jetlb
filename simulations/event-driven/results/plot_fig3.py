"""
    @author: Shay Vargaftik
    @author: Dean H. Lorenz
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

size = 18

update_rates = [1, 2, 5, 10, 20, 40]

os.system('python3 parse_fig3.py > anchor_fig3.csv')
data = pd.read_csv("anchor_fig3.csv")

# connection_rate = 100000
connection_rate = 1000

data = data[data['connection_target'] == connection_rate]
num_horizon = 47
data = data[data['num_horizon'] == num_horizon]

labels = data[data['update_rate'] == 1]['lru_size']

labels_range = np.arange(len(labels))
print(labels)
print(labels_range)

total_connections = int(np.ceil((np.mean(data['total connections'])/10**6))*10**6)

fig, ax = plt.subplots(1,1, figsize=(16,4))
width = 0.1
hpatterns =['..', '||||', 'xx','///','\\\\\\','oo']

for w, update_rate in enumerate(update_rates):
    cdata = data[data['update_rate'] == update_rate]
    ind = range(len(cdata['lru_size']))

    print(cdata['lru_size'])
    print(cdata['FCT broken connections'])

    for x, y in zip(labels_range - width*len(update_rates)/2.0 + w*width,
                    cdata['FCT broken connections']):
        ax.text(x + width/10, y + 3000, y, color='black', rotation=90, fontsize=10)

    hatch=hpatterns[w]
    ax.bar(labels_range + -width*len(update_rates)/2 + (w+0.5)*width,
           cdata['FCT broken connections'],
           label='Full CT (Update rate {})'.format(update_rate),
           width = width, hatch=hatch, fill=True, edgecolor='black')

for w, update_rate in enumerate(update_rates):
    cdata = data[data['update_rate'] == update_rate]

    ind = range(len(cdata['lru_size']))

    print(cdata['lru_size'])
    print(cdata['FCT broken connections'])

    ax.bar(labels_range - width*len(update_rates)/2 + (w+0.5)*width,
           cdata['JET broken connections'], width = width, color='black', hatch='+')

ax.bar(0, 0, color='black', label='JET (Horizon 10%)')
ax.minorticks_on()
ax.set_xticks(labels_range)
ax.set_xticklabels([str(i) for i in labels])

ax.set_xlabel(r"CT table size", fontsize=size)
ax.set_ylabel("PCC violations", fontsize=size)

ax.tick_params(axis='x', labelsize=size)
ax.tick_params(axis='y', labelsize=size)

# colors
bars = ax.patches
print([b.get_hatch() for b in bars])
plt.grid(color='lightgray', linestyle='-', linewidth=0.5, which='major', axis='y')
plt.grid(color='lightgray', linestyle=':', linewidth=0.1, which='minor', axis='y')

ax.set_axisbelow(True)

plt.tight_layout()
plt.legend(fontsize=size-4)
plt.show()
plt.savefig("fig3.pdf", bbox_inches='tight')

