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

from re import sub
from .request import get_image_data
from .comment import Comment

__all__ = [
  "Image"
]

class Image(object):
  """
  This class provides a thin wrapper around JSON data, mapping each value to
  its own property. Once instantiated the data is immutable so as to reflect
  the stateless nature of a REST API
  """
  def __init__(self, data, proxy={}):
    self.proxy = proxy
    self._data = data

    for field, body in data.items():
      if not hasattr(self, field):
        setattr(self, field, body) 

  def __str__(self):
    return f"Image({self.id})"

  @property
  def tags(self):
    return self.data["tags"].split(", ")

  @property
  def representations(self):
    sizes = self.data["representations"].items()
    images = { image: f"https:{url}" for image, url in sizes }

    return images

  @property
  def thumb(self):
    return self.representations["thumb"]

  @property
  def thumb_tiny(self):
    return self.representations["thumb_tiny"]

  @property
  def small(self):
    return self.representations["small"]

  @property
  def full(self):
    return self.representations["full"]

  @property
  def tall(self):
    return self.representations["tall"]

  @property
  def large(self):
    return self.representations["large"]

  @property
  def medium(self):
    return self.representations["medium"]

  @property
  def thumb_small(self):
    return self.representations["thumb_small"]

  @property
  def image(self):
    return f'https:{self.data["image"]}'

  @property
  def faved_by(self):
    faved_by = "favourited_by_users"

    if not faved_by in self.data:
      if self.faves > 0:
        self.update()
      else:
        self._data[faved_by] = []

    return self._data[faved_by]

  @property
  def comments(self):
    if not "comments" in self.data:
      if self.comment_count > 0:
        self.update()
      else:
        self._data["comments"] = []

    return [Comment(c) for c in self.data["comments"]]
       
  @property
  def url(self):
    return f"https://derpibooru.org/{self.id}"

  @property
  def data(self):
    return self._data

  def update(self):
    data = get_image_data(self.id, proxy=proxy)

    if data:
      self._data = data

  @property
  def artists(self):
      _list = [];
      for tag in self.tags:
         if tag.startswith("artist:") or tag.startswith("editor:"):
            _list.append(tag[7:]);
         elif tag.startswith("colorist:"):
            _list.append(tag[9:]);
         elif tag in ("artist needed","anonymous artist"):
            _list.append(tag);
      return _list;

  @property
  def rating(self):
      _list = [];
      for tag in self.tags:
         if tag in ("safe","suggestive","questionable","explicit","semi-grimdark","grimdark","grotesque"):
            _list.append(tag);
      return _list;

  @property
  def species(self):
      _list = [];
      for tag in self.tags:
         if tag in ("pony","earth pony","pegasus","unicorn","alicorn","zebra","zebrasus","zebracorn","zebra alicorn","zony","bat pony","bat unicorn","bat alicorn","dragon","changeling","changeling queen","changedling","breezie","yak","hippogriff","griffon","seapony","seapony (g4)","merpony","dracony","demon pony","tatzlpony","kirin","abyssinian","semi-anthro","anthro","unguligrade anthro","plantigrade anthro","digitigrade anthro","anthro centaur","centaur","human","humanized","mermaid","hybrid","original species"):
            _list.append(tag);
      return _list;

  @property
  def source(self):
      if self.data['source_url']:
         return self.data['source_url'];
      else:
         return self.url;

  @property
  def width(self):
      return f'https:{self.data["width"]}'

  @property
  def height(self):
      return f'https:{self.data["height"]}'
