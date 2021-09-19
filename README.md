# Load Balancing with JET: Just Enough Tracking for Connection Consistency

JET is am algorithmic framework for hash-based stateful load balancers that uses much smaller connection tracking tables (typically a about 10% of full connection tracking). It is described in our paper:

[Load Balancing with JET: Just Enough Tracking for Connection Consistency](FIXME)

**Paper Abstract:** Hash-based stateful load-balancers employ connection tracking to avoid per-connection consistency (PCC) violations that lead to broken connections. In this paper, we propose Just Enough Tracking (JET), a new algorithmic framework that significantly reduces the size of the connection tracking tables without increasing PCC violations.

Under mild assumptions on how backend servers are added, JET adapts consistent hash techniques to identify which connections do not need to be tracked. We provide a model to identify these safe connections and a pluggable framework with appealing theoretical guarantees that supports a variety of consistent hash and connection tracking modules.

We implemented JET in two different environments and with four different consistent hash techniques. Using a series of evaluations, we demonstrate that JET requires connection tracking tables that are an order of magnitude smaller than those required with full connection tracking while preserving PCC and balance properties. In addition, JET often increases the lookup rate due to improved caching.

## Code
This repository contains the code used to create the figures for the evaluation section in the paper.

- `cpp-jetlb` is a C++ implementation of JET
- `py-jetlb` is a Python implemenation of JET
- `simulation` contains the code to create the figures from 3 types of evaluations
  - Event-driven simulation
  - Sythetic traces
  - Real-traces

# Reproduce our results

## System Requirements
1. Install needed `python3` packages from `requirements.txt`
   - go into `py-jetlb`
   - run 
     ```bash
     pip3 install -r requirements.txt
     ```
 
## Event-driven simulation
1. Go into `simulations/event-driven`
2. Run
   ```bash
   python3 run_example.py
   ```
   - This script runs a single run of the simulation; namely, a single point in our figures. Note that, running the full simulations may take several days. During the run, the progress of the simulation as well as additional data are printed to the standard output
   - Once the simulation is complete (may take 1-2 hours), the results of this run can be examined in `simulations/even-driven/results/anchor_example.txt`. This file shows: 
   - The results of this run can be examined in `simulations/even-driven/results/anchor_example.txt`. This file shows:
     ```
     ****************************************************************************************************
     Parameters: ch_type:anchor, num_horizon:70, no_server_tag_recycling:False, num_servers:468, lru_size:25000, seed:12345, capacity:936, replicas:300, num_keys:1000000, connection_target:100000, update_rate:10.0, simulation_time:1000, file_name:anchor_example, 
     JET broken connections: 0
     FCT broken connections: 7417
     removed server times: [0, 7.7172900914043225, 19.192523833050437, 29.57152932488366, 30.7036687347961, 31.022016496491304, 37.13196789260673, ..., 997.4677108232434]
     added server times: [149.92592033305044, 160.30492582488367, 161.75541299649132, 187.04254069140433, 188.38889396897346, 190.24564819260672, 196.15485731135527, 196.40565753479612, 197.12428456277928, ..., ]
     maximum over-subscription is 1.238
     total connections: 4687530
     ****************************************************************************************************
     ``` 
     - the parameters of the simulation
     - the number of PCC violations ("broken connections") by full connection-as compared to  JET
     - the update events (additions/removals)
     - the maximal over subscription (imbalance)
     - the total number of connections for the entire simulation
 3. Reproduce figure 3
    ```bash
    python3 run_fig3.py
    pushd results
    python3 plot_fig3.py
    popd
    ```
    - this creates figure 3 as `result/anchor_fig3.pdf`
    - as mentioned, a full run may take several days
    - to reduce run time, edit `run_fig3.py`, line 13: reduce `connection_target_list` from `100K` to `10K` or even `1K` (the latter should run in less than two hours). The results will still reflect the same trends that are presented in the paper, but absolute numbers would be different.
 4. Reproduce figures 4a, 4b, and 5
    - same as for figure 3, just replace with the corresponding numbered scripts
    - same as for figure 3, run time may be reduced by adjusting `connection_target_list`

## Synthetic traces
1. Compile JET C++
   - Go into `simulations/trace-based`
   - run 
     ```bash
     make
     ```
 
2. Generate synthetic traces (zipf distribution)
   - Go into `simulations/trace-based/zipf_traces` 
   - To create the synthetic traces
     ```bash
     make
     ./gentzipf_bash
     ```
   
3. Reproduce figure 6b
   - Go into `simulations/trace-based`
   - run 
     ```bash
     python3 plot_fig6b.py
     ```
   
4. Reproduce figures 7a and 7b
   - Go into `simulations/trace-based`
   - run 
     ```bash
     python3 run_fig7.py
     python3 plot_fig7a.py
     python3 plot_fig7b.py
     ```
   - A full run may take about half a day. To reduce run time it is possible to average over fewer experiments and or use shorter traces. For example, 
     ```bash
     python3 run_fig7.py --trials 3 --trace_length 1000000
     python3 plot_fig7a.py --trials 3
     python3 plot_fig7b.py --trials 3
     ``` 
     will plot an average over only `3` trials and use only the first  `1000000` 5-tuples from each trace. 


## Real traces

1. Compile JET C++
   - Go into `simulations/trace-based`
   - run 
     ```bash
     make
     ```
 
