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

from .request import get_user_data, get_user_id_by_name
from .tag import Tag
from .comments import Comments
from .search import Search
from .galleries import Galleries
from .posts import SearchPosts

__all__ = [
  "Profile"
]

class Profile(object):
  def __init__(self, user_id, username="", url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self.url_domain = url_domain
    if user_id is None:
      user_id = get_user_id_by_name(username, url_domain=url_domain, proxies=proxies)
    self._data = get_user_data(user_id, url_domain=url_domain, proxies=proxies)
    for field, body in self.data.items():
      if not hasattr(self, field):
        setattr(self, field, body)

  def __str__(self):
    return f'''Profile({self.name})'''

  @property
  def data(self):
    return self._data
       
  @property
  def url(self):
    return f"{self.url_domain}/profiles/{self.slug}"

  def update(self):
    data = get_user_data(self.id, url_domain=self.url_domain, proxies=self.proxies)

    if data:
      self._data = data

  def awards(self):
    for award_data in self.data['awards']:
      yield Award(award_data)

  def links(self):
    for link_data in self.data['links']:
      yield Link(link_data, url_domain=self.url_domain, proxies=self.proxies)

  def comments(self, key="", limit=50, filter_id="", per_page=25, page=1):
    return Comments(user_id=self.id, key=key, limit=limit, filter_id=filter_id,
                    per_page=per_page, page=page,
                    url_domain=self.url_domain, proxies=self.proxies)

  def uploads(self, key="", sf="created_at", sd="desc", limit=50,
              filter_id="", per_page=25, page=1):
    return Search(q=(f"uploader_id:{self.id}",), key=key, sf=sf, sd=sd,
                  limit=limit, filter_id=filter_id, per_page=per_page,
                  page=page, url_domain=self.url_domain, proxies=self.proxies)

  def favorites(self, key="", sf="created_at", sd="desc", limit=50,
                filter_id="", per_page=25, page=1):
    return Search(q=(f"faved_by_id:{self.id}",), key=key, sf=sf, sd=sd,
                  limit=limit, filter_id=filter_id, per_page=per_page,
                  page=page, url_domain=self.url_domain, proxies=self.proxies)

  def artworks(self, key="", sf="created_at", sd="desc", limit=50,
               filter_id="", per_page=25, page=1):
    artist_tags = {link.tag.name for link in self.links()}
    return Search(q=artist_tags, key=key, sf=sf, sd=sd,
                  limit=limit, filter_id=filter_id, per_page=per_page,
                  page=page, url_domain=self.url_domain, proxies=self.proxies)

  def galleries(self, key="", limit=50, per_page=25, page=1):
    return Galleries(self, key=key, q=(f"user:{self.name}",), limit=limit,
                     per_page=per_page, page=page,
                     url_domain=self.url_domain, proxies=self.proxies)

  def posts(self, limit=50, per_page=25, page=1):
    return SearchPosts(q={f"user_id:{self.id}",}, limit=limit, per_page=per_page,
                       page=page, url_domain=self.url_domain, proxies=self.proxies)

class Award(object):
  def __init__(self, data):
    self._data = data
    for field, body in self.data.items():
      if not hasattr(self, field):
        setattr(self, field, body)

  def __str__(self):
    return f'''Badge({self.title})'''

  @property
  def data(self):
    return self._data

class Link(object):
  def __init__(self, data, url_domain="https://derpibooru.org", proxies={}):
    self.proxies = proxies
    self._data = data
    for field, body in self.data.items():
      if not hasattr(self, field):
        setattr(self, field, body)

  def __str__(self):
    return f'''Link({self.title})'''

  @property
  def data(self):
    return self._data

  @property
  def tag(self):
    return Tag(None, tag_id=self.data["tag_id"],
               url_domain=self.url_domain, proxies=self.proxies)

