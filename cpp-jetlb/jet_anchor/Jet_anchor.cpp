#include "Jet_anchor.h"

Jet::Jet(vector<FiveTuple> servers, int capacity, int horizon, int seed, bool baseline) :
	m_horizon(horizon),
	m_capacity(capacity),
	m_anchorhash(AnchorHash(capacity, servers.size(), seed, horizon)),
	m_baseline(baseline)
{
	assert(servers.size() + horizon <= capacity && "Jet::Jet: servers.size() + horizon > capacity");
	assert(((!baseline) || horizon == 0) && "Baseline has no horizon");

	// init bijection
	m_b2s = new FiveTuple[capacity];
	for (int bucket = 0; bucket < capacity; bucket++)
	{
		if (bucket < servers.size())
		{
			m_b2s[bucket] = servers[bucket];
			m_s2b[servers[bucket]] = bucket;
		}
	}
}

Jet::~Jet()
{
	delete[] m_b2s;
}

void Jet::AddServer(const FiveTuple& server)
{
	int bucket = m_anchorhash.UpdateNewBucket();

	assert(!m_s2b[server] && "Jet::AddServer: server allready exists");

	m_b2s[bucket] = server;
	m_s2b[server] = bucket;
}

void Jet::RemoveServer(const FiveTuple& server)
{
	auto it = m_s2b.find(server);

	assert(it != m_s2b.end() && "Jet::RemoveServer: server not found");

	int bucket = it->second;

	m_anchorhash.UpdateRemoval(bucket);
	m_s2b.erase(server);
}

const FiveTuple Jet::GetServer(const FiveTuple& connID)
{
	auto it = m_ct.find(connID);
	if (it != m_ct.end())
	{
		return it->second;
	}

	auto bucket_track_pair = m_anchorhash.ComputeBucket(connID.ft, FT_LEN);

	int bucket = bucket_track_pair.first;
	bool track = m_baseline || bucket_track_pair.second;

	if (track)
	{
		m_ct[connID] = m_b2s[bucket];
	}
	
	return m_b2s[bucket];
}

void Jet::RemoveConnection(const FiveTuple& connID)
{
	m_ct.erase(connID);
}
