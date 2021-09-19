#include "Jet_hrw.h"

JetHRW::JetHRW(vector<FiveTuple> workers, vector<FiveTuple> horizon, int capacity, int seed, bool baseline) :
	m_capacity(capacity),
	m_hrw(HRW(workers, horizon, capacity, seed)),
	m_baseline(baseline)
{
	assert(workers.size() + horizon.size() <= capacity && "Jet::Jet: servers.size() + horizon.size() > capacity");
	assert( ((!baseline) || horizon.size() == 0) && "Baseline has no horizon");
}

JetHRW::~JetHRW()
{
	
}

void JetHRW::AddWorkerServer(const FiveTuple& server)
{
	m_hrw.AddWorkerServer(server);
}

void JetHRW::RemoveWorkerServer(const FiveTuple& server)
{
	m_hrw.RemoveWorkerServer(server);
}

void JetHRW::AddHorizonServer(const FiveTuple& server)
{
	m_hrw.AddHorizonServer(server);
}

void JetHRW::RemoveHorizonServer(const FiveTuple& server)
{
	m_hrw.RemoveHorizonServer(server);
}

const FiveTuple JetHRW::GetServer(const FiveTuple& connID)
{
	auto it = m_ct.find(connID);
	if (it != m_ct.end())
	{
		return it->second;
	}

	auto server_track_pair = m_hrw.ComputeServer(connID.ft, FT_LEN);
	const FiveTuple server = server_track_pair.first;
	bool track = m_baseline || server_track_pair.second;

	if (track)
	{
		m_ct[connID] = server;
	}
	
	return FiveTuple(server);
}

void JetHRW::RemoveConnection(const FiveTuple& connID)
{
	m_ct.erase(connID);
}
