#!/bin/bash

appcfg.py upload_data \
    --config_file=bulkloader.yaml \
    --filename=import.csv \
    --kind=Course \
    --url http://courses-epfl.appspot.com/_ah/remote_api
