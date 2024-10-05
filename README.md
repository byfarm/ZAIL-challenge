# ZAIL-challenge
Byron Farmar - Mechanical Engineering student at Gonzaga University

Scraper for google results page

Currently only gets the default cards from results but can be extended to get 
videos, etc.

Developed on MacOs using Firefox so headers are included in the request that 
have google render the response like it is expecting that machine. Removing the
headers will break the scraper.

Dependencies:
* Python 3.12^
* anyio          4.6.0     High level compatibility layer for multiple asynchronous event loop implementations
* asttokens      2.4.1     Annotate AST trees with source code positions
* beautifulsoup4 4.12.3    Screen-scraping library
* bs4            0.0.2     Dummy package for Beautiful Soup (beautifulsoup4)
* certifi        2024.8.30 Python package for providing Mozilla's CA Bundle.
* devtools       0.12.2    Python's missing debug print command, and more.
* executing      2.1.0     Get the currently executing AST node of a frame, and other information
* h11            0.14.0    A pure-Python, bring-your-own-I/O implementation of HTTP/1.1
* httpcore       1.0.6     A minimal low-level HTTP client.
* httpx          0.27.2    The next generation HTTP client.
* idna           3.10      Internationalized Domain Names in Applications (IDNA)
* pygments       2.18.0    Pygments is a syntax highlighting package written in Python.
* six            1.16.0    Python 2 and 3 compatibility utilities
* sniffio        1.3.1     Sniff out which async library your code is running under
* soupsieve      2.6       A modern CSS selector implementation for Beautiful Soup.

if you have the repo and have [poetry](https://python-poetry.org/) installed then you can run 

```poetry install```

in the root of the repo and it should install all dependencies. Otherwise,

```pip3 install bs4 httpx devtools```

should take care of it (make sure you run in a venv).
