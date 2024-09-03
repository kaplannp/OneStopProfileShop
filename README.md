# Overview  
This github project is designed to make profiling applications extremely easy.
It provides 3 useful features
1. It provides a simple api for inserting ROI regions into code.
2. It nicely formats outputs so that everything goes to a neat output directory
   and is preparsed (along with the raw data)
3. It provides a nice bundled calling configuration which allows you to automate
   running common analyses, and allows the user to forget about the esoteric
   syntax of each command

# Installation  
`./build.sh` will init submodules, download and build pin, and build the cpp api
`./clean.sh` removes pin and cpp api obj/lib files

# Usage  
Python scripts are used to run the actual tools, but for these tools to interact
with the application, you must include cpp macros to deliniate the roi within
your code.
## Cpp API  
In your code you may add any of the following macros around the ROI
```
BEGIN_VTUNE_ROI //tells vtune to start collecting here
BEGIN_PIN_ROI //tells pin to start collecting here
BEGIN_TIMER //starts a regular chrono timer
//a bunch of c++ code. The ROI
END_TIMER //finish timer and print time
END_PIN_ROI //stop pin collection
END_VTUNE_ROI //stop vtune collection
```

Because all three of these analysises are commonly needed together, I add a
shortcut for the above
```
BEGIN_ROI
//c++ code. ROI
END_ROI
```

An example is shown in `dummy/main.cpp`
### Makefile changes
A few things you need to add to your makefile:
+ To include the api, include `profilingUtils.h` from `Roi/CppHeaders/include`.
+ You will also need to link the static library `-lprofileUtils` in 
  `RoiCppHeaders/lib`.
+ To tell the macros to enable or disable without changing the source, you pass
  these profile flags `-DTIMER_ENABLED=1 -DVTUNE_ENABLED=1 -DPIN_ENABLED=1`
+ You will also need to include and link vtune `-littnotify -ldl`,
  `-L$(VTUNE_HOME)/lib64` `-I$(VTUNE_HOME)/include`. It is recommended you store
  `VTUNE_HOME` as an environment variable somewhere.

A full minimal exaple is shown in Dummy/makefile

## Python API
The `runBenchmark.py` script contains all the useful functions for profiling. A
user imports this script, creates a Runner object by passing the output
directory location, and the runs analyses. Currently supported are:
```
runVtuneUarch(app)
runVanillaApp(app)
runPinInstrCount(app)
runVtuneCache(app)
```
Each function takes as input the application to run, and will automatically
store everything in a nice ouput directory

An example is shown in `main.py`. Note you'll need to build dummy seperately
