import os
import shutil
import re
import pandas as pd
import tempfile

#root directory. Used so we have paths to other things in this github
HOME=os.path.dirname(os.path.abspath(__file__))


class UarchReportParser:
    """
    Class for parsing a uarch report. It extracts cpi, retiring, frontent bound
    core bound, bad spec, and mem bound.
    It's essentially a bunch of grep functions and one function for getting
    everything and pretty formating
    """

    def getCpi(self, s):
        return float(re.search(r"CPI Rate: (\d+\.\d+)", s).groups()[0])

    def getRetiring(self, s):
        return float(re.search(r"Retiring: (\d+\.\d+)%", s).groups()[0])

    def getFrontEndBound(self, s):
        return float(re.search(r"Front-End Bound: (\d+\.\d+)%", s).groups()[0])

    def getCoreBound(self, s):
        return float(re.search(r"Core Bound: (\d+\.\d+)%", s).groups()[0])

    def getBadSpeculationBound(self, s):
        return float(re.search(r"Bad Speculation: (\d+\.\d+)%", s).groups()[0])

    def getMemBound(self, s):
        return float(re.search(r"Memory Bound: (\d+\.\d+)%", s).groups()[0])

    def parseUarchReport(self, filename):
        s = self.loadFile(filename)
        stats = "" 
        stats += "Cpi " + str(self.getCpi(s)) + "\n"
        stats += "Retiring " + str(self.getRetiring(s)) + "\n"
        stats += "FrontEndBound " + str(self.getFrontEndBound(s)) + "\n"
        stats += "CoreBound " + str(self.getCoreBound(s)) + "\n"
        stats += "BadSpeculationBound " + str(self.getBadSpeculationBound(s)) + "\n"
        stats += "MemBound " + str(self.getMemBound(s)) + "\n"
        return stats

    def loadFile(self, filename):
        '''
        read file to string. Saves typing
        '''
        data = ""
        with open(filename, "r") as iFile:
            data = iFile.read();
        return data

'''
This is quite brittle. If you're reading this, you should probably just start
from scratch.
It produces a list of tuples with name and the value of that hw counter
'''

class CacheReportParser:
    '''
    This one is spaghetti code, sorry. It should work though. 
    '''
    def generateTupleList(self, dataFile):
        data = ""

        with open(dataFile, 'r') as rFile:
            data = rFile.read()

        PREFIX = r"MEM_LOAD_RETIRED\."
        METRICS = ["L1_MISS","L2_MISS","L3_MISS"]

        results = []
        for reQuery in [r"{}({}) *(\d*)".format(PREFIX, metric) for metric in METRICS]:
            results.append(re.search(reQuery, data).groups())
        results.append(("ALL_LOADS", re.search(
            r'MEM_INST_RETIRED\.ALL_LOADS *(\d*)', data).groups()[0]))
        results.append(("DYN_INST_CNT", re.search(
            r'\nINST_RETIRED\.ANY *(\d*)', data).groups()[0]))
        return pd.Series({key:val for key, val in results}, dtype=int)

    def formatSeriesOut(self, data):
        '''
        formats the tuple list output of generateTupleList. Might be destructive
        of the series
        '''
        data["L1_MISS_EXL"] =(data["L1_MISS"]-data["L2_MISS"])
        data["L2_MISS_EXL"] =(data["L2_MISS"]-data["L3_MISS"])
        data["L3_MISS_EXL"] =data["L3_MISS"]
        outStr = ""
        outStr += "DYN_INST_CNT {}\n".format(data["DYN_INST_CNT"])
        outStr += "L1_MISS {}\n".format(data["L1_MISS_EXL"])
        outStr += "L2_MISS {}\n".format(data["L2_MISS_EXL"])
        outStr += "L3_MISS {}\n".format(data["L3_MISS_EXL"])
        return outStr
    
    def parseCacheReport(self, dataFile):
        '''
        Parses the cache data and returns a string nicely formated of useful
        information
        '''
        print(self.generateTupleList(dataFile))
        return self.formatSeriesOut(self.generateTupleList(dataFile))


