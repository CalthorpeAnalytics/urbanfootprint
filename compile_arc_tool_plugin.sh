#!/bin/bash -e
cd ./footprint/upload_manager
if [[ -f ./arc_tool.py ]]
then
    rm ./urbanfootprint-arc-toolbox.zip
    cp ./arc_tool.py ./urbanfootprint-arc-toolbox/UrbanFootprint.pyt
    zip -j -r ./urbanfootprint-arc-toolbox.zip ./urbanfootprint-arc-toolbox/
fi
