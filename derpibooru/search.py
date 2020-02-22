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

from .request import get_images, url
from .image import Image
from .helpers import tags, api_key, sort_format, join_params, user_option, set_limit, validate_filter

__all__ = [
  "Search"
]

class Search(object):
  """
  Search() is the primary interface for interacting with Derpibooru's REST API.

  All properties are read-only, and every method returns a new instance of
  Search() to avoid mutating state in ongoing search queries. This makes object
  interactions predictable as well as making versioning of searches relatively
  easy.
  """
  def __init__(self, key="", q={}, sf="created_at", sd="desc", limit=50,
               faves="", upvotes="", uploads="", watched="", filter_id="", perpage=50, page=1, proxy={}):
    """
    By default initializes an instance of Search with the parameters to get
    the first 50 images on Derpibooru's front page.
    """
    self.proxy = proxy
    self._params = {
      "key": api_key(key),
      "q": tags(q),
      "sf": sort_format(sf),
      "sd": sd,
      "faves": user_option(faves),
      "upvotes": user_option(upvotes),
      "uploads": user_option(uploads),
      "watched": user_option(watched),
      "filter_id": validate_filter(filter_id),
      "perpage": perpage,
      "page": page
    }
    self._limit = set_limit(limit)
    self._search = get_images(self._params, self._limit, proxy=self.proxy)
  
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
    params = join_params(self._params, {"limit": self._limit})
    return params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/search?sd=desc&sf=created_at&q=%2A
    """
    return url(self._params)

  def key(self, key=""):
    """
    Takes a user's API key string which applies content settings. API keys can
    be found at <https://derpibooru.org/users/edit>.
    """
    params = join_params(self.parameters, {"key": key})

    return self.__class__(**params)

  def query(self, *q):
    """
    Takes one or more strings for searching by tag and/or metadata.
    """
    params = join_params(self.parameters, {"q": q})

    return self.__class__(**params)

  def sort_by(self, sf):
    """
    Determines how to sort search results. Available sorting methods are
    sort.SCORE, sort.COMMENTS, sort.HEIGHT, sort.RELEVANCE, sort.CREATED_AT,
    and sort.RANDOM; default is sort.CREATED_AT.
    """
    params = join_params(self.parameters, {"sf": sf})

    return self.__class__(**params)

  def descending(self):
    """
    Order results from largest to smallest; default is descending order.
    """
    params = join_params(self.parameters, {"sd": "desc"})

    return self.__class__(**params)

  def ascending(self, sd="asc"):
    """
    Order results from smallest to largest; default is descending order.
    """
    params = join_params(self.parameters, {"sd": sd})

    return self.__class__(**params)

  def limit(self, limit):
    """
    Set absolute limit on number of images to return, or set to None to return
    as many results as needed; default 50 posts.
    """
    params = join_params(self.parameters, {"limit": limit})

    return self.__class__(**params)

  def filter(self, filter_id=""):
    """
    Takes a filter's ID to be used in the current search context. Filter IDs can
    be found at <https://derpibooru.org/filters/> by inspecting the URL parameters.
    
    If no filter is provided, the user's current filter will be used.
    """
    params = join_params(self.parameters, {"filter_id": filter_id})

    return self.__class__(**params)


  def faves(self, option):
    """
    Set whether to filter by a user's faves list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    params = join_params(self.parameters, {"faves": option})

    return self.__class__(**params)

  def upvotes(self, option):
    """
    Set whether to filter by a user's upvoted list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    params = join_params(self.parameters, {"upvotes": option})

    return self.__class__(**params)

  def uploads(self, option):
    """
    Set whether to filter by a user's uploads list. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    params = join_params(self.parameters, {"uploads": option})

    return self.__class__(**params)

  def watched(self, option):
    """
    Set whether to filter by a user's watchlist. Options available are
    user.ONLY, user.NOT, and None; default is None.
    """
    params = join_params(self.parameters, {"watched": option})

    return self.__class__(**params)

  def top(self,limited=50):
     return self.sort_by(sort.SCORE).limit(limited).query('first_seen_at.gt:3 days ago')
  
  def get_non_upvoted(self,limited=50):
     return self.upvotes(user.NOT).limit(limited)

  def get_upvoted(self,limited=50):
     return self.query_append().limit(limited)

  # ids - list of int
  def exclude_by_id(self,ids=[]):
     q=''
     if ids:
        for elem in ids[:-1]:
           q = f'{q}-id:{elem},'
        q = f'{q}-id:{ids[-1]}'
     return q

  def query_append(self,*q):
     query = self._params['q'].union(q)
     params = join_params(self.parameters, {"q": query})

     return self.__class__(**params)

  def query_remove(self,*q):
     query = self._params['q'].difference(q)
     params = join_params(self.parameters, {"q": query})

     return self.__class__(**params)
  
  def is_upvoted(self,img_id):
     up = []
     for img in self.limit(1).query(f'id:{img_id}','my:upvotes'):
        up.append(img)
     if len(up)==0:
        return False;
     else:
        return True;

  def get_page(self,page):
    params = join_params(self.parameters, {"page": page})

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Image().
    """
    return Image(next(self._search), proxy=self.proxy)
