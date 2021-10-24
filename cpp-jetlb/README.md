# Jet C++ implementation

Jet is implemented with different consistent hashes:
1. AnchorHash
2. Table-based HRW 

## Jet API

- All implementations share the same API.
- All implementations use `robin_hood::unordered_map` as the connection tracking module.
- All implementations use `FiveTuple` and `FiveTupleHasher` structs (defined in `defs.h`) to represent unique ids (both for connections and servers).


## Jet Anchorhash (in folder `jet_anchor`)
- A Jet implementation using AnchorHash as the consistent hash module.
- With this implementation the _caller must maintain the horizon set_ and declare the _maximal horizon size_ at initialization.
  
### Constructor 
```C++
Jet::Jet(vector<FiveTuple> servers, int capacity, int horizon, int seed, bool baseline)
```
#### Arguments:
- `servers`: vector of worker server ids
- `capacity`: maximal number of servers (workers and horizon)
- `horizon`: maximal size of horizon (horizon set is maintained by the caller)
- `seed`:  seed for random generators (for reproducability)
- `baseline`: should be `false` (otherwise full connection tracking is used instead of Jet)  

### Get Server
```C++
const FiveTuple Jet::GetServer(const FiveTuple& connID)
```
Computes a destination for a connection with a given id.

This is the main function of Jet. It firsts checks if the connection id is already known and tracked in the connection tracking module. If so, it returns the tracked destination (to maintain PCC). Otherwise, it computes the destination (among current worker servers) based on a consistent hash (AnchorHash) of the connection ID. Jet selectively decides whether to track the connection, based on the horizon.
#### Arguments:
`connID`: unique id of the connection
#### Returns:
Server id

### Add Server
```C++
void Jet::AddServer(const FiveTuple& server)
```
- Adds a worker server.
- The added server should have been in the horizon set for a warmup period.
- Caller must remove the added server from the horizon set before calling this function.
- Caller may add a new server to the horizon set to replace the added server.
#### Arguments:
`server`: unique id of the server

### Remove Server
```C++
void Jet::RemoveServer(const FiveTuple& server)
```
- Removes a worker server.
- Server must be in the worker set.
- Caller may add the removed server to the horizon set, provided its current size is less than the declared maximal size.
#### Arguments:
`server`: String representning a unique id of the server

### Remove Connection
```C++
void Jet::RemoveConnection(const FiveTuple& connID)
```
- Stop tracking a connection (e.g., upon FIN).
- This deletes the connection information from the connection tracking module (if it was tracked).
- This implementation does _not_ employ any eviction policy. Caller must remove stale connections explicitly.
#### Arguments:
`connID`: String representning a unique id of the connection


## Jet HRW (in folder `jet_hrw`)
- A Jet implementation using table-based Highest Random Weight (HRW) as the consistent hash module.
- This implementation maintains a fixed size lookup table, using HRW consistent hash to set the destination server for each table row.  
  A (standard) hash is used to map each connection id to a table row; then the row value determines the connection's destination.  
  After every change in the worker set, Jet updates the detination only for the affected table rows (typical table-based consistent hashes recompute the entire table). 

### Constructor 
```C++
JetHRW::JetHRW(vector<FiveTuple> workers, vector<FiveTuple> horizon, int capacity, int seed, bool baseline)
```
#### Arguments:
- `workers`: vector of worker server ids
- `horizon`: vector of horizon server ids
- `capacity`: maximal number of servers; used to calculate size of lookup table (filled by HRW)
- `seed`:  seed for random generators (for reproducability)
- `baseline`: should be `false` (otherwise full connection tracking is used instead of Jet)  

### Get Server
```C++
const FiveTuple JetHRW::GetServer(const FiveTuple& connID)
```
Computes a destination for a connection with a given id.

This is the main function of Jet. It firsts checks if the connection id is already known and tracked in the connection tracking module. If so, it returns the tracked destination (to maintain PCC). Otherwise, it computes the destination (among current worker servers) based on a consistent hash (table-based HRW) of the connection ID. Jet selectively decides whether to track the connection, based on the horizon.
#### Arguments:
`connID`: unique id of the connection
#### Returns:
Server id

### Add Worker
```C++
void JetHRW::AddWorkerServer(const FiveTuple& server)
```
- Adds a worker server from the horizon (and removes it from the horizon set).
- Caller must make sure that the added server is in the horizon set.
- The added server should have been in the horizon set for a warmup period.
#### Arguments:
`server`: unique id of the server

### Remove Worker 
```cpp
void JetHRW::RemoveWorkerServer(const FiveTuple& server)
```
- Removes a worker server.
- The removed server must be in the worker set.
- The removed server is _not_ added automatically to the horizon set. Caller may add it by calling `AddHorizonServer`.
#### Arguments:
`server`: String representning a unique id of the server

### Add Horizon
```cpp
void JetHRW::AddHorizonServer(const FiveTuple& server)
```
- Adds a new server to the horizon set (warmup for a new server in the system).
- Caller must make sure that the added server is not in the worker or horizon sets.
#### Arguments:
`server`: unique id of the server

### Remove Horizon
```cpp
void JetHRW::RemoveHorizonServer(const FiveTuple& server)
```
- Removes a server from the horizon set (remove permamnently).
- Server must be in the horizon set.
#### Arguments:
`server`: String representning a unique id of the server

### Remove Connection
```cpp
void JetHRW::RemoveConnection(const FiveTuple& connID)
```
- Stop tracking a connection (e.g., upon FIN).
- This deletes the connection information from the connection tracking module (if it was tracked).
- This implementation does _not_ employ any eviction policy. Caller must remove stale connections explicitly.
#### Arguments:
`connID`: String representning a unique id of the connection
  

# Code credits

## xxHash - Extremely Fast Hash algorithm

1. Copyright (C) 2012-2020 Yann Collet
2. See header file at xxhash/xxhash.h for lisence (BSD 2-Clause License)
3. See https://www.xxhash.com and https://github.com/Cyan4973/xxHash

## robinhoodmap - Fast & memory efficient hashtable based on robin hood hashing for C++11/14/17/20

1. Copyright (c) 2018-2020 Martin Ankerl <http://martin.ankerl.com>
2. See header file at robinhoodmap/robin_hood.h for lisence (MIT License)
3. See https://github.com/martinus/robin-hood-hashing

## genzipf.c - generate Zipf distributed traces

1. This tool has been developed by Ken Christensen at the University of South Florida
2. See: genzipf.c at https://www.csee.usf.edu/~kchriste/tools/toolpage.html

## AnchorHash: A Scalable Consistent Hash

1. See paper: https://arxiv.org/abs/1812.09674
2. Official repository: https://github.com/anchorhash/cpp-anchorhash
