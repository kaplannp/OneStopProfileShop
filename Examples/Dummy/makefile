CXX=g++ -O3

INCLUDES=-I../../RoiCppHeaders/include -I$(VTUNE_HOME)/include
LIB_DIRS=-L../../RoiCppHeaders/lib -L$(VTUNE_HOME)/lib64
LIBS=-lprofileUtils -littnotify -ldl
PROFILE_FLAGS=-DTIMER_ENABLED=1 -DVTUNE_ENABLED=1 -DPIN_ENABLED=1
#now for the other version
main: main.cpp
	$(CXX) $(INCLUDES) $(LIB_DIRS) main.cpp -o main $(LIBS) $(PROFILE_FLAGS)

clean:
	rm -f main
