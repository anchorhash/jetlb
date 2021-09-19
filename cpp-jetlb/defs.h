#ifndef DEFS
#define DEFS

#include <iostream>
#include <ctime>
#include <unordered_map>
#include <map>
#include <chrono>
#include <string>
#include <fstream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <cassert>

#include "./anchorhash/AnchorHash.h"
#include "./robinhoodmap/robin_hood.h"
#include "./xxhash/xxhash.h"

using namespace std;

void inline pause()
{
      cout << '\n' << "Press the Enter key to continue.";
      cin.ignore( ( numeric_limits< streamsize >::max )( ), '\n' );
}

#define FT_LEN 13

struct FiveTuple
{
	char ft[14];

	bool operator==(const FiveTuple& connID) const
	{
		return memcmp(ft, connID.ft, FT_LEN) == 0;
	}

	FiveTuple(const FiveTuple& connID)
	{
		memcpy(ft, connID.ft, FT_LEN);
		ft[FT_LEN] = 0;
	}

	FiveTuple(const string str)
	{
		memcpy(ft, str.c_str(), FT_LEN);
		ft[FT_LEN] = 0;
	}

	FiveTuple(const char* chr)
	{
		memcpy(ft, chr, FT_LEN);
		ft[FT_LEN] = 0;
	}

	FiveTuple()
	{
		ft[FT_LEN] = 0;
	}
};

struct FiveTupleHasher
{
	std::hash<string> string_hash;
	size_t operator()(const FiveTuple& x) const
	{
		return XXH64(x.ft, FT_LEN, 42);
	}
};

typedef std::pair<FiveTuple, int> hist_pair;

#endif
