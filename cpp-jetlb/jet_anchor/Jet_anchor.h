#ifndef JET
#define JET

#include "../defs.h"

using namespace std;

class Jet
{
	// is baseline?
	bool m_baseline;

	// consistent hash
	AnchorHash m_anchorhash;

	// maximum number of servers
	int m_capacity;

	// horizon
	int m_horizon;

	// bijection
	FiveTuple* m_b2s;
	//tsl::robin_map<FiveTuple, int, FiveTupleHasher> m_s2b;
	robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> m_s2b;

public:

	// connection tracking table
	//tsl::robin_map<FiveTuple, FiveTuple, FiveTupleHasher>  m_ct;
	robin_hood::unordered_map<FiveTuple, FiveTuple, FiveTupleHasher>  m_ct;
	int get_ct_table_size() { return m_ct.size(); };

	// constructor
	Jet(vector<FiveTuple> servers, int capacity, int horizon, int seed, bool baseline);

	// destructor
	~Jet();

	void AddServer(const FiveTuple& server);

	void RemoveServer(const FiveTuple& server);

	const FiveTuple GetServer(const FiveTuple& connID);

	void RemoveConnection(const FiveTuple& connID);

};

#endif 

