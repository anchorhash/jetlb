#ifndef HRW_H
#define HRW_H


#include "../defs.h"

using namespace std;

/** Class declaration */
class HRW {

private:

	// Workers
	vector<FiveTuple> m_workers;

	// Horizon  
	vector<FiveTuple> m_horizon;

	// Random seed
	uint64_t m_seed;

	// table		
	std::pair<FiveTuple, bool> *m_table;
	int m_table_size;
	int m_mask;

	// capacity
	uint32_t m_capacity;

	// hrw score
	uint64_t RowKey(int row);
	uint64_t ServerScore(const FiveTuple* server, uint64_t key);

	// best
	std::pair<const FiveTuple, bool> BestServer(vector<FiveTuple> workers, vector<FiveTuple> horizon, uint64_t key);


public:

	HRW(vector<FiveTuple> workers, vector<FiveTuple>  horizon, int capacity, int seed);

	~HRW();

	const std::pair<FiveTuple, bool> ComputeServer(const char* connID, int len);

	void AddWorkerServer(const FiveTuple& server);

	void RemoveWorkerServer(const FiveTuple& server);

	void AddHorizonServer(const FiveTuple& server);

	void RemoveHorizonServer(const FiveTuple& server);
};

#endif