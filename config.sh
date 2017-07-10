#!/bin/bash

bold=$(tput bold)
normal=$(tput sgr0)
py3=`python -c "import sys; print('1' if sys.version_info >= (3,0) else '0')"`

function link_folder {
    FOLDER_PATH=$1
    SYMLINK_NAME=$2
    if [ ! -d ${FOLDER_PATH} ]; then
        echo "WARNING: Target folder ${bold}${FOLDER_PATH}${normal} does not exist"
    elif [ ! -d ${SYMLINK_NAME} ]; then
	ln -sv ${FOLDER_PATH} ${SYMLINK_NAME}
    else
	echo "Folder ${bold}${SYMLINK_NAME}${normal} exists."
    fi
}

function link_file {
    TARGET_FILE=$1
    SYMLINK_NAME=$2
    if [ ! -f ${TARGET_FILE} ]; then
        echo "WARNING: Target file ${bold}${TARGET_FILE}${normal} does not exist"
    elif [ ! -f ${SYMLINK_NAME} ]; then
	ln -sv ${TARGET_FILE} ${SYMLINK_NAME}
    else
	echo "File ${bold}${SYMLINK_NAME}${normal} exists."
    fi
}

if [ ${py3} -eq 0 ]; then
    echo "+-------------------------------+"
    echo "| WARNING: Python 3 is required |"
    echo "+-------------------------------+"
fi

# Config Coolisf 
cd modules/intsem.fx/
if [ ! -d './modules/chirptext/chirptext' ]; then
    git submodule init && git submodule update
fi
./config.sh
cd ../../

# Link required modules
link_folder `readlink -f ./modules/intsem.fx/coolisf` coolisf
link_folder `readlink -f ./modules/intsem.fx/djangoisf` djangoisf
link_folder `readlink -f ./modules/intsem.fx/modules/chirptext/chirptext` chirptext
link_folder `readlink -f ./modules/intsem.fx/modules/puchikarui/puchikarui` puchikarui
link_folder `readlink -f ./modules/intsem.fx/modules/lelesk/lelesk` lelesk
link_folder `readlink -f ./modules/intsem.fx/modules/yawlib/yawlib` yawlib
link_folder `readlink -f ./modules/intsem.fx/modules/yawlib/yawoldjango` yawoldjango

./manage.py migrate
