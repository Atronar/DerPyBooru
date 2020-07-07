# -*- coding: utf-8 -*-

# Copyright (c) 2014, Joshua Stone
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from .request import get_images, url, get_related, url_related
from .image import Image
from .helpers import tags, api_key, sort_format, join_params, user_option, set_limit, \
                     validate_filter, set_distance

__all__ = [
  "Search",
  "Related"
]

class Search(object):
  """
  Search() is the primary interface for interacting with Derpibooru's REST API.

  All properties are read-only, and every method returns a new instance of
  Search() to avoid mutating state in ongoing search queries. This makes object
  interactions predictable as well as making versioning of searches relatively
  easy.
  """
  def __init__(self, key="", q=set(), sf="created_at", sd="desc",
               limit=50, faves="", upvotes="", uploads="", watched="",
               filter_id="", per_page=25, page=1,
               reverse_url="", distance=0.25,
               url_domain="https://derpibooru.org", proxies={}):
    """
    By default initializes an instance of Search with the parameters to get
    the first 25 images on Derpibooru's front page.
    For reverse searching by image use reverse_url field.
    """
    self.proxies = proxies
    self.url_domain = url_domain
    self._params = {
      "key": api_key(key),
      "reverse_url": reverse_url,
      "distance": set_distance(distance),
      "q": tags(q),
      "sf": sort_format(sf),
      "sd": sd,
      "filter_id": validate_filter(filter_id),
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }

    if faves:
      if self._params["key"] and faves is user.ONLY:
         self._params["q"] -= {"-my:faves"}
         self._params["q"].add("my:faves")
      elif self._params["key"] and faves is user.NOT:
         self._params["q"] -= {"my:faves"}
         self._params["q"].add("-my:faves")
    if upvotes:
      if self._params["key"] and upvotes is user.ONLY:
         self._params["q"] -= {"-my:upvotes"}
         self._params["q"].add("my:upvotes")
      elif self._params["key"] and upvotes is user.NOT:
         self._params["q"] -= {"my:upvotes"}
         self._params["q"].add("-my:upvotes")
    if uploads:
      if self._params["key"] and uploads is user.ONLY:
         self._params["q"] -= {"-my:uploads"}
         self._params["q"].add("my:uploads")
      elif self._params["key"] and uploads is user.NOT:
         self._params["q"] -= {"my:uploads"}
         self._params["q"].add("-my:uploads")
    if watched:
      if self._params["key"] and watched is user.ONLY:
         self._params["q"] -= {"-my:watched"}
         self._params["q"].add("my:watched")
      elif self._params["key"] and watched is user.NOT:
         self._params["q"] -= {"my:watched"}
         self._params["q"].add("-my:watched")
      
    self._limit = set_limit(limit)
    self._search = get_images(self._params, self._limit,
                              url_domain=self.url_domain, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Search() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Search().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/search?sd=desc&sf=created_at&q=%2A
    """
    return url(self.parameters, url_domain=self.url_domain)

  def key(self, key=""):
    """
    Takes a user's API key string which applies content settings. API keys can
    be found at <https://derpibooru.org/registration/edit>.
    """
    params = join_params(self.parameters, {"key": key,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def query(self, *q):
    """
    Takes one or more strings for searching by tag and/or metadata.
    """
    params = join_params(self.parameters, {"q": q,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def sort_by(self, sf):
    """
    Determines how to sort search results. Available sorting methods are
    sort.SCORE, sort.COMMENTS, sort.HEIGHT, sort.RELEVANCE, sort.CREATED_AT,
    and sort.RANDOM; default is sort.CREATED_AT.
    """
    params = join_params(self.parameters, {"sf": sf,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def descending(self):
    """
    Order results from largest to smallest; default is descending order.
    """
    params = join_params(self.parameters, {"sd": "desc",
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def ascending(self, sd="asc"):
    """
    Order results from smallest to largest; default is descending order.
    """
    params = join_params(self.parameters, {"sd": sd,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def limit(self, limit):
    """
    Set absolute limit on number of images to return, or set to None to return
    as many results as needed; default 50 posts. This limit on app-level.
    """
    params = join_params(self.parameters, {"limit": limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies})

    return self.__class__(**params)

  def filter(self, filter_id=""):
    """
    Takes a filter's ID to be used in the current search context. Filter IDs can
    be found at <https://derpibooru.org/filters/> by inspecting the URL parameters.
    
    If no filter is provided, the user's current filter will be used.
    """
    params = join_params(self.parameters, {"filter_id": validate_filter(filter_id),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)


  def faves(self, option):
    """
    Set whether to filter by a user's faves list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    if self.parameters["key"] and option is user.ONLY:
       query = self.query_remove("-my:faves").query_append("my:faves")
    elif self.parameters["key"] and option is user.NOT:
       query = self.query_remove("my:faves").query_append("-my:faves")
    else:
       query = self.query_remove("my:faves").query_remove("-my:faves")
    return query

  def upvotes(self, option):
    """
    Set whether to filter by a user's upvoted list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    if self.parameters["key"] and option is user.ONLY:
       query = self.query_remove("-my:upvotes").query_append("my:upvotes")
    elif self.parameters["key"] and option is user.NOT:
       query = self.query_remove("my:upvotes").query_append("-my:upvotes")
    else:
       query = self.query_remove("my:upvotes").query_remove("-my:upvotes")
    return query

  def uploads(self, option):
    """
    Set whether to filter by a user's uploads list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    if self.parameters["key"] and option is user.ONLY:
       query = self.query_remove("-my:uploads").query_append("my:uploads")
    elif self.parameters["key"] and option is user.NOT:
       query = self.query_remove("my:uploads").query_append("-my:uploads")
    else:
       query = self.query_remove("my:uploads").query_remove("-my:uploads")
    return query

  def watched(self, option):
    """
    Set whether to filter by a user's watchlist. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    if self.parameters["key"] and option is user.ONLY:
       query = self.query_remove("-my:watched").query_append("my:watched")
    elif self.parameters["key"] and option is user.NOT:
       query = self.query_remove("my:watched").query_append("-my:watched")
    else:
       query = self.query_remove("my:watched").query_remove("-my:watched")
    return query

  def top(self):
     """
     Returns search for Trending Images from front page.
     """
     return self.query('first_seen_at.gt:3 days ago').sort_by(sort.SCORE)
  
  # ids - list of int
  def exclude_by_id(self,*ids):
     """
     Excludes images from search by id.
     """
     return self.query_remove(f"id:{elem}" for elem in ids).query_append(f"-id:{elem}" for elem in ids)

  def query_append(self,*q):
     """
     Adds tags to current search.
     """
     query = self.parameters['q'].union(q)
     params = join_params(self.parameters, {"q": query,
                                            "limit": self._limit,
                                            "url_domain": self.url_domain,
                                            "proxies": self.proxies}
                         )

     return self.__class__(**params)

  def query_remove(self,*q):
     """
     Removes tags from current search.
     """
     query = self.parameters['q'].difference(q)
     params = join_params(self.parameters, {"q": query,
                                            "limit": self._limit,
                                            "url_domain": self.url_domain,
                                            "proxies": self.proxies}
                         )

     return self.__class__(**params)

  def get_related(self,image):
    if isinstance(image,Image):
      return Related(image, key=self.parameters['key'], limit=self._limit,
                     filter_id=self.parameters['filter_id'],
                     per_page=self.parameters['per_page'],
                     url_domain=self.url_domain, proxies=self.proxies)
    else:
      return Related(Image(None, image_id=image, url_domain=self.url_domain, proxies=self.proxies),
                     key=self.parameters['key'], limit=self._limit,
                     filter_id=self.parameters['filter_id'],
                     per_page=self.parameters['per_page'],
                     url_domain=self.url_domain, proxies=self.proxies)

  def get_page(self,page):
    """
    Set page for gets result of search.
    """
    params = join_params(self.parameters, {"page": set_limit(page),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def per_page(self,limit):
    """
    Set absolute limit on number of images to get, or set to None to return
    defaulting 25 posts; max 50 posts. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def reverse(self,url):
    """
    Takes an url image for reverse search.
    """
    params = join_params(self.parameters, {"reverse_url": url,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def distance(self,distance):
    """
    Match distance for reverse search (suggested values: between 0.2 and 0.5)
    """
    params = join_params(self.parameters, {"distance": set_distance(distance),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Image().
    """
    return Image(next(self._search), search_params=self.parameters,
                 url_domain=self.url_domain, proxies=self.proxies)

class Related(Search):
  """
  Related() is the Search-like interface based on related images instead query.
  Related images gets with old API in JSON and with new API in Web.
  This class should returns Search() for any query-like actions.
  """
  def __init__(self, image, key="", limit=50,
               filter_id="", per_page=25,
               url_domain="https://derpibooru.org", proxies={}):
    """
    By default initializes with the parameters to get the first 25 related images.
    """
    if proxies:
      self.proxies = proxies
    else:
      self.proxies = image.proxies
    self.url_domain = url_domain
    self.image = image
    self._params = {
      "key": api_key(key) if key else api_key(image._params['key']),
      "filter_id": validate_filter(filter_id),
      "per_page": set_limit(per_page)
    }
    self._limit = set_limit(limit)
    self._search = get_related(self.image.id, self._params, self._limit,
                               url_domain=self.url_domain, proxies=self.proxies)

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/images/***/related?key=&filter_id=&per_page=25
    """
    return url_related(self.image.id, self.parameters, url_domain=self.url_domain)

  def query(self, *q):
    """
    Takes one or more strings for searching by tag and/or metadata.
    """
    params = join_params(self.parameters, {"q": q,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )
    return Search(**params)

  def sort_by(self, sf):
    """
    Related() can't be sorted.
    """
    return self

  def descending(self):
    """
    Related() can't be sorted.
    """
    return self

  def ascending(self, sd="asc"):
    """
    Related() can't be sorted.
    """
    return self
  
  def query_append(self,*q):
    """
    Synonyme of query() for Related().
    """
    return self.query(q)

  def query_remove(self,*q):
    """
    Nothing remove from Related().
    """
    return self

  def get_page(self,page):
    """
    Related() hasn't pages.
    """
    return self

  def reverse(self,url):
    """
    Takes an url image for reverse search.
    """
    params = join_params(self.parameters, {"reverse_url": url,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return Search(**params)

  def distance(self,distance):
    """
    It hasn't any sense in Related()
    """
    return self