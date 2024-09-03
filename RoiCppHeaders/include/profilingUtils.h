/*
 * This file combines macros for PIN, for vtune, and for regular timers
 */

#ifndef PROFILING_UTILS_H
#define PROFILING_UTILS_H

#include "pinRoi.h"
#include "vtuneConfigs.h"
//Note this must never be called for more than one roi in a kernel
#if (TIMER_ENABLED==1)
  #include <chrono>
  #define BEGIN_TIMER auto kernel_begin_zkn = std::chrono::system_clock::now();
  #define END_TIMER auto kernel_end_zkn = std::chrono::system_clock::now(); \
                    auto kernel_time_us_zkn = \
                        std::chrono::duration_cast<std::chrono::microseconds>( \
                        kernel_end_zkn-kernel_begin_zkn).count(); \
                    std::cout << "zkn kernel time: " << kernel_time_us_zkn << \
                    "us" << std::endl;
#else
  #define BEGIN_TIMER
  #define END_TIMER
#endif

#define BEGIN_ROI BEGIN_VTUNE_ROI BEGIN_PIN_ROI BEGIN_TIMER
#define END_ROI END_TIMER END_PIN_ROI END_VTUNE_ROI 

#endif  // PROFILING_UTILS_H