2. Fetch and parse real traces
   - Download a trace `pcap` file
   - Go into `simulations/trace-based/real_traces`    
   - run
     ```bash
     pcap_to_trace.py --path PATH_TO_PCAP_FILE --file_name BINARY_TRACE_FILENAME
     ```
     (the script ignores non-TCP packets)
   - This would generate a binary file similar to `simulations/trace-based/real_traces/toy.bin` encoding each 5-tuple with `13` bytes.   
   
3. Reproduce figure 6a
   - Go into `simulations/trace-based`
   - run 
     ```bash
     python3 plot_fig6a.py --trace_path PATH_TO_BINARY_TRACE --trace_length TRACE_LENGTH
     ```
   - For example, 
     ```bash
     python3 plot_fig6a.py --trace_path real_traces/toy.bin --trace_length $(wc -c real_traces/toy.bin | awk '{print $1/13}')
     ```
  
4. Reproduce Tables 1, 2
   - Go into `simulations/trace-based`
   - run 
     ```bash
     python3 run_table.py --trace_path PATH_TO_BINARY_TRACE --result_fn RESULT_FILENAME --trials NUMBER_OF_SEEDS --trace_length TRACE_LENGTH
     ```
   - For example, 
     ```bash
     python3 run_table.py --trace_path real_traces/toy.bin --result_fn toy --trials 3 --trace_length $(wc -c real_traces/toy.bin | awk '{print $1/13}')
     ```
     (averages over `3` trials and saves to `toy`) 
   - To parse data and output summary run 
     ```bash
     python3 plot_table.py --result_fn PATH_TO_RESULTS_FILE --trials NUMBER_OF_SEEDS
     ```
   - For example, 
     ```bash
     python3 plot_table.py --result_fn toy --trials 3
     ```


# Algorithm

Bellow you can find the pseudocode for JET with different consistent hashing techniques. See paper for details.

## JET Framework
```hs
- CT    Connection tracking table
- CH    Consistent hash
- W     worker set
- H     Horizon set
- k     Connection key (5-tuple) 
- s     A backend server

GetDestination(K)
    s ← CT[k]
    IF not s:
        s ← CH(W, k)
    IF not s=CH(W ∪ H, k):  // Should track?
        CT[K] ← s
    Return s

AddWorkingServer(s)         // can add workers only from H
    reomve s from H
    add s to W
        
RemoveWorkingServer(s)      // removed worker may be added later
    remove s from W
    add s to H
        
AddHorizonServer(S)
    add s to H

RemoveHorizonServer(S)
    remove s from H
```

## JET with Highest Random Weight (HRW) hash

```hs
GetDestination(k)
    s ← CT[k]
    IF not s:
        s ← ARGMAX_{w ∈ W} HASH(w,k)
    IF hash(s, k) < MAX_{h ∈ H} HASH(h,k):
        CT[k] ← s
    Return s
```
## JET with RING hash

```hs
- RING                Ring data structure, stores values in ring sort order
- RING.Successor(x)   Returns position of first ring entry after x (clockwise)
- W-RING, H-RING      Temporary rings

PopulateRing}(W,H)    // Called to initialize and afer each update
    FOR w ∈ W:
        W-RING[hash(w)] ← (w,False)
    FOR h ∈ H:
        p ← W-RING.Successor(HASH(h))
        w,track ← W-RING[p]
        H-RING[HASH(h)] ← (w,True)
    RING ← W-RING ∪ H-RING      

GetDestination(k)
    s ← CT[k]
    IF not s:
        p ← RING.Successor(HASH(k))
        s,track ← RING[p]
        IF track:
            CT[k] ← s
    Return s
```

## JET with AnchorHash

```hs
- CT            // Connection tracking
- A             // All servers (W, H are subsets of A)
- TR            // Tracking table (True if should track)
- s-HASH()      // hash into the worker set W(s) where
                // W(s) is the worker set right after s was removed
- A-HASH()      // hash into the worker set A
                
GetDestination(k)
    s ← CT[k]
    IF not s:
        s ← A-HASH(k)
        WHILE s is not in W:
            h ← s
            s ← s-HASH(k)
        if h ∈ H:
            CT[k] ← s
    Return s 
```

## JET with Table-based hash that uses HRW hash

```hs
- CH    Consistent hash table
- TR    Tracking table (True if should track)

GetDestination(k)
    s ← CT[k]
    IF not s:
        r ← HASK(k) % size(CH)    // Get table row
        s ← CH[r]
        if TR[r]:
            CT[k] ← s 
    Return s

AddWorkingServer(s)
    remove s from H
    add s to W
    For row r such that TR[r] is True:
        IF HASH(s,r) > HASH(CH[r],r):
            CH[r] ← s
            x ← MAX_{h ∈ H} HASH(h,r)
            TR[r] ← HASH(s,r) < x

RemoveWorkingServer(s)
    remove s from W
    add s to H
    For row r such that CH[r]=s:
        CH[r] ← ARGMAX_{w ∈ W} HASH(w,r)
        TR[r] ← True

AddHorizonServer(s)
    add s to H
    For row r such that TR[r] is False:
        TR[r] ← HASH(s,r) > HASH(CH[r],r)

RemoveHorizonServer(s)
    remove s form H
    For row r such that TR[r] is True:
        x ← MAX_{h ∈ H} HASH(h,r):
        TR[r] ← HASH(CH[r],r) < x
```
