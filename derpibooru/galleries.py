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

from .request import get_galleries, url_galleries
from .gallery import Gallery
from .helpers import tags, api_key, join_params, set_limit

__all__ = [
  "Galleries"
]

class Galleries(object):
  """
  All properties are read-only, and every method returns a new instance of
  Galleries() to avoid mutating state in ongoing search queries. This makes object
  interactions predictable as well as making versioning of searches relatively
  easy.
  """
  def __init__(self, key="", q=set(), limit=50,
               per_page=25, page=1,
               url_domain="https://derpibooru.org", proxies={}):
    """
    By default initializes an instance of Galleries with the parameters to get
    the first 25 galleries on Derpibooru's galleries page.
    """
    self.proxies = proxies
    self.url_domain = url_domain
    self._params = {
      "key": api_key(key),
      "q": tags(q),
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }
    self._limit = set_limit(limit)
    self._search = get_galleries(self._params, self._limit,
                                 url_domain=self.url_domain, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Galleries() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Galleries().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/galleries?gallery[title]=*&gallery[description]=&gallery[creator]=&gallery[include_image]=&gallery[sf]=created_at&gallery[sd]=desc
    """
    return url_galleries(self.parameters, url_domain=self.url_domain)

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

  def limit(self, limit):
    """
    Set absolute limit on number of galleries to return, or set to None to return
    as many results as needed; default 50 galleries. This limit on app-level.
    """
    params = join_params(self.parameters, {"limit": limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies})

    return self.__class__(**params)

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
    Set absolute limit on number of galleries to get, or set to None to return
    defaulting 25 galleries; max 50 galleries. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Gallery().
    """
    return Gallery(next(self._search), search_params=self.parameters,
                   url_domain=self.url_domain, proxies=self.proxies)