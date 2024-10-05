"""
Byron Farmar - Mechanical Engineering student at Gonzaga University
Scraper for google results page

Currently only gets the default cards from results but can be extended to get 
videos, etc.

Developed on MacOs using Firefox so headers are included in the request that 
have google render the response like it is expecting that machine. Removing the
headers will break the scraper.

Dependencies:
Python 3.12^
anyio          4.6.0     High level compatibility layer for multiple asynchronous event loop implementations
asttokens      2.4.1     Annotate AST trees with source code positions
beautifulsoup4 4.12.3    Screen-scraping library
bs4            0.0.2     Dummy package for Beautiful Soup (beautifulsoup4)
certifi        2024.8.30 Python package for providing Mozilla's CA Bundle.
devtools       0.12.2    Python's missing debug print command, and more.
executing      2.1.0     Get the currently executing AST node of a frame, and other information
h11            0.14.0    A pure-Python, bring-your-own-I/O implementation of HTTP/1.1
httpcore       1.0.6     A minimal low-level HTTP client.
httpx          0.27.2    The next generation HTTP client.
idna           3.10      Internationalized Domain Names in Applications (IDNA)
pygments       2.18.0    Pygments is a syntax highlighting package written in Python.
six            1.16.0    Python 2 and 3 compatibility utilities
sniffio        1.3.1     Sniff out which async library your code is running under
soupsieve      2.6       A modern CSS selector implementation for Beautiful Soup.

if you have the repo and have poetry installed then you can run 
```poetry install```
in the root of the repo and it should install all dependencies. Otherwise,
```pip3 install bs4 httpx devtools```
should take care of it (make sure you run in a venv).
"""

import sys  # for cli arguments
import httpx  # good async request library
import asyncio  # speeding up requests
from bs4 import BeautifulSoup, Tag  # parsing html
import re  # formatting scraped strings
import datetime  # metadata

# pretty printer for the output
from devtools import debug

client = httpx.AsyncClient()


def format_str(string: str) -> str:
    """utility function to format a result string"""
    return re.sub(r" +", " ", string).replace("\n", "")


class Result:
    """The result card the contains the good information"""

    url: str | None = None  # the link from google to the page
    title: str | None = None  # the title of the result
    description: str | None = None  # the description of the result

    def __init__(self, result: Tag) -> None:
        title_link = result.find("div", attrs={"data-snhf": True})
        description = result.find("div", attrs={"data-sncf": True})

        # parses out the title, link, and description.
        # allows the ability to add different cards if needed
        if title_link and description:
            self.organic_card(title_link, description)

    def organic_card(self, title: Tag, description: Tag):
        """
        parses an organic card (default search result)

        :param - title
        The html tag with the title contents

        :param - description
        The html tag with the description contents contents
        """
        # get the info from the tags and put into object
        self.url = title.find("a").attrs.get("href", "")
        self.title = format_str(title.find("h3").get_text(strip=True))

        self.description = format_str(description.get_text())

    def __repr__(self) -> str:
        return f"{self.title}, {self.url}, \n{self.description}"

    def jsonify(self):
        """Returns the contents as a dict object"""
        return {
            "url": self.url,
            "title": self.title,
            "description": self.description,
        }

    @property
    def is_valid(self) -> bool:
        """checks to see if it is a valid card"""
        return self.url and self.title and self.description


async def google_request(query: str, page: int):
    """
    sends the request out to google
    query: the query string the user is searching
    page: the page number of google to scrape
    """
    # the base google search url
    base_url: str = "https://www.google.com/search"

    # sets the parameters for the request
    params: dict[str, str] = {
        "q": query,
        "client": "firefox-b-1-d",
        "start": str(10 * page),  # looks like google expects 10 responses per page
    }

    # sets the headers so we get the response format we expect (firefox)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=0, i",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    # send out the request async
    response = await client.get(base_url, params=params, headers=headers)

    # check the response code
    if (sc := response.status_code) != 200:
        raise Exception(f"recieved status code {sc} in google call")

    # convert to parsing format
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


def get_results_tag(soup: BeautifulSoup) -> Tag:
    """
    parses the soup to get the info we want
    """
    # finds the search html tag
    search_results: Tag = soup.find("div", attrs={"id": "search"})
    if not search_results:
        raise Exception("cannot find search html tag")

    # gets the tag with all the contents as children
    return search_results.find("div", attrs={"id": "rso"})


def parse_results(response: Tag) -> list[dict]:
    """
    parses the results from the results section into local dict format
    response: the #search.#rso tag from the results page
    """
    results: list[dict] = []
    if not response:
        raise Exception(f"no results, {response}")

    for result in response.children:
        # navigable string or None has no contents so we do not want it
        if not isinstance(result, Tag):
            continue

        # if it has no children then it is not the tag we are looking for
        if not result.children:
            continue

        # convert to result object and check validity
        result_obj: Result = Result(result)
        if not result_obj.is_valid:
            continue

        # add to our resutls list
        results.append(result_obj.jsonify())

    return results


async def main(query="hello world", num_pages=10):
    """
    main runner function that organizes the code
    query: the query that google resorts are wanted for
    num_pages: how many pages of google results you want
    """
    # the results list which will be our main return data
    sc_results: list[dict] = []

    # metadat from our scrape (more will be added at end of foo)
    metadata: dict = {
        "query": query,
        "requested_at": datetime.datetime.now(datetime.UTC).strftime("%d/%m/%Y, %H:%M:%S.%f"),
    }

    # make the api calls async
    api_calls = [google_request(query, p) for p in range(num_pages)]

    # gather the calls and parse the results
    for api_result in await asyncio.gather(*api_calls):
        results = parse_results(get_results_tag(api_result))
        sc_results.extend(results)

    # add info to metadata
        metadata["processed_at"] = datetime.datetime.now(datetime.UTC).strftime("%d/%m/%Y, %H:%M:%S.%f")
    metadata["num_results"] = len(sc_results)

    # return dict structure
    return {"metadata": metadata, "results": sc_results}


if __name__ == "__main__":
    # make easy to run as cli
    if len(sys.argv) > 2:
        query, pages = sys.argv[1:]
        result = asyncio.run(main(query, int(pages)))
    else:
        result = asyncio.run(main())

    # debug is just a pretty printer
    debug(result)
