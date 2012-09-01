#!/bin/bash

wget -e robots=off -k -H \
    -D 'search-test.epfl.ch,isa.epfl.ch' -r \
    http://search-test.epfl.ch/eduweb.action \
    -U Mozilla \
    --accept '*eduweb.action*,*studyplan.action*,*itffichecours.htm*' \
    --reject '*studyplan.action*request_locale=*'
