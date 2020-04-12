#Set this to -fopenmp to enable compiling with openmp
parallel = -fopenmp

#Set this to -DTIMING to enable timing output
timing = -DTIMING

#Set this to -DDEBUG to enable debugging output
debug = 

#Set this to -DMERSENNE_TWISTER to use the Mersenne twister 19937 Random number generator
random = -DMERSENNE_TWISTER

include_paths = -Ilibs/ -Ilibs/cxxopts-2.2.0/include/
headers = models.h initializers.h interventions.h updates.h simulator.h outputs.h defaults.h
obj = initializers.o models.o interventions.o updates.o simulator.o outputs.o
opts = --std=c++14 -O3 $(parallel) $(timing) $(debug) $(random)
CC = g++ $(opts) $(include_paths)

outputs.o: outputs.cc $(headers)
	$(CC) -c outputs.cc -o outputs.o

simulator.o: simulator.cc $(headers)
	$(CC) -c simulator.cc -o simulator.o

updates.o: updates.cc $(headers)
	$(CC) -c updates.cc -o updates.o

interventions.o: interventions.cc $(headers)
	$(CC) -c interventions.cc -o interventions.o

models.o: models.cc $(headers)
	$(CC) -c models.cc -o models.o

initializers.o: initializers.cc $(headers)
	$(CC) -c initializers.cc -o initializers.o

drive_simulator: drive_simulator.cc $(obj) $(headers)
	$(CC) -o drive_simulator drive_simulator.cc $(obj)

all: drive_simulator

clean:
	rm drive_simulator $(obj)

