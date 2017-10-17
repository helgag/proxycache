# proxycache

Cache HTTP(s) responses of a domain using a simple proxy.

### Setup
Uses Python 2.7 in a virtual environment

```
virtualenv .env
source .env/bin/activate
pip install -r requirements.txt
```

To run (in virtual env), change `BASE_DOMAIN` in proxy.py to desired domain.
```
python proxy.py
```
