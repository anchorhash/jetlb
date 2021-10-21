# Jet C++ implementation

JET implemented with different consistent hashes:
1. AnchorHash
2. Table-based HRW 

## Jet API

- All implementations share the API explained in the paper.
- All implementations use `robin_hood::unordered_map` as the connection tracking module.
- All implementations use `FiveTuple` and `FiveTupleHasher` (in `defs.h`) to represent unique ids (both for connections and servers).


## Jet Anchorhash (in `jet_anchor`)
- Jet implementations using AnchorHash as the consistent hash module.
- With this implementation the _caller must maintain a fixed-size horizon set_. 
  
### Constructor 
```cpp
Jet::Jet(vector<FiveTuple> servers, int capacity, int horizon, int seed, bool baseline)
```
#### Arguments:
- `servers`: vector of worker server ids
- `capacity`: maximal number of servers (workers and horizon)
- `horizon`: size of horizon
- `seed`:  seed for random generators (for reproducability)
- `baseline`: should be `false` (otherwise full connection tracking is used instead of Jet)  

### Get Server
```cpp
const FiveTuple Jet::GetServer(const FiveTuple& connID)
```
Computes a destination for a connection with a given id
#### Arguments:
`connID`: unique id of the connection
#### Returns:
Server id

### Add Server
```cpp
void Jet::AddServer(const FiveTuple& server)
```
- Adds a worker server.
- Caller must make sure that the added server is in the horizon set and remove it from the horizon set.
- Caller must add a new server to the horizon set to keep a fixed-size horizon.
#### Arguments:
`server`: unique id of the server

### Remove Server
```cpp
void Jet::RemoveServer(const FiveTuple& server)
```
- Removes a worker server.
- Caller must move the server to the horizon set and remove one server permanently to keep a fixed-size horizon.
- Server must be in the worker set.
#### Arguments:
`server`: String representning a unique id of the server

### Remove Connection
```cpp
void Jet::RemoveConnection(const FiveTuple& connID)
```
Stop tracking a connection (e.g., upon FIN)
#### Arguments:
`connID`: String representning a unique id of the connection


## Jet HRW (in `jet_hrw`)
- Jet implementation using table-based Highest Random Weight (HRW) as the consistent hash module

### Constructor 
```cpp
JetHRW::JetHRW(vector<FiveTuple> workers, vector<FiveTuple> horizon, int capacity, int seed, bool baseline)
```
#### Arguments:
- `workers`: vector of worker server ids
- `horizon`: vector of horizon server ids
- `capacity`: maximal number of servers; used to calculate size of lookup table (filled by HRW)
- `seed`:  seed for random generators (for reproducability)
- `baseline`: should be `false` (otherwise full connection tracking is used instead of Jet)  

### Get Server
```cpp
const FiveTuple JetHRW::GetServer(const FiveTuple& connID)
```
Computes a destination for a connection with a given id
#### Arguments:
`connID`: unique id of the connection
#### Returns:
Server id

### Add Worker
```cpp
void JetHRW::AddWorkerServer(const FiveTuple& server)
```
- Adds a worker server from the horizon.
- Caller must make sure that the added server is in the horizon set.
#### Arguments:
`server`: unique id of the server

### Remove Worker 
```cpp
void JetHRW::RemoveWorkerServer(const FiveTuple& server)
```
- Removes a worker server.
- Server must be in the worker set.
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
Stop tracking a connection (e.g., upon FIN)
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
