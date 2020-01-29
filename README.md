# BDX Departure checker

## Requirements 

* Python 3.6+
* virtualenv

## Installation

* Copy files or clone repository
* In project folder, set virtual environment and activate according to your operating system
* Install dependencies `$ pip install -r requirements.txt`

## Run tests

`(venv) pytest`

## Usage

```
(venv) python ./ -h

usage: [-h] time

BDX TRAFFIC CHECKER

positional arguments:
  time        Time to check for (hh:mm)

optional arguments:
  -h, --help  show this help message and exit
```

Example

```
(venv) python ./ 14:28

BDX TRAFFIC CHECKER

Prevision: 2344 @ 14:30
Minimum: 247 @ 07:00
Maximum: 15480 @ 18:05
Average: 5394

It's a great time to leave :)
```