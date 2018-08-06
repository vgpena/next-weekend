# next weekend

This project repackages data from [OregonHikers.org](http://www.oregonhikers.org) into a more usable, readable format.

Current output is a CSV which can be imported into Google My Maps. The most recent map is [here](https://www.google.com/maps/d/edit?hl=es&mid=1ezjdM8suiJzJKp_QuxbYRQRNj3Zpx2_H&ll=45.48824113998795%2C-122.17070642031251&z=11).

## installation
- With virtualenv and virtualenvwrapper installed, make and workon an environment using Python 3.6.3
- `pip install -r requirements/base.txt`

## usage
- In that environment, run `python scraper.py`. Once it's done running, you will have `hikes.csv`.
- This can be imported into Google My Maps as a data layer.

## development
- To get dev dependencies, run `pip install -r requirements/dev.txt`.