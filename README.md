# dig-ed-cat-indexer
script to populate a Typesense Index with data from the Catalogue of Digital Editions


## how to

* clone the repo
* create virtual env and install requirements `pip install -r requirements.txt`
* copy and adapt `default.env` to `secret.env` and add typesense credentials
* configuration like schema definition or location of source files is done in `config.py`
* run `python index.py` to (re)index