#!/bin/bash

nvtversion="1.0.18"
nvtserver="${2}"
nvtpackage="nvt-${nvtversion}.tar.gz"
nvtdir="/home/max/development/nvt"
nvtdir_build="${nvtdir}/build"

current=`pwd`
cd ${nvtdir_build}
make package_source
echo "Copy to Modron..."
scp -r $nvtpackage sukhanov@192.168.204.32:/home/sukhanov/nvt/
echo "Building NVT..."
ssh sukhanov@192.168.204.32 "cd /home/sukhanov/nvt && tar xvzf $nvtpackage && rm -f $nvtpackage && cd nvt-$nvtversion && mkdir build ; cd build && cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_MYSQL=1 && make -j4"
scp -r sukhanov@192.168.204.32:"/home/sukhanov/nvt/nvt-$nvtversion/build/bin/drivers/libnvtd_drivers.so" "/home/max/development/"
if [ "${1}" == "upload" ] ; then
  scp -r "/home/max/development/libnvtd_drivers.so" "root@$nvtserver:/root/"
  ssh "root@$nvtserver" "sv stop nvt; killall -9 nvtd; cp /root/libnvtd_drivers.so /usr/lib64/nvt/; sv start nvt"
fi
cd $current

