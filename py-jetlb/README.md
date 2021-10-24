# Jet Python implementation

JET implemented with different consistent hashes:
1. AnchorHash
2. Highest Random Weight (HRW)
3. Ring Hash
4. Table-based HRW 

## Jet API

All implementations share the same API, excpet initialization (see below).  
All implementations use an LRU cache as the connection tracking module (i.e., a table of fixed size that uses an LRU eviction policy).

### `get_destination`
Computes a destination for a connection with a given id (e.g., 5-tuple).

This is the main function of Jet.  
It firsts checks if the connection id is already known and tracked in the connection tracking module.  
If so, it returns the tracked destination (to maintain PCC).  
Otherwise, it computes the destination (among current worker servers) based on a consistent hash of the connection ID.  
Jet selectively decides whether to track the connection, based on the horizon.
```python
def get_destination(self, connection_id)
```
#### Arguments:
`connection_id`: String representing a unique id of the connection
#### Returns:
String represting a unique id of the destination server


### `add_working_server`
Adds a worker server from the horizon set

- The added server must be in the horizon set (and is automatically removed from it)
- The added server should have in the horizon set for a warm-up period.
```python
def add_working_server(self, server)
```
#### Arguments:
`server`: String representning a unique id of the server


### `remove_working_server`
Removes a worker server

- The removed server must be in the worker set.
- The removed server is automatically added to the horizon set. 
```python
def remove_working_server(self, server)
```
#### Arguments:
`server`: String representning a unique id of the server


### `add_horizon_server`
Adds a new server to the horizon set (warmup for a new server in the system).

- The added server must not be in either the worker or horizon sets.
```python
def add_horizon_server(self, server)
```
#### Arguments:
`server`: String representning a unique id of the server


### `remove_horizon_server`
Removes a server from the horizon set (remove permamnently).

- The removed server must be in the horizon set.
```python
def remove_horizon_server(self, server)
```
#### Arguments:
`server`: String representning a unique id of the server


### `remove_connection`
Stop tracking a connection (e.g., upon FIN)

- This deletes the connection information from the connection tracking module (if it was tracked).
- This implementation employs an LRU eviction policy. Caller may remove stale connections explicitly.
```python
def remove_connection(self, connection_id)
```
#### Arguments:
`connection_id`: String representning a unique id of the connection


## Initialization of different Jet implementations

#### Common arguments:
- `workers`: List of Strings representning unique ids of the worker servers 
- `horizon`: List of Strings representning unique ids of the horizon servers
- `lru_size`: Int capacity of the connection tracking table
- `seed`: (optinal, default:`42`) Int seed for random generators (for reproducability)

`workers` and `horizon` should not contain duplicates and should not intersect.


### anchorhash (`jet_anchorhash.JetAnchorHash`)
A Jet implementation using AnchorHash as the consistent hash module
```python
def __init__(self, workers, horizon, lru_size, capacity=100, seed=42)
```
#### Arguments:
`capacity`: (optinal, default:`100`) Int maximal number of servers (both horizon and workers set)


### hrw JetHRW (`jet_hrw.JetHRW`)
A Jet implementation using Highest Random Weight (HRW) as the consistent hash module
```python
def __init__(self, workers, horizon, lru_size, seed=42)
```
#### Arguments:
none


### ring (`jet_ring.JetRing`)
A Jet implementation using Ring as the consistent hash module
```python
def __init__(self, workers, horizon, lru_size, replicas=100, seed=42)
```
#### Arguments:
replicas: (optinal, default:`100`) Int number of virtual nodes for each server on the ring


### table_hrw (`jet_table.JetTableHRW`)
A Jet implementation using a table-based HRW as the consistent hash module (table is filled using HRW)

- This implementation maintains a fixed size lookup table, using HRW consistent hash to set the destination server for each table row.
  A (standard) hash is used to map each connection id to a table row; then the row value determines the connection's destination.
  After every change in the worker set, Jet updates the detination only for the affected table rows (typical table-based consistent hashes recompute the entire table).
```python
def __init__(self, workers, horizon, lru_size, table_size=1000, seed=42)
```
#### Arguments:
table_size: (optinal, default:`1000`) Int size of the table
    

## Examples

```python
from jet_anchorhash import JetAnchorHash

JetAnchorHash
Out: jet_anchorhash.JetAnchorHash

workers = ['server_1', 'server_2', 'server_3']
horizon = ['server_4', 'server_5']

workers
Out: ['server_1', 'server_2', 'server_3']

horizon
Out: ['server_4', 'server_5']

# initialize jet with connection tracking capacity of 1000
jet = JetAnchorHash(workers, horizon, 1000, capacity=100, seed=42)

jet
Out: <jet_anchorhash.JetAnchorHash at 0x2c48b0d7880>

# map a few connections
jet.get_destination('key_1')
Out: 'server_2'

jet.get_destination('key_2')
Out: 'server_1'

# change in working server
jet.add_working_server('server_4')

jet.horizon
Out: ['server_5']

jet.workers
Out: ['server_1', 'server_2', 'server_3', 'server_4']

jet.get_destination('key_1')
Out: 'server_2'

jet.get_destination('key_2')
Out: 'server_1'

jet.get_destination('key_3')
Out: 'server_1'

jet.get_destination('key_4')
Out: 'server_2'

jet.get_destination('key_5')
Out: 'server_4'

# another change
jet.remove_working_server('server_1')

jet.workers
Out: ['server_2', 'server_3', 'server_4']

jet.horizon
Out: ['server_5', 'server_1']

# server_1 is not a worker anymore, change does not violate PCC
jet.get_destination('key_2')
Out: 'server_3'

# add it back
jet.add_working_server('server_1')

jet.horizon
Out: ['server_5']

jet.workers
Out: ['server_2', 'server_3', 'server_4', 'server_1']

# key_2 is tracked with server_3 as the destination to maintain PCC
jet.get_destination('key_2')
Out: 'server_3'

# permanently remove a server
jet.remove_horizon_server('server_5')

jet.horizon
Out: []

jet.workers
Out: ['server_2', 'server_3', 'server_4', 'server_1']

# add a new server and warmup
jet.add_horizon_server('server_6')

jet.horizon
Out: ['server_6']

jet.workers
Out: ['server_2', 'server_3', 'server_4', 'server_1']
```



# Credits

Our python simulations are inspired by:
1. See (1) CHEETAH and (2) SilkRoad papers: (1) https://www.usenix.org/system/files/nsdi20-paper-barbette.pdf, (2) https://dl.acm.org/doi/pdf/10.1145/3098822.3098824
2. See simulations repository: 
    - hadoop stats: https://github.com/cheetahlb/simulations/tree/master/algorithm_simulation/data
    - code: https://github.com/cheetahlb/simulations
