CXX = g++
CFLAGS = -g
LIBS = -levent
.SUFFIXES: .cxx .o
.cxx.o:
	$(CXX) $(CFLAGS) -c $^ -o $@

all: test

opfsd: opfsd.o util.o opfs_entries.o net.o
	$(CXX) $(CFLAGS) $^ -o $@ $(LIBS)

opfsc: opfsc.o
	$(CXX) $(CFLAGS) $^ -o $@ $(LIBS)

test: opfsd
	./$< ./testdir

memtest: opfsd
	valgrind --suppressions=./valgrind_suppress --leak-check=full --show-reachable=yes ./$< ./testdir
#	valgrind --gen-suppressions=yes --suppressions=./valgrind_suppress  --leak-check=full --show-reachable=yes ./$< ./testdir


clean:
	rm -rf opfsd.o util.o opfs_entries.o net.o opfsd
