# next weekend

This project repackages data from [OregonHikers.org](http://www.oregonhikers.org) into a more usable, readable format.

Current output is a CSV which can be imported into Google My Maps. The most recent map is [here](https://www.google.com/maps/d/edit?hl=es&mid=1ezjdM8suiJzJKp_QuxbYRQRNj3Zpx2_H&ll=45.48824113998795%2C-122.17070642031251&z=11).

## installation
- This project uses [pipenv](https://github.com/pypa/pipenv) for dependency management. Once you have pipenv installed:
  - `pipenv install`

## usage
- Run `pipenv shell` to work in a virtual environment, then run `python scraper.py`.
- This command will generate `hikes_db.tsv` and `hikes.csv`.
- `hikes.csv` can be imported into Google My Maps as a data layer.

## development
- To get dev dependencies, run `pipenv install --dev`.
- Linter is [pylint](https://www.pylint.org/), currently with all default settings. I recommend integrating it into your editor ✨