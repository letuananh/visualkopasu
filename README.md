Prerequisite
===========
* GNU/Linux Fedora
* Django version 1.9.6
* Python 3.4.2
* SQLite 3.11.0
* beautifulsoup
* numpy
* lxml
* pyDelphin 0.5.1 (https://github.com/delph-in/pydelphin)
* fuzzywuzzy (required by coolisf)
* python-levenshtein (optional for fuzzywuzzy)
* nltk (Use this version instead of NLTK's trunk: https://github.com/letuananh/nltk)
  + WordNet data should be downloaded (nltk.download() => `book` package)
* The Integrated Semantic Framework - CoolISF (https://github.com/letuananh/intsem.fx)
  + lelesk library (requires WordNet data - see LeLesk README file for more information)
* The LinGO English Resource Grammar (http://www.delph-in.net/erg/)
  + Generate grammar file (erg.dat) and copy it to data folder


Installation guide
===============

* Installed required packages using pip3
pip3 install django==1.9.6 numpy lxml pydelphin==0.5.1 nltk==3.2.1 fuzzywuzzy python-levenshtein

* Extract the visual_kopasu.tar.gz to a folder (e.g. /home/user/visualkopasu)
* Download sample dataset ("the Cathedral and the Bazaar") from: http://letuananh.dakside.org/home/download/cb.tgz
* Copy all data files of "the Cathedral and the Bazaar" 
	(non-wordnet with multiple DMRS & syntactic trees version)
	```cp redwoods/cb/*.gz $(PROJECT_ROOT)/data/corpora/raw/redwoods/cb/```
* Modify file config.py to point to actual project root
	```PROJECT_ROOT = '/home/user/visualkopasu'```
* From terminal run the following command:
	```cd ~/visualkopasu
	chmod +x manage.py```
	(The command below may take very long time to run!)
	```./manage.py```
	(OR ```python manage.py```)
	Make sure you have backed up old database before run setup script.
* Create django database (important!!!)
	```python manage.py migrate```
* Now, everytime we want to run the project, just type
	```cd ~/visualkopasu
	./manage.py runserver```
	(OR ```python manage.py runserver```)
	After the server is started, access the server from the URL:
	http://localhost:8000/