class CacheStallReportParser:
    '''
    This one is spaghetti code, sorry. It should work though. 
    '''
    def generateTupleList(self, dataFile):
        data = ""

        with open(dataFile, 'r') as rFile:
            data = rFile.read()

        PREFIX = r"CYCLE_ACTIVITY\.STALLS_"
        METRICS = ["L1D_MISS", "L2_MISS", "L3_MISS", "TOTAL"]

        results = []
        for reQuery in [r"{}({}) *(\d*)".format(PREFIX, metric) for metric in METRICS]:
            results.append(re.search(reQuery, data).groups())
        return pd.Series({key:val for key, val in results}, dtype=int)

    def formatSeriesOut(self, data):
        '''
        formats the tuple list output of generateTupleList. Might be destructive
        of the series
        '''
        outStr = ""
        data["L1D_MISS_EXL"] =(data["L1D_MISS"]-data["L2_MISS"]) / data["TOTAL"]
        data["L2_MISS_EXL"] =(data["L2_MISS"]-data["L3_MISS"]) / data["TOTAL"]
        data["L3_MISS_EXL"] =data["L3_MISS"] / data["TOTAL"]
        outStr += "TOTAL_STALLS {}\n".format(data["TOTAL"])
        outStr += "L1_MISS {}\n".format(data["L1D_MISS_EXL"])
        outStr += "L2_MISS {}\n".format(data["L2_MISS_EXL"])
        outStr += "L3_MISS {}\n".format(data["L3_MISS_EXL"])
        return outStr
    
    def parseCacheReport(self, dataFile):
        '''
        Parses the cache data and returns a string nicely formated of useful
        information
        '''
        return self.formatSeriesOut(self.generateTupleList(dataFile))

