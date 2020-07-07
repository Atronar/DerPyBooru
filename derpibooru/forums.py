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

from .request import get_forums, get_forum_data, \
                     get_topics, url_topics, get_topic_data, \
                     get_posts, url_posts
from .helpers import join_params, set_limit, destructive_slug
from .post import Post

__all__ = [
  "Forums",
  "Forum",
  "Topics",
  "Topic",
  "Posts"
]

class Forums(object):
  def __init__(self, limit=50, per_page=25, page=1,
               url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain
    self._params = {
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }      
    self._limit = set_limit(limit)
    self._search = get_forums(self._params, self._limit, url_domain=self.url_domain, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Forums() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Forums().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a standart URL of avaliable forums list
    """
    return f"{self.url_domain}/forums"

  def limit(self, limit):
    """
    Set absolute limit on number of forums to return, or set to None to return
    as many results as needed; default 50 forums. This limit on app-level.
    """
    params = join_params(self.parameters, {"limit": limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies})

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
    Set absolute limit on number of forums to get, or set to None to return
    defaulting 25 forums; max 50 forums. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Forum().
    """
    return Forum(next(self._search), url_domain=self.url_domain, proxies=self.proxies)

class Forum(object):
  """
  This class provides a thin wrapper around JSON data, mapping each value to
  its own property. Once instantiated the data is immutable so as to reflect
  the stateless nature of a REST API.
  """
  def __init__(self, data, short_name=None,
               url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain

    if data is None and short_name:
      self._data = data = get_forum_data(short_name, url_domain=url_domain, proxies=proxies)
    else:
      self._data = data

    for field, body in data.items():
      if not hasattr(self, field):
        setattr(self, field, body) 

  def __str__(self):
    return f"Forum({self.name})"
       
  @property
  def url(self):
    return f"{self.url_domain}/forums/{self.short_name}"

  @property
  def data(self):
    return self._data

  def update(self):
    data = get_forum_data(self.short_name, url_domain=self.url_domain, proxies=self.proxies)

    if data:
      self._data = data

  def topics(self, limit=50, per_page=25, page=1):
    return Topics(self.short_name, limit=limit, per_page=per_page, page=page,
                  url_domain=self.url_domain, proxies=self.proxies)

class Topics(object):
  def __init__(self, forum_short_name, limit=50, per_page=25, page=1,
               url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain
    self.forum_short_name = forum_short_name
    self._params = {
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }      
    self._limit = set_limit(limit)
    self._search = get_topics(forum_short_name, self._params, self._limit,
                              url_domain=self.url_domain, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Topics() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Topics().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/forums/forum?page=1&per_page=25
    """
    return url_topics(self.forum_short_name, self.parameters, url_domain=self.url_domain)

  def limit(self, limit):
    """
    Set absolute limit on number of topics to return, or set to None to return
    as many results as needed; default 50 topics. This limit on app-level.
    """
    params = join_params(self.parameters, {"limit": limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies})

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
    Set absolute limit on number of topics to get, or set to None to return
    defaulting 25 topics; max 50 topics. This limit on API-level.
    """
    params = join_params(self.parameters, {"per_page": set_limit(limit),
                                           "limit": self._limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies}
                        )

    return self.__class__(**params)

  def __next__(self):
    """
    Returns a result wrapped in a new instance of Topic().
    """
    return Topic(next(self._search), forum_short_name=self.forum_short_name,
                 url_domain=self.url_domain, proxies=self.proxies)

class Topic(object):
  """
  This class provides a thin wrapper around JSON data, mapping each value to
  its own property. Once instantiated the data is immutable so as to reflect
  the stateless nature of a REST API.
  """
  def __init__(self, data, forum_short_name=None, topic_name=None, slug=True,
               url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain
    self.forum_short_name = forum_short_name

    if data is None and forum_short_name and topic_name:
      if not slug:
        topic_slug = destructive_slug(topic_name)
      else:
        topic_slug = topic_name
      self._data = data = get_topic_data(forum_short_name, topic_slug,
                                         url_domain=self.url_domain, proxies=proxies)
    else:
      self._data = data

    for field, body in data.items():
      if not hasattr(self, field):
        setattr(self, field, body) 

  def __str__(self):
    return f"Topic({self.title})"
       
  @property
  def url(self):
    if self.forum_short_name:
      return f"{self.url_domain}/forums/{self.forum_short_name}/topics/{self.slug}"

  @property
  def data(self):
    return self._data

  def update(self):
    if self.forum_short_name:
      data = get_topic_data(self.forum_short_name, self.slug,
                            url_domain=self.url_domain, proxies=self.proxies)
      if data:
        self._data = data

  def posts(self, forum_short_name="", limit=50, per_page=25, page=1):
    if not forum_short_name:
      forum_short_name = self.forum_short_name
    return Posts(forum_short_name, self.slug, slug=False, limit=limit,
                 per_page=per_page, page=page,
                 url_domain=self.url_domain, proxies=self.proxies)

class Posts(object):
  def __init__(self, forum_short_name, topic_name, slug=True, limit=50,
               per_page=25, page=1, url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain
    self.forum_short_name = forum_short_name
    if slug:
      self.topic_slug = destructive_slug(topic_name)
    else:
      self.topic_slug = topic_name
    self._params = {
      "per_page": set_limit(per_page),
      "page": set_limit(page)
    }
    self._limit = set_limit(limit)
    self._search = get_posts(self._params, forum_short_name=self.forum_short_name,
                             topic_slug=self.topic_slug, limit=self._limit,
                             url_domain=self.url_domain, proxies=self.proxies)
  
  def __iter__(self):
    """
    Make Posts() iterable so that new search results can be lazily generated
    for performance reasons.
    """
    return self

  @property
  def parameters(self):
    """
    Returns a list of available parameters; useful for passing state to new
    instances of Posts().
    """
    return self._params

  @property
  def url(self):
    """
    Returns a search URL built on set parameters. Example based on default
    parameters:

    https://derpibooru.org/forums/forum/topics/topic?page=1&per_page=25
    """
    return url_posts(self.forum_short_name, self.topic_slug, self.parameters, url_domain=self.url_domain)

  def limit(self, limit):
    """
    Set absolute limit on number of posts to return, or set to None to return
    as many results as needed; default 50 posts. This limit on app-level.
    """
    params = join_params(self.parameters, {"limit": limit,
                                           "url_domain": self.url_domain,
                                           "proxies": self.proxies})

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
    Set absolute limit on number of posts to get, or set to None to return
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
    Returns a result wrapped in a new instance of Post().
    """
    return Post(next(self._search), url_domain=self.url_domain, proxies=self.proxies)