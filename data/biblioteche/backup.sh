#!/bin/bash

COLLECTION=$1
if [ -d ${COLLECTION} ]; then
    find ${COLLECTION} -name "*.gz" | tar -zcvf ${COLLECTION}.tar.gz -T -
fi
