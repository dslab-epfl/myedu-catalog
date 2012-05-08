#!/bin/bash

BASE_URL=http://courses-epfl.appspot.com

if [ "$1" == "--local" ]; then
    echo "-- Populating locally"
    BASE_URL=http://localhost:8080
fi

appcfg.py upload_data \
    --config_file=bulkloader.yaml \
    --filename=import.csv \
    --kind=Course \
    --url "$BASE_URL/_ah/remote_api"
