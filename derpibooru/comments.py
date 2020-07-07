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

from .request import get_comments, url_comments
from .comment import Comment
from .helpers import search_comments_fields, api_key, join_params, set_limit, validate_filter

__all__ = [
  "Comments"
]

class Comments(object):
  """
  Comments() is the interface for interacting with Derpibooru's API similar on Search().

  All properties are read-only, and every method returns a new instance of
  Comments() to avoid mutating state in ongoing search queries. This makes object
  interactions predictable as well as making versioning of searches relatively
  easy.
  """
  def __init__(self, key="", q=set(), limit=50, filter_id="",
               author="", body="", created_at="", comment_id="", image_id="",
               my=None, user_id="", per_page=25, page=1,
               url_domain="https://derpibooru.org", proxies={}):
    """
    By default initializes an instance of Comments with the parameters to get
    the first 25 comments on Derpibooru's comments activity page.
    """
    self.proxies = proxies
    self.url_domain = url_domain
    self._params = {
      "key": api_key(key),
      "q": search_comments_fields(q, author=author, body=body,
                                  created_at=created_at, comment_id=comment_id,
                                  image_id=image_id, my=my, user_id=user_id),
      "filter_id": validate_filter(filter_id),
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }
    self._limit = set_limit(limit)
    self._search = get_comments(self._params, self._limit, url_domain=self.url_domain, proxies=self.proxies)
  
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

    https://derpibooru.org/comments?qc=%2A
    """
    return url_comments(self._params, url_domain=self.url_domain)

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
    Takes one or more strings for searching by query.
    """
    params = join_params(self.parameters, {"q": q,
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

  def set_field(self, field, string):
    """
    Common function for set values in fields. When string starts with "-", appends tag "-field:value".
    """
    if string:
       if f"{string}".startswith("-"):
          query = self.query_remove(f"{field}:{string[1:]}").query_append(f"-{field}:{string[1:]}")
       else:
          query = self.query_remove(f"-{field}:{string}").query_append(f"{field}:{string}")
    else:
       exists_tags = set(filter(lambda tag: True
                                            if f"{tag}".startswith(f"field:")
                                               or f"{tag}".startswith(f"-{field}:")
                                            else False,
                                q)
                        )
       query = self.query_remove(exists_tags)
    return query

  def author(self, string=None):
    """
    Set the author of comment. Anonymous authors will never match this term.
    """
    return self.set_field("author", string)

  def created_at(self, string=None):
    """
    Set the creation time of comment in ISO 8601 format.
    """
    return self.set_field("created_at", string)

  def comment_id(self, string=None):
    """
    Set the numeric surrogate key for comment.
    """
    return self.set_field("id", string)

  def image_id(self, string=None):
    """
    Set the numeric surrogate key for the image comment belongs to.
    """
    return self.set_field("image_id", string)

  def my(self, my_value=None):
    """
    my:comments matches comments you have posted if you are signed in. 
    """
    if not self._params["key"] or my_value is None:
       return self.set_field("my", None)
    elif my_value:
       return self.set_field("my", "comments")
    else:
       return self.set_field("my", "-comments")

  def user_id(self, string=None):
    """
    Matches comments with the specified user_id. Anonymous users will never match this term.
    """
    return self.set_field("user_id", string)

  def query_append(self,*q):
     """
     Adds query to current search.
     """
     query = self._params['q'].union(q)
     params = join_params(self.parameters, {"q": query,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                         )

     return self.__class__(**params)

  def query_remove(self,*q):
     """
     Removes query from current search.
     """
     query = self._params['q'].difference(q)
     params = join_params(self.parameters, {"q": query,
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                         )

     return self.__class__(**params)

  def get_page(self,page):
    """
    Set returned page of search.
    """
    params = join_params(self.parameters, {"page": set_limit(page),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def per_page(self,limit):
    """
    Set absolute limit on number of comments to get, or set to None to return
    defaulting 25 posts; max 50 posts. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Comment().
    """
    return Comment(next(self._search), url_domain=self.url_domain, proxies=self.proxies)