class Runner:

    def __init__(
        self, 
        outDir,
        vtune=None,
        pinLocalPath=None
    ):
        """
        @params string: outDir the ouput directory to store all the files
        @params string: app the application to run with all args
        @params string: vtune the path of the vtune application to be used
        @params string: pinLocalPath local path from the home directory to the
                        pin directory
        """
        #initialize default args if not passed
        if not vtune:
            vtune=os.path.join(os.environ["VTUNE_HOME"], "bin64", "vtune")
        if not pinLocalPath:
            pinLocalPath=os.path.join(HOME,"deps/IntelPin")

        self.setupOutputDir(outDir)
        self.vtune = vtune
        self.pin = os.path.join(HOME, pinLocalPath, "pin")
        self.micaLib = os.path.join(HOME, pinLocalPath,
                "source/tools/MICA-Pausable/obj-intel64/mica.so")
        self.uarchReportParser = UarchReportParser()
        self.cacheReportParser = CacheReportParser()
        self.cacheStallReportParser = CacheStallReportParser()


    def setupOutputDir(self, outDir):
        """
        @param the ouput directory
        This initializes the member varables of the class refering to output
        dirs
        postcondition: then creates the ouput dir and a standardized subdirectory 
                       structure in the output dir Strucutred as follows:
        # ROOT_OUT_DIR
        # - KernelOuts/ //outputs of kernel for true comparisons
        #   - Out/ //The outputs of the kernel for comparison to true
        # - Logs/ //the log of the command including the runtime
        #   - uarch.log
        # - Profiles/ //the raw vtune profile
        #   - Uarch
        # - Reports/ //reports generated from vtune
        """
        assert not os.path.exists(outDir), "Directory {} already exists! Please remove it before running this script".format(outDir)
        self.outDir = outDir
        self.profileDir = os.path.join(outDir, "Profiles")
        self.kernelOutputDir = os.path.join(outDir, "KernelOuts")
        self.logDir = os.path.join(outDir, "Logs")
        self.reportDir = os.path.join(outDir, "Reports")
        self.resultsDir = os.path.join(outDir, "Results")
        os.makedirs(self.outDir);
        os.mkdir(self.profileDir);
        os.mkdir(self.kernelOutputDir);
        os.mkdir(self.logDir);
        os.mkdir(self.reportDir);
        os.mkdir(self.resultsDir);

    def runVtuneUarch(self, app):
        '''
        initializes the uarch profile in profileDir/Uarch
        and a log in logDir/uarch.log
        and report in reportDir/uarchSum.txt
        final stats in resultsDir/uarchStats.txt
        '''
        execAndLog("{} -collect uarch-exploration -knob sampling-interval=.1 -start-paused -data-limit=15000 -result-dir {}/Uarch {} 2>&1 | tee {}/uarch.log".format(self.vtune, self.profileDir, app, self.logDir))
        execAndLog("{} -report summary -inline-mode on -r {}/Uarch -report-output {}/uarchSum.txt".format(self.vtune, self.profileDir, self.reportDir))
        #extract important stats from vtune report and write to the result dir
        stats = self.uarchReportParser.parseUarchReport(
                  os.path.join(self.reportDir,"uarchSum.txt"))
        with open(os.path.join(self.resultsDir, "uarchStats.txt"),'w') as oFile:
            oFile.write(stats);

    def getCacheCollectionMetrics(self):
        """
        This is a constant, it's just more readable here. These are the PMU
        events we need to pass to intel. (google intel PMU)
        """
        METRICS="MEM_INST_RETIRED.ALL_LOADS,"
        METRICS+="MEM_LOAD_RETIRED.L1_MISS,"
        METRICS+="MEM_LOAD_RETIRED.L2_MISS,"
        METRICS+="MEM_LOAD_RETIRED.L3_MISS,"
        #METRICS+="MEM_LOAD_L3_MISS_RETIRED.LOCAL_DRAM,"
        METRICS+="INST_RETIRED.ANY"
        return METRICS

    def getCacheCollectionFlags(self):
        """
        This is a constant, it's just more readable here. These are flags for a
        cache analysis
        """
        METRICS=self.getCacheCollectionMetrics()
        FLAGS="-collect-with runsa \
               -start-paused \
               -knob event-config={} \
               -knob process-kernel-binaries=true \
               -knob stack-size=16384 \
               -knob enable-user-tasks=true \
               -finalization-mode=full \
               -knob sampling-interval=.1 \
               -data-limit=15000 \
               -inline-mode=on".format(METRICS)
        return FLAGS

    def runVtuneCache(self, app):
        """
        runs vtune profiling to collect cache statistics in profileDir/Cache
        log in logDir/cache.log
        There is another type of analysis which gets stalls, but this one gets
        the counts of cache misses/hits per instruction
        report in reportDir/cachSum.txt
        final stats in resultsDir/cacheStats.txt
        """
        FLAGS=self.getCacheCollectionFlags()
        #run the profiling
        execAndLog("{} {} -result-dir {} {} 2>&1 | tee {}".format(
                        self.vtune,
                        FLAGS,
                        os.path.join(self.profileDir, "Cache"),
                        app,
                        os.path.join(self.logDir, "cache.log")))
        #generate a report summary. Note, I've tried -report output, for some
        #reason only > works
        execAndLog("{} -report summary -r {} > {}".format(
                self.vtune, 
                os.path.join(self.profileDir, "Cache"),
                os.path.join(self.reportDir, "cacheSum.txt")))
        stats = self.cacheReportParser.parseCacheReport(
                os.path.join(self.reportDir,"cacheSum.txt"))
        with open(os.path.join(self.resultsDir, "cacheStats.txt"),'w') as oFile:
            oFile.write(stats);

    def getCacheStallFlags(self):
        """
        This is a constant, it's just more readable here. These are flags for a
        cache analysis
        """
        METRICS="CYCLE_ACTIVITY.STALLS_TOTAL,"
        METRICS+="CYCLE_ACTIVITY.STALLS_L1D_MISS,"
        METRICS+="CYCLE_ACTIVITY.STALLS_L2_MISS,"
        METRICS+="CYCLE_ACTIVITY.STALLS_L3_MISS,"
        #METRICS+="CYCLE_ACTIVITY.STALLS_MEM_ANY," #this is DRAM. cache exclusive
        FLAGS="-collect-with runsa \
               -start-paused \
               -knob event-config={} \
               -knob process-kernel-binaries=true \
               -knob stack-size=16384 \
               -knob max-region-duration=1000 \
               -knob enable-user-tasks=true \
               -finalization-mode=full \
               -knob sampling-interval=.1 \
               -inline-mode=on".format(METRICS)
        return FLAGS

    def runVtuneCacheStall(self, app):
        """
        runs vtune profiling to collect cache statistics in
        profileDir/CacheStalls
        log in logDir/cacheStall.log. The difference between this and the other 
        cache collection is that this one collects cycles when there was a stall
        and a cache miss at the same time.
        report in reportDir/cacheStallSum.txt
        final stats in resultsDir/cacheStallStats.txt
        """
        FLAGS=self.getCacheStallFlags()
        #run the profiling
        execAndLog("{} {} -result-dir {} {} 2>&1 | tee {}".format(
                        self.vtune,
                        FLAGS,
                        os.path.join(self.profileDir, "CacheStall"),
                        app,
                        os.path.join(self.logDir, "cacheStall.log")))
        #generate a report summary. Note, I've tried -report output, for some
        #reason only > works
        execAndLog("{} -report summary -r {} > {}".format(
                self.vtune, 
                os.path.join(self.profileDir, "CacheStall"),
                os.path.join(self.reportDir, "cacheStallSum.txt")))
        stats = self.cacheStallReportParser.parseCacheReport(
                os.path.join(self.reportDir,"cacheStallSum.txt"))
        with open(os.path.join(self.resultsDir, "cacheStallStats.txt"),
                  'w') as oFile:
            oFile.write(stats);

    
    def formatMicaOutput(self):
        '''
        Assuming MICA files in cwd, this generates instrCounts.txt from
        ityped_full_int_pin.out. instrCounts is labeled, and reports in terms of
        percentages instead of counts
        '''
        with open("itypes_full_int_pin.out", 'r') as iFile:
            data = iFile.read().split(" ")
            with open("instrCounts.txt", 'w') as oFile:
                countNames = ["Count", "Nop", "VecMemory", "Memory", "FpScalar", 
                       "Vector", "Ctrl", "Register", "Scalar", "Other"]
                total = 0;
                for name, val in zip(countNames, data[:len(countNames)]):
                    if (name == "Count"):
                        total = int(val)
                    else:
                        val = int(val) / total #used to get a percentage
                    oFile.write("{} {}\n".format(name, val))

    def runVanillaApp(self, app, outputs=[]):
        '''
        runs vanilla application to collect outputs in KernelOuts
        log in logDir/vanillaApp.log
        final stats in resultsDir/vanillaRunTimes.txt
        @param list<str> outputs: this is a list of outputs of the application,
                                  e.g. it produces a fasta file or something. It
                                  can also be a directory. If you specify it,
                                  any files specified will be moved into the
                                  kernel Output Directory
        '''
        execAndLog("{} 2>&1 | tee {}".format(
            app, 
            os.path.join(self.logDir, "vanillaApp.log")))
        for filename in outputs:
            #move the ouput, kernels always generate Out/ in cwd
            os.rename(filename, os.path.join(self.kernelOutputDir, filename))

        #run regex to get the timing from the output
        with open(os.path.join(self.logDir,"vanillaApp.log"), 'r') as iFile:
            strLog = iFile.read()
            matches = re.findall(r"(load|kernel|write) time: (\d*us)", strLog)
        #write the output to file
        with open(os.path.join(self.resultsDir,"vanillaRunTimes.txt"),'w') as wFile:
            for match in matches:
                wFile.write("{} {}\n".format(match[0], match[1]))

    def runThreadScaling(self, app, nThreads=[1]):
        '''
        Runs the app a bunch of times with different number of threads. The app
        must be instrumented with timers so we can parse the kernel runtime. The
        list of runtimes will be written to the file
        resultsDir/threadScaling.txt
        @param str app: the application to run WITH one {}. This is used directly 
                        to insert the thread count with a format string. I hope
                        your application doesn't use {} anywhere else
        @param list<int> nThreads: the different thread numbers you want to run
                                   this analysis on
        '''
        outputString = ""
        for threadCnt in nThreads:
            logFileName = os.path.join(self.logDir,
                    "threadScaling{}.log".format(threadCnt))
            #basically executing the app here with some decoration
            execAndLog("{} 2>&1 | tee {}".format( 
                app.format(threadCnt),
                logFileName))
            with open(logFileName, "r") as iFile:
                strLog = iFile.read()
                matches = re.findall(r"zkn kernel time: (\d*us)", strLog)
                outputString += "{} {}\n".format(threadCnt, matches[0])

        outputFileName = os.path.join(self.resultsDir, "threadScaling.txt")
        with open(outputFileName, 'w') as oFile:
            oFile.write(outputString)





    def runPinInstrCount(self, app):
        """
        Runs MICA PINtool to count the instructions. It then outputs the 
        instructions.
        Note, an issue with MICA pin is that it only produces files in the cwd.
        so we create a tmp directory and move the files to the output directory.
        *THIS REQUIRES THAT APP PATH IS ABSOLUTE*
        """
        #init final ouput directories
        micaOut=os.path.join(self.profileDir, "Mica")
        os.mkdir(micaOut)
        useExistingConf = os.path.isfile("mica.conf")

        #push cwd to find your way back, and make a tmp output dir to run thepin
        cwd = os.getcwd()
        workingDir = micaOut
        #copy the conf from here if it exists
        if useExistingConf:
            shutil.copy("mica.conf", os.path.join(workingDir, "mica.conf"))

        os.chdir(workingDir)
        #make a new conf if you need
        if not useExistingConf:
            with open("mica.conf", 'w') as ofile:
                ofile.write("analysis_type: itypes\n")
                ofile.write("interval_size: full\n")
                ofile.write("itypes_spec_file: hierarchical")
        #run pin
        execAndLog("{} -t {} -- {}".format(self.pin, self.micaLib, app))
        # parse the cryptic mica file to get the outputs
        self.formatMicaOutput()

        #Pin has run successfully! Now we return to cwd and move the outputs
        os.chdir(cwd)
        #copy the instruction counts to results
        shutil.copy(os.path.join(micaOut,"instrCounts.txt"), 
                os.path.join(self.resultsDir, "instrCounts.txt"))

    def printResults(self):
        '''
        just convenience for oupting the results that you've generated at the 
        end of the script
        '''
        for filename in os.listdir(self.resultsDir):
            os.system("cat {}".format(os.path.join(self.resultsDir, filename)))
            os.system("echo")


