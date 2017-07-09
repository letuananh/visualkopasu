#!/bin/bash

function link_folder {
    FOLDER_PATH=$1
    SYMLINK_NAME=$2
    if [ ! -d ${SYMLINK_NAME} ]; then
        ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
    else
        echo "Folder ${SYMLINK_NAME} exists."
    fi
}

function link_file {
    FOLDER_PATH=$1
    SYMLINK_NAME=$2
    if [ ! -f ${SYMLINK_NAME} ]; then
        ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
    else
        echo "File ${SYMLINK_NAME} exists."
    fi
}

# git submodule sync && git submodule init && git submodule update

cd modules/intsem.fx/
git submodule init && git submodule update
cd ../../
link_folder `readlink -f ./modules/intsem.fx/coolisf` coolisf
link_folder `readlink -f ./modules/intsem.fx/djangoisf` djangoisf
link_folder `readlink -f ./modules/intsem.fx/modules/chirptext/chirptext` chirptext
link_folder `readlink -f ./modules/intsem.fx/modules/puchikarui/puchikarui` puchikarui
link_folder `readlink -f ./modules/intsem.fx/modules/lelesk/lelesk` lelesk
link_folder `readlink -f ./modules/intsem.fx/modules/yawlib/yawlib` yawlib
link_folder `readlink -f ./modules/intsem.fx/modules/yawlib/yawoldjango` yawoldjango

./manage.py migrate
