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

from .request import get_tags, url_tags
from .tag import Tag
from .helpers import tags, join_params, set_limit

__all__ = [
  "Tags"
]

class Tags(object):
  """
  Tags() is the interface for interacting with Derpibooru's API similar on Search().

  All properties are read-only, and every method returns a new instance of
  Tags() to avoid mutating state in ongoing search queries. This makes object
  interactions predictable as well as making versioning of searches relatively
  easy.
  """
  def __init__(self, q=set(), limit=50, per_page=25, page=1, proxies={}):
    """
    By default initializes an instance of Tags with the parameters to get
    the first 25 comments on Derpibooru's comments activity page.
    """
    self.proxies = proxies
    self._params = {
      "q": tags(q),
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }
    self._limit = set_limit(limit)
    self._search = get_tags(self._params, self._limit, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Comments() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Comments().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/tags?tq=%2A
    """
    return url_tags(self._params)

  def query(self, *q):
    """
    Takes one or more strings for searching by query.
    """
    params = join_params(self.parameters, {"q": q, "proxies": self.proxies})

    return self.__class__(**params)

  def limit(self, limit):
    """
    Set absolute limit on number of images to return, or set to None to return
    as many results as needed; default 50 posts. This limit on app-level.
    """
    self._limit = set_limit(limit)

    return self.__class__(**params)

  def query_append(self,*q):
     """
     Adds query to current search.
     """
     query = self._params['q'].union(q)
     params = join_params(self.parameters, {"q": query, "proxies": self.proxies})

     return self.__class__(**params)

  def query_remove(self,*q):
     """
     Removes query from current search.
     """
     query = self._params['q'].difference(q)
     params = join_params(self.parameters, {"q": query, "proxies": self.proxies})

     return self.__class__(**params)

  def get_page(self,page):
    """
    Set returned page of search.
    """
    params = join_params(self.parameters, {"page": set_limit(page), "proxies": self.proxies})

    return self.__class__(**params)

  def per_page(self,limit):
    """
    Set absolute limit on number of images to get, or set to None to return
    defaulting 25 posts; max 50 posts. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit), "proxies": self.proxies})

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Tag().
    """
    return Tag(next(self._search), proxies=self.proxies)