def execAndLog(cmd):
    print("executing: {}".format(cmd))
    os.system(cmd)


if __name__ == "__main__":
    outDir="DummyOut"
    app="./Dummy/bin/dummy /data2/kaplannp/Genomics/Datasets/Kernels/Dummy"
    execAndLog("rm -rf {}".format(outDir))
    runner = Runner(outDir)
    runner.runVtuneUarch(app)
    runner.runVanillaApp(app)
    runner.runPinInstrCount(app)
    runner.runVtuneCache(app)
    runner.printResults()

    #outDir="GbwtOut"
    #app="./Gbwt/bin/gbwt /data2/kaplannp/Genomics/Datasets/Kernels/smallGbwt"
    #execAndLog("rm -rf {}".format(outDir))
    #runner = Runner(outDir)
    #runner.runVanillaApp(app)
    #runner.runPinInstrCount(app)
    #runner.runVtuneUarch(app)
    #runner.runVtuneCache(app)
    #runner.printResults()
    #runner = Runner(outDir)
    #runner.runPinInstrCount(app)
    #runner.runVtuneUarch(app)
#GSSW="./Gssw/bin/gssw /data2/kaplannp/Genomics/Datasets/Kernels/Gssw"
#GBV="./Gbv/bin/gbv /data2/kaplannp/Genomics/Datasets/Kernels/Gbv"
