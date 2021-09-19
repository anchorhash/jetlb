#ifndef ANCHOR
#define ANCHOR

#include <iostream>
#include <stack>
#include <stdint.h>

#include "../defs.h"

/** Class declaration */
class AnchorHash {

private:

	// Horozon size
	uint32_t Horizon;

	// Random seed
	uint32_t Seed;

	// Anchor		
	uint32_t* A;

	// Working
	uint32_t* W;

	// Last appearance 
	uint32_t* L;

	// "Map diagonal"	
	uint32_t* K;

	// Size of the anchor
	uint32_t M;

	// Size of the working
	uint32_t N;

	// Removed buckets
	std::stack<uint32_t> r;

	// Translation oracle
	uint32_t ComputeTranslation(uint32_t i, uint32_t j);

public:

	AnchorHash(uint32_t a, uint32_t w, uint32_t seed, uint32_t horizon);

	~AnchorHash();

	std::pair<uint32_t, bool> ComputeBucket(const char* connID, int len);

	uint32_t UpdateRemoval(uint32_t b);

	uint32_t UpdateNewBucket();

};

#endif