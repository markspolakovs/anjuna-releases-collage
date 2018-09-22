# anjuna-releases-collage

Generate a collage of Anjunabeats or Anjunadeep releases between key dates (eg. ABGTs)

## Installation

```sh
$ git clone https://github.com/markspolakovs/anjuna-releases-collage.git
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

## Usage

```sh
$ python collage.py -h
usage: collage.py [-h] [--rows ROWS] [--cols COLS] [--square_size SQUARE_SIZE]
                  label pages key_start key_end

positional arguments:
  label                 Which label to generate for
  pages                 How many pages of releases to scrape from
                        music.anjunabeats.com
  key_start             Which key date should we generate from
  key_end               Which key date should we generate until

optional arguments:
  -h, --help            show this help message and exit
  --rows ROWS           How many rows of releases should we generate
  --cols COLS           How many columns of releases should we generate
  --square_size SQUARE_SIZE
                        How big should each square be
$ python collage.py anjunadeep 2 ABGT250 ABGT300 
```
