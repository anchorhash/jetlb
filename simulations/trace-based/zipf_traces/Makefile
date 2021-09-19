objects = genzipf.o 

genzipf : $(objects) 
	g++ -o genzipf $(objects) -std=c++11
	
genzipf.o : ../../../cpp-jetlb/gen_zipf/genzipf.cpp ../../../cpp-jetlb/gen_zipf/genzipf.h 
	g++ -Wall -c ../../../cpp-jetlb/gen_zipf/genzipf.cpp -std=c++11
					
# Cleaning old files before new make
clean : 
	rm genzipf $(objects)

