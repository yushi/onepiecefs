#!/bin/bash
INSTALL_PATH=/opt/opfs
PWD=`pwd`
WORK_DIR=${PWD}/opfsbuild
PYTHON_DL_URL="http://www.python.org/ftp/python/2.7/Python-2.7.tar.bz2"
SETUPTOOLS_URL='http://pypi.python.org/packages/2.7/s/setuptools/setuptools-0.6c11-py2.7.egg#md5=fe1f997bc722265116870bc7919059ea'
PIP_URL='http://pypi.python.org/packages/source/p/pip/pip-0.8.1.tar.gz#md5=5d40614774781b118dd3f10c0d038cbc'

mkdir -p /opt/opfs
if [ $? -eq 1 ];then
    echo "can't write ${INSTALL_PATH}. please make writable (ex. sudo mkdir -p /opt/opfs && sudo chown you /opt/opfs)"
    exit
fi

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
cd ${WORK_DIR}

wget ${SETUPTOOLS_URL} 
PYTHONPATH=${INSTALL_PATH}/python27/lib/python2.7/site-packages sh setuptools-0.6c11-py2.7.egg --prefix=${INSTALL_PATH}/python27

wget ${PIP_URL}
tar zxvf pip-0.8.1.tar.gz
cd pip-0.8.1
${INSTALL_PATH}/python27/bin/python setup.py install

export CFLAGS_TMP=$CFLAGS
export CFLAGS="${CFLAGS} -I${WORK_DIR}/include"
${INSTALL_PATH}/python27/bin/pip install fuse-python
export CFLAGS=$CFLAGS_TMP

${INSTALL_PATH}/python27/bin/pip install tornado
${INSTALL_PATH}/python27/bin/pip install urlgrabber


cd ${WORK_DIR}

rm -rf ${WORK_DIR}

echo -e "\nbuild finished"

