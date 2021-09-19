#include "hrw.h"

/** Constructor */
HRW::HRW(std::vector<FiveTuple> workers, std::vector<FiveTuple> horizon, int capacity, int seed) : m_workers(workers),
																								   m_horizon(horizon),
																								   m_capacity(capacity),
																								   m_seed(seed)
{
	assert(workers.size() > 0 && "HRW::HRW: no workers");
	assert(capacity >= (workers.size() + horizon.size()) && "HRW::HRW: capacity < ( workers.size() + horizon.size() )");

	m_table_size = 1;
	for (auto size = m_capacity * 300; size > 0; size >>= 1)
	{
		m_table_size <<= 1;
	}
	m_mask = m_table_size - 1;
	m_table = new std::pair<FiveTuple, bool>[m_table_size];

	for (int row = 0; row < m_table_size; ++row)
	{
		auto key = RowKey(row);
		m_table[row] = BestServer(m_workers, m_horizon, key);
	}

	robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> balance;
	for (auto pserver = balance.begin(); pserver != balance.end(); ++pserver) {
		pserver->second = 0;
	}
	for (int r = 0; r < m_table_size; r++)
	{
		balance[m_table[r].first] += 1;
	}
	auto mins = balance.begin();
	auto maxs = balance.begin();

	// cout << "\nHRW Balance:\n";
	for (auto pserver = balance.begin(); pserver != balance.end(); ++pserver)
	{
		//cout << (pserver->first).ft << ":\t" << pserver->second << endl;
		if (pserver->second > maxs->second) {
			maxs = pserver;
		}
		if (pserver->second < mins->second) {
			mins = pserver;
		}
	}
	// cout << "max:\t" << (maxs->first).ft << ":\t" << maxs->second << endl;
	// cout << "min:\t" << (mins->first).ft << ":\t" << mins->second << endl;
	cout << "HRW load factor:\t" << 1.0 * maxs->second * workers.size() / m_table_size << endl;
	cout << "HRW table size: " << m_table_size << endl;

}

/** Destructor */
HRW::~HRW()
{
	delete[] m_table;
}

// hrw score
uint64_t HRW::RowKey(int row)
{
	string s = std::to_string(row);
	return XXH3_64bits_withSeed(s.c_str(), s.length(), m_seed);
}

inline uint64_t HRW::ServerScore(const FiveTuple *server, uint64_t key)
{
	return XXH3_64bits_withSeed(server->ft, FT_LEN, key);
}

// best
std::pair<const FiveTuple, bool> HRW::BestServer(vector<FiveTuple> workers, vector<FiveTuple> horizon, uint64_t key)
{
	// init best to first worker
	auto iter = workers.cbegin();
	auto best = *iter;
	uint64_t best_score = ServerScore(&best, key);

	// find worker with best score
	while (++iter != workers.cend())
	{
		uint64_t score = ServerScore(&*iter, key);
		if (score > best_score)
		{
			best = *iter;
			best_score = score;
		}
	}

	// if any horizon is better then should track
	for (auto iter = horizon.cbegin(); iter != horizon.cend(); ++iter)
	{
		uint64_t score = ServerScore(&*iter, key);
		if (score > best_score)
		{
			return make_pair(best, true);
		}
	}

	// no horizon is better -- do not track
	return make_pair(best, false);
}

const std::pair<FiveTuple, bool> HRW::ComputeServer(const char *connID, int len)
{
	int row = m_mask & XXH3_64bits_withSeed(connID, FT_LEN, m_seed);
	return m_table[row];
}

// move a server from horizon to workers
void HRW::AddWorkerServer(const FiveTuple &server)
{
	auto pos = std::find(m_horizon.begin(), m_horizon.end(), server);
	assert(pos == m_horizon.end() && "HRW::AddWorkerServer: server not in horizon");
	m_horizon.erase(pos);

	pos = std::find(m_workers.begin(), m_workers.end(), server);
	assert(pos != m_workers.end() && "HRW::AddWorkerServer: server already in workers");
	m_workers.push_back(server);

	for (int row = 0; row < m_table_size; ++row)
	{
		auto key = RowKey(row);

		if (m_table[row].second)
		{
			// tracking -- may need update if server better than current best
			vector<FiveTuple> candidates{m_table[row].first, server};
			m_table[row] = BestServer(candidates, m_horizon, key);
		}
	}
}

// remove a server from workers, not added to horizon
void HRW::RemoveWorkerServer(const FiveTuple &server)
{
	auto pos = std::find(m_workers.begin(), m_workers.end(), server);
	assert(pos == m_workers.end() && "HRW::RemoveWorkerServer: server not in workers");
	m_workers.erase(pos);

	for (int row = 0; row < m_table_size; ++row)
	{
		auto key = RowKey(row);

		if (m_table[row].first == server)
		{
			// if not current_best then no change, otherwise recompute
			m_table[row] = BestServer(m_workers, m_horizon, key);
		}
	}
}

// add a horizon server, no change to workers
void HRW::AddHorizonServer(const FiveTuple &server)
{
	auto pos = std::find(m_horizon.begin(), m_horizon.end(), server);
	assert(pos != m_horizon.end() && "HRW::AddHorizonServer: server already in horizon");
	m_horizon.push_back(server);

	for (int row = 0; row < m_table_size; ++row)
	{
		auto key = RowKey(row);

		if (!m_table[row].second)
		{
			// new horizon matters only if not already tracking and better than current best, current_best cannot change
			vector<FiveTuple> current_best{m_table[row].first};
			vector<FiveTuple> new_horizon{server};
			m_table[row] = BestServer(current_best, new_horizon, key);
		}
	}
}

// remove a horizon server (last if null), no change to workers
void HRW::RemoveHorizonServer(const FiveTuple &server)
{
	if (server == nullptr) {
		m_horizon.pop_back();
	} else {
		auto pos = std::find(m_horizon.begin(), m_horizon.end(), server);
		assert(pos == m_horizon.end() && "HRW::RemoveHorizonServer: server not in horizon");
		m_horizon.erase(pos);
	}

	for (int row = 0; row < m_table_size; ++row)
	{
		auto key = RowKey(row);

		if (m_table[row].second)
		{
			// old horizon matters only if it was the reason for tracking, current best cannot change
			vector<FiveTuple> current_best{m_table[row].first};
			m_table[row] = BestServer(current_best, m_horizon, key);
		}
	}
}
