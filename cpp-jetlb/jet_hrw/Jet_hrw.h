#ifndef JETHRW
#define JETHRW

#include "../defs.h"
#include "../hrw/hrw.h"

using namespace std;

class JetHRW
{
	// is baseline?
	bool m_baseline;

	// consistent hash
	HRW m_hrw;

	// maximum number of servers
	int m_capacity;

	// worker servers
	vector<FiveTuple> m_workers;

	// horizon servers
	vector<FiveTuple> m_horizon;

public:

	// connection tracking table
	//tsl::robin_map<FiveTuple, FiveTuple, FiveTupleHasher>  m_ct;
	robin_hood::unordered_map<FiveTuple, FiveTuple, FiveTupleHasher>  m_ct;
	int get_ct_table_size() { return m_ct.size(); };

	// constructor
	JetHRW(vector<FiveTuple> workers, vector<FiveTuple>  horizon, int capacity, int seed, bool baseline);

	// destructor
	~JetHRW();

	void AddWorkerServer(const FiveTuple& server);

	void RemoveWorkerServer(const FiveTuple& server);

	void AddHorizonServer(const FiveTuple& server);

	void RemoveHorizonServer(const FiveTuple& server);

	const FiveTuple GetServer(const FiveTuple& connID);

	void RemoveConnection(const FiveTuple& connID);

};

#endif 

