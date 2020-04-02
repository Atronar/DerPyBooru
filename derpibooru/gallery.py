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

from .request import get_galleries
from .search import Search
from .image import Image

__all__ = [
  "Gallery"
]

class Gallery(object):
  """
  This class provides a thin wrapper around JSON data, mapping each value to
  its own property. Once instantiated the data is immutable so as to reflect
  the stateless nature of a REST API.
  """
  def __init__(self, data, gallery_id=None, search_params={}, proxies={}):
    self.proxies = proxies
    self._params = search_params

    if data is None and gallery_id:
      search_params['q'] = (f"id:{gallery_id}",)
      self._data = data = next(get_galleries(search_params, 1, proxies=proxies))
    else:
      self._data = data

    for field, body in data.items():
      if not hasattr(self, field):
        setattr(self, field, body) 

  def __str__(self):
    return f"Gallery({self.id})"
       
  @property
  def url(self):
    return f"https://derpibooru.org/galleries/{self.id}"

  @property
  def data(self):
    return self._data

  def update(self):
    data = next(get_galleries(self._params, 1, proxies=self.proxies))

    if data:
      self._data = data

  @property
  def thumbnail(self):
    return Image(None, image_id=self.thumbnail_id, search_params=self._params, proxies=self.proxies)
  
  def images(self, sf="created_at", sd="desc", limit=50, faves="", upvotes="", uploads="",
             watched="", filter_id="", per_page=25, page=1):
    return Search(key=self._params["key"] if "key" in self._params else "", 
                  q=(f"gallery_id:{self.id}",), sf=sf, sd=sd, limit=limit,
                  faves=faves, upvotes=upvotes, uploads=uploads, watched=watched,
                  filter_id=filter_id, per_page=per_page, page=page,
                  proxies=self.proxies)