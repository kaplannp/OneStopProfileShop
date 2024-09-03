#ifndef PIN_ROI_H
#define PIN_ROI_H

/*
 * These functions are used to invoke the PIN tool ROI. The name is the only
 * important thing. The implementation of the function
 * is designed such that it will not take a lot of time, but that it is
 * difficult for the compiler to inline. It is not recommended you change the
 * implementation. While it is possible to make it more efficient, the chosen
 * functions have been empirically verified by generations of graduate student
 * labour
 */
const char* __attribute__((noinline)) __begin_pin_roi(const char *s, int *beg, int *end);
const char* __attribute__((noinline)) __end_pin_roi(const char *s, int *beg, int *end);

/*
 * This is pulled directly off a stack overflow, which in turn copies a chunk of
 * the google testbench suite. The idea is to use it on the inputs/outputs of a
 * function to ensure they aren't moved outside the timers
 */
template <class T>
__attribute__((always_inline)) inline void Barrier(const T &value) {
    asm volatile("" : "+m"(const_cast<T &>(value)));
}


#if (PIN_ENABLED==1)
  #define BEGIN_PIN_ROI __begin_pin_roi(new char[5], new int, new int);
  #define END_PIN_ROI __end_pin_roi(new char[5], new int, new int);
#else
  #define BEGIN_PIN_ROI
  #define END_PIN_ROI
#endif


#endif //PIN_ROI_H
