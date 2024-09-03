CXX:=g++

LIB_DIR=lib
SRC_DIR=src
OBJ_DIR=obj
LIB_TARGET=profileUtils.a

INCLUDE_FLAGS=-Iinclude


all: $(LIB_DIR)/lib$(LIB_TARGET)

$(LIB_DIR)/lib%.a: $(OBJ_DIR)/%.o
	ar rvs $@ $<

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDE_FLAGS) -c -o $@ $<

clean:
	rm -r $(LIB_DIR)/*
