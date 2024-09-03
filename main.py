from runBenchmark import *

outDir="Out"
app="./Examples/Dummy/main"
execAndLog("rm -rf {}".format(outDir))
runner = Runner(outDir)
runner.runVtuneUarch(app)
runner.runVanillaApp(app)
runner.runPinInstrCount(app)
runner.runVtuneCache(app)
runner.printResults()
