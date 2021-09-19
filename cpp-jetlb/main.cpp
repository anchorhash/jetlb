#include "defs.h"

#include "./jet_anchor/Jet_anchor.h"
#include "./jet_hrw/Jet_hrw.h"

using namespace std;

string gen_random(const int len) {

	string tmp_s;
	static const char alphanum[] =
		"0123456789"
		"ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		"abcdefghijklmnopqrstuvwxyz";

	tmp_s.reserve(len);

	for (int i = 0; i < len; ++i)
		tmp_s += alphanum[rand() % (sizeof(alphanum) - 1)];


	return tmp_s;

}

int main(int argc, char* argv[]) {


	cout << "Cargumets:";
	for (int i = 1; i < argc; i++)
	{
		cout << "\t" << argv[i];
	}
	cout << endl;

	int seed = atoi(argv[7]);

	srand(seed);

	/*
	
	1. trace: path to binary of 5-tuples (e.g., "G:/traces/my_trace")
	2. trace length: number of 5-tuples (13 bytes) to read from binary
	3. number of servers (e.g., 100)
	4. horizon size (0 means zero -> for full CT)
	5. hash type: "anchor" or "hrw"
	6. print trace historgram and exit: 0 (false) or 1 (true)
	7. random seed
	
	*/

	string path = argv[1];

	int n = atoi(argv[2]);
	int m = atoi(argv[3]);
	int h = atoi(argv[4]);

	// capacity
	int w = 1.2 * m;

	// baseline or jet?
	bool is_baseline = h == 0;

	// read trace from file?
	FiveTuple* fts = new FiveTuple[n];

	ifstream f(path, ios::binary);

	char buffer[13];
	int i = 0;
	while (f.peek() != EOF && i < n)
	{
		f.read(buffer, FT_LEN);
		fts[i] = FiveTuple(buffer);
		i++;
	}
	n = i;
	f.close();

	// print trace histogram
	bool trace_histogram = atoi(argv[6]) == 1;

	if (trace_histogram) {

		unordered_map<FiveTuple, int, FiveTupleHasher> th;

		// populate the map
		for (int i = 0; i < n; i++)
		{
			th[fts[i]] += 1;
		}

		// create an empty vector of pairs
		std::vector<hist_pair> vec;

		// copy key-value pairs from the map to the vector
		std::copy(th.begin(), th.end(), std::back_inserter<std::vector<hist_pair>>(vec));

		// sort the vector by increasing the order of its pair's second value
		// if the second value is equal, order by the pair's first value
		std::sort(vec.begin(), vec.end(),
			[](const hist_pair& l, const hist_pair& r)
			{
					return l.second < r.second;
			});

		// print the vector
		for (auto const& pair : vec) {
			std::cout << pair.second << std::endl;
		}

		return 0;

	}

	vector<FiveTuple> servers;

	for (int i = 0; i < m; i++)
	{
		servers.push_back(FiveTuple(gen_random(13)));
	}

	vector<FiveTuple> horizon;
	for (int i = 0; i < h; i++)
	{
		horizon.push_back(FiveTuple(gen_random(13)));
	}

	if (is_baseline)
	{
		h = 0;
	}

	if (strcmp(argv[5], "anchor") == 0)
	{
		Jet j(servers, w, h, seed, is_baseline);

		//for (int i = 0; i < n; i++)
		//{
		//	j.GetServer(fts[i]);
		//}

		auto t1 = std::chrono::high_resolution_clock::now();
		for (int i = 0; i < n; i++)
		{
			j.GetServer(fts[i]);
		}
		auto t2 = std::chrono::high_resolution_clock::now();
		auto getDestinations_microsec_exectime = std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count();

		cout << "Execution time in milliseconds: " << getDestinations_microsec_exectime / 1000 << endl;
		cout << "MKPS: " << (double)n / getDestinations_microsec_exectime << endl;

		robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> balance;
		robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> flows;

		for (auto pserver = std::begin(servers); pserver != std::end(servers); ++pserver)
		{
			balance[*pserver] = 0;
		}
		for (int i = 0; i < n; i++)
		{
			flows[fts[i]] = 0;
		}

		for (int i = 0; i < n; i++)
		{
			if (flows[fts[i]] == 0)
			{
				flows[fts[i]] = 1;
				balance[j.GetServer(fts[i])] += 1;
			}
		}

		auto mins = balance.begin();
		auto maxs = balance.begin();

		//cout << "\nBalance:\n";
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
		//cout << "max:\t" << (maxs->first).ft << ":\t" << maxs->second << endl;
		//cout << "min:\t" << (mins->first).ft << ":\t" << mins->second << endl;
		cout << "load factor:\t" << 1.0 * maxs->second * m / flows.size() << endl;

		cout << "CT table size: " << j.get_ct_table_size() << endl;
		cout << "Number of disctinct flows: " << flows.size() << endl;
	}

	else if (strcmp(argv[5], "hrw") == 0)
	{
		JetHRW j(servers, horizon, w, seed, is_baseline);

		//for (int i = 0; i < n; i++)
		//{
		//	j.GetServer(fts[i]);
		//}

		auto t1 = std::chrono::high_resolution_clock::now();
		for (int i = 0; i < n; i++)
		{
			j.GetServer(fts[i]);
		}
		auto t2 = std::chrono::high_resolution_clock::now();
		auto getDestinations_microsec_exectime = std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count();

		cout << "Execution time in milliseconds: " << getDestinations_microsec_exectime / 1000 << endl;
		cout << "MKPS: " << (double)n / getDestinations_microsec_exectime << endl;

		robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> balance;
		robin_hood::unordered_map<FiveTuple, int, FiveTupleHasher> flows;

		for (auto pserver = std::begin(servers); pserver != std::end(servers); ++pserver)
		{
			balance[*pserver] = 0;
		}
		for (int i = 0; i < n; i++)
		{
			flows[fts[i]] = 0;
		}

		for (int i = 0; i < n; i++)
		{
			if (flows[fts[i]] == 0)
			{
				flows[fts[i]] = 1;
				balance[j.GetServer(fts[i])] += 1;
			}
		}

		auto mins = balance.begin();
		auto maxs = balance.begin();

		//cout << "\nBalance:\n";
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
		//cout << "max:\t" << (maxs->first).ft << ":\t" << maxs->second << endl;
		//cout << "min:\t" << (mins->first).ft << ":\t" << mins->second << endl;
		cout << "load factor:\t" << 1.0 * maxs->second * m / flows.size() << endl;

		cout << "CT table size: " << j.get_ct_table_size() << endl;
		cout << "Number of disctinct flows: " << flows.size() << endl;
	}

	else
	{
		cout << "unknown hash type";
		exit(-1);
	}

	cout << "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%" << endl;

	delete[] fts;

	return 0;

}
