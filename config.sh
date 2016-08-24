#!/usr/bin/sh

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

git submodule sync && git submodule init && git submodule update

cd modules/intsem.fx
git submodule sync && git submodule init && git submodule update
bash ./config.sh
cd ../../

link_folder `readlink -f ../beautifulsoup/bs4-python3` bs4
# link_folder `readlink -f ../pydelphin/delphin` delphin
# link_folder `readlink -f ../nltk/nltk` nltk

link_folder `readlink -f ./modules/chirptext/chirptext` chirptext
link_folder `readlink -f ./modules/puchikarui/puchikarui` puchikarui

link_folder `readlink -f ./modules/intsem.fx/lelesk` lelesk
link_folder `readlink -f ./modules/intsem.fx/coolisf` coolisf

# Grammars
link_file `readlink -f ~/workspace/grammars/erg.dat` data/erg.dat

./manage.py migrate
