#include <iostream>
#include <stdlib.h>
#include <cstring>
#include <cmath>

#include "profilingUtils.h"

using namespace std; 

int runKernel(int size){
  std::srand(size);
  int x=0;
  int y = 3;
  for (int i=0; i < size; i++){
    int y = std::rand();
    if (y%5 == 0){
      x += std::rand();
    }
  }
  return x;
}

float doSomeFPArithmetic(int size){
  std::srand(size);
  float total = 0.0;
  float context = 0.0;
  total = std::rand() + 3.14;
  total = std::rand() + 3.14;
#pragma loop(no_vector)
  for (int i = 0; i < size; i++){
    total = std::sin(total + std::sin(i + std::rand()));
  }
  return total;
}


int main(){
  int x =0;
  int* size = new int;
  *size = 10000;
  runKernel(*size);

  BEGIN_ROI
  Barrier<int*>(size);
  int kernelOut =  runKernel(*size);
  float fpOut = doSomeFPArithmetic(*size);
  Barrier<int*>(size);
  END_ROI
  std::cout << "outs "<< kernelOut << ", " << fpOut << std::endl;
}

