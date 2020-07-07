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

from .request import get_tag_data, get_tags
from .helpers import slugging_tag

__all__ = [
  "Tag"
]

class Tag(object):
  def __init__(self, data, tag=None, slug=False, tag_id=None,
               url_domain="https://derpibooru.org", proxies={}):
    """
    tag field is slug.
    """
    self.proxies = proxies
    self.url_domain = url_domain
    if data is None and (tag or tag_id):
      if tag:
        if slug:
          self._data = data = get_tag_data(tag, url_domain=url_domain, proxies=proxies)
        else:
          self._data = data = get_tag_data(slugging_tag(tag),
                                           url_domain=url_domain, proxies=proxies)
      elif tag_id:
          self._data = data = next(get_tags({"q": (f"id:{tag_id}",), "per_page":1},
                                            limit=1, url_domain=url_domain, proxies=proxies)
                                  )
    else:
      self._data = data
    for field, body in self.data.items():
      if not hasattr(self, field):
        setattr(self, field, body)

  def __str__(self):
    return f'''Tag({self.name})'''

  @property
  def data(self):
    return self._data
       
  @property
  def url(self):
    """
    Also url for search image by single tag.
    """
    return f"{self.url_domain}/tags/{self.slug}"

  def update(self):
    data = get_tag_data(self.id, url_domain=self.url_domain, proxies=self.proxies)

    if data:
      self._data = data

  def allias_parent(self):
    """
    Return main Tag() for this tag.
    """
    if self.aliased_tag:
      return Tag(None, tag=self.aliased_tag, slug=True,
                 url_domain=self.url_domain, proxies=self.proxies)

  def allias_children(self):
    """
    Return in generator all alliases tags.
    """
    for tag in self.aliases:
      yield Tag(None, tag=tag, slug=True, url_domain=self.url_domain, proxies=self.proxies)

  def implied(self):
    for tag in self.implied_tags:
      yield Tag(None, tag=tag, slug=True, url_domain=self.url_domain, proxies=self.proxies)

  def implied_by(self):
    for tag in self.implied_by_tags:
      yield Tag(None, tag=tag, slug=True, url_domain=self.url_domain, proxies=self.proxies)