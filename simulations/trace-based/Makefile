objects = main.o AnchorHash.o hrw.o xxhash.o Jet_anchor.o Jet_hrw.o

main : $(objects) 
	g++ -O2 -o main $(objects) -std=c++11
	
main.o : ../../cpp-jetlb/main.cpp ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/main.cpp -std=c++11
	
AnchorHash.o : ../../cpp-jetlb/anchorhash/* ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/anchorhash/AnchorHash.cpp -std=c++11

Jet_anchor.o : ../../cpp-jetlb/jet_anchor/* ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/jet_anchor/Jet_anchor.cpp -std=c++11
	
hrw.o : ../../cpp-jetlb/hrw/* ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/hrw/hrw.cpp -std=c++11

Jet_hrw.o : ../../cpp-jetlb/jet_hrw/* ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/jet_hrw/Jet_hrw.cpp -std=c++11
	
xxhash.o : ../../cpp-jetlb/xxhash/* ../../cpp-jetlb/defs.h 
	g++ -Wall -O2 -c ../../cpp-jetlb/xxhash/xxhash.c -std=c++11
					
# Cleaning old files before new make
clean : 
	rm main $(objects)
