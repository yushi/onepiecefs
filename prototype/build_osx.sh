#!/bin/bash

PWD=`pwd`
WORK_DIR=${PWD}/opfsbuild
PYTHON_DL_URL="http://www.python.org/ftp/python/2.7/Python-2.7.tar.bz2"
FUSE_PYTHON_URL="http://pypi.python.org/packages/source/f/fuse-python/fuse-python-0.2.tar.gz#md5=68be744e71a42cd8a92905a49f346278"
INSTALL_PATH=`echo ~/opfs`
if [ ! -d /Library/Frameworks/MacFUSE.framework ];then
    echo -e "MacFuse not installed\n\thttp://code.google.com/p/macfuse/"
    exit
fi

mkdir ${WORK_DIR}
mkdir ${WORK_DIR}/include
touch ${WORK_DIR}/include/osreldate.h

cd ${WORK_DIR}
wget ${PYTHON_DL_URL}
tar jxf Python-2.7.tar.bz2 

cd Python-2.7
./configure --prefix=${INSTALL_PATH}/python27
make && make install
cd ..


export CFLAGS_TMP=$CFLAGS
export CFLAGS="${CFLAGS} -I${WORK_DIR}/include"
wget $FUSE_PYTHON_URL
tar zxf fuse-python-0.2.tar.gz
cd fuse-python-0.2
${INSTALL_PATH}/python27/bin/python setup.py install
cd ..

rm -rf ${WORK_DIR}
export CFLAGS=$CFLAGS_TMP

echo -e "\nbuild finished"

