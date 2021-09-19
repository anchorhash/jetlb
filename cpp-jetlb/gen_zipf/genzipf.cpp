#include <iostream>
#include <string>

#include "./genzipf.h"

using namespace std;

int main(int argc, char* argv[]) {

	int trace_length = atoi(argv[1]);
	string trace_name = argv[2];
	double trace_skew = atof(argv[3]);
	
	cout << "generating zipf trace named " << trace_name << " of length " << trace_length << " and skew " << trace_skew << endl;
	
	genzipf(trace_name.c_str(), 42, trace_skew, 1 << 24, trace_length);
	
	return 0;
}



