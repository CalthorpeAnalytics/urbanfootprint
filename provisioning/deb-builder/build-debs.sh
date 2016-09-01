#!/bin/bash -e

NUM_CORES=$(grep -c ^processor /proc/cpuinfo)

mkdir -p /opt/uf-provisioning/ \
    && cd /opt/uf-provisioning/ \
    && rm -f *deb

cd /opt/uf-provisioning/

# Original source: http://appsforms.esri.com/products/download/index.cfm?fuseaction=download.main&downloadid=841
wget https://s3-us-west-2.amazonaws.com/uf-provisioning/FileGDB_API_1_3-64.tar.gz

# Original source: http://download.osgeo.org/geos/geos-3.4.2.tar.bz2
wget https://s3-us-west-2.amazonaws.com/uf-provisioning/geos-3.4.2.tar.bz2

# Original source: http://download.osgeo.org/proj/proj-4.8.0.tar.gz
wget https://s3-us-west-2.amazonaws.com/uf-provisioning/proj-4.8.0.tar.gz

# Original source: http://download.osgeo.org/gdal/1.10.1/gdal-1.10.1.tar.gz
wget https://s3-us-west-2.amazonaws.com/uf-provisioning/gdal-1.10.1.tar.gz

# FILEGDB
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++ INSTALLING FILEGDB"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
time (cd /opt/uf-provisioning/ \
    && tar -xzf FileGDB_API_1_3-64.tar.gz \
    && cp -r FileGDB_API /usr/local/FileGDB_API \
    && ln -sf /usr/local/FileGDB_API/lib/* /usr/local/lib/ \
    && ldconfig -v)

# PROJ
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++ COMPILING PROJ"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
time (cd /opt/uf-provisioning/ \
    && mkdir -p /opt/uf-provisioning/proj-4.8.0-TARGET \
    && tar -zxf proj-4.8.0.tar.gz \
    && cd proj-4.8.0 \
    && ./configure \
    && make -j${NUM_CORES} \
    && make -j${NUM_CORES} install \
    && ldconfig \
    && make install DESTDIR=/opt/uf-provisioning/proj-4.8.0-TARGET)

cd /opt/uf-provisioning/
time fpm -s dir \
         -t deb \
         -n proj \
         -v 4.8.0 \
         -C /opt/uf-provisioning/proj-4.8.0-TARGET \
         -p uf-proj_VERSION_ARCH.deb

# GEOS
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++ COMPILING GEOS"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
time (cd /opt/uf-provisioning/ \
    && mkdir -p geos-3.4.2-TARGET \
    && tar -xjf geos-3.4.2.tar.bz2 \
    && cd geos-3.4.2 \
    && ./configure \
    && make -j${NUM_CORES} \
    && make -j${NUM_CORES} install \
    && make install DESTDIR=/opt/uf-provisioning/geos-3.4.2-TARGET \
    && ldconfig)

# FPM GEOS
cd /opt/uf-provisioning/
time fpm -s dir \
         -t deb \
         -n geos \
         -v 3.4.2 \
         -C /opt/uf-provisioning/geos-3.4.2-TARGET \
         -p uf-geos_VERSION_ARCH.deb

# GDAL
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "+++ COMPILING GDAL"
echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
time (cd /opt/uf-provisioning/ \
    && mkdir -p gdal-1.10.1-TARGET \
    && tar -xzf gdal-1.10.1.tar.gz \
    && cd gdal-1.10.1 \
    && export LD_LIBARY_PATH='/usr/local/FileGDB_API/lib' \
    && ./configure --with-python --with-fgdb=/usr/local/FileGDB_API \
    && make -j${NUM_CORES} \
    && make -j${NUM_CORES} install \
    && make install DESTDIR=/opt/uf-provisioning/gdal-1.10.1-TARGET \
    && ldconfig)

# FPM GDAL
cd /opt/uf-provisioning/
time fpm -s dir \
         -t deb \
         -n gdal \
         -v 1.10.1 \
         -C /opt/uf-provisioning/gdal-1.10.1-TARGET \
         -p uf-gdal_VERSION_ARCH.deb

cd /opt/uf-provisioning/
echo "Copying deb files to ~ for safe-keeping...."
cp *deb /code
