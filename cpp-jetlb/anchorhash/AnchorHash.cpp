#include "AnchorHash.h"

/** Constructor */
AnchorHash::AnchorHash(uint32_t a, uint32_t w, uint32_t seed, uint32_t horizon) {

	assert(w + horizon <= a && "AnchorHash::AnchorHash: w + horizon > a");

	// Horizon size
	Horizon = horizon;

	// Random seed
	Seed = seed;

	// Allocate the anchor array	
	A = new uint32_t[a]();

	// Allocate the working array
	W = new uint32_t[a]();

	// Allocate the last apperance array
	L = new uint32_t[a]();

	// Allocate the "map diagonal"	
	K = new uint32_t[a]();

	// Initialize "swap" arrays 
	for (uint32_t i = 0; i < a; ++i) {
		L[i] = i;
		W[i] = i;
		K[i] = i;
	}

	// We treat initial removals as ordered removals
	for (uint32_t i = a - 1; i >= w; --i) {
		A[i] = i;
		r.push(i);
	}

	// Set initial set sizes
	M = a;
	N = w;

}

/** Destructor */
AnchorHash::~AnchorHash() {

	delete[] A;
	delete[] W;
	delete[] L;
	delete[] K;

}

uint32_t AnchorHash::ComputeTranslation(uint32_t i, uint32_t j) {

	if (i == j) return K[i];

	uint32_t b = j;

	while (A[i] <= A[b]) {
		b = K[b];
	}

	return b;

}

pair<uint32_t, bool> AnchorHash::ComputeBucket(const char* connID, int len) {

	// First hash is uniform on the anchor set
	XXH64_hash_t bs = XXH64(connID, len, Seed);
	uint32_t b = bs % M;

	uint32_t last_hit = M + 1;

	// Loop until hitting a working bucket
	while (A[b] != 0) {

		// did we hit a horizon bucket?
		last_hit = A[b];

		// rehash		
		bs = XXH64(&bs, 8, b);

		uint32_t h = bs % A[b];

		//  h is working or observed by bucket
		if ((A[h] == 0) || (A[h] < A[b])) {
			b = h;
		}

		// need translation for (bucket, h)
		else {
			b = ComputeTranslation(b, h);
		}

	}

	return make_pair(b, last_hit < N + Horizon);

}

uint32_t AnchorHash::UpdateRemoval(uint32_t b) {

	// update reserved stack
	r.push(b);

	// update live set size
	N--;

	// who is the replacement
	W[L[b]] = W[N];
	L[W[N]] = L[b];

	// Update map diagonal
	K[b] = W[N];

	// Update removal
	A[b] = N;

	return 0;

}

uint32_t AnchorHash::UpdateNewBucket() {

	assert(N + Horizon < M && "AnchorHash::AnchorHash: (N + 1) + horizon > M");

	// Who was removed last?	
	uint32_t b = r.top();
	r.pop();

	// Restore in observed_set
	L[W[N]] = N;
	W[L[b]] = b;

	// update live set size
	N++;

	// Ressurect
	A[b] = 0;

	// Restore in diagonal
	K[b] = b;

	return b;

}