#unmake the lib
cd RoiCppHeaders
make clean
cd ..

#remove the intel pin
cd deps
rm -rf IntelPin
cd ..
