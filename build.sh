#update the submodules to get mica pin
git submodule update --init --recursive

#first build the header library
cd RoiCppHeaders
make
cd ..

#build the intel script
cd deps
wget https://software.intel.com/sites/landingpage/pintool/downloads/pin-external-3.31-98861-g71afcc22f-gcc-linux.tar.gz
tar -xzvf pin-external-3.31-98861-g71afcc22f-gcc-linux.tar.gz
rm pin-external-3.31-98861-g71afcc22f-gcc-linux.tar.gz
mv pin-external-3.31-98861-g71afcc22f-gcc-linux IntelPin
cp -r MICA-Pausable IntelPin/source/tools/
cd IntelPin/source/tools/MICA-Pausable
make -j
cd ../../../../
