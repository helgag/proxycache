# proxycache

Cache HTTP(s) responses of a domain using a simple proxy.

### Install virtualenv
sudo pip install virtualenv

### Setup
Uses Python 2.7 in a virtual environment

```
virtualenv --python=/usr/bin/python2.7 .env
source .env/bin/activate
pip install -r requirements.txt
```

### Running
Change `BASE_DOMAIN` in proxy.py to desired domain.
```
source .env/bin/activate
python proxy.py
```
