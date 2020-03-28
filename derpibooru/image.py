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

from .request import get_image_data, get_image_faves, request as request_image
from .comments import Comments
from .tags import Tags

__all__ = [
  "Image"
]

class Image(object):
  """
  This class provides a thin wrapper around JSON data, mapping each value to
  its own property. Once instantiated the data is immutable so as to reflect
  the stateless nature of a REST API.
  For getting image by id field data should be None and image_id contains id.
  For getting current featured image field data should be None and image_id="featured"
  API key need for checking my:***
  """
  def __init__(self, data, image_id=None, key="", search_params={}, proxies={}):
    self.proxies = proxies
    # key needed for checking my:***
    if key:
      self.key = key if key else search_params['key']
    elif 'key' in search_params:
      self.key = search_params['key']
    else:
      self.key = ""
    self._params = search_params

    # Set image_id="featured" for get current featured image
    if data is None and image_id:
      self._data = data = get_image_data(image_id, proxies=proxies)
    else:
      self._data = data

    for field, body in data.items():
      if not hasattr(self, field):
        setattr(self, field, body) 

  def __str__(self):
    return f"Image({self.id})"

  @property
  def tags(self):
    return self.data["tags"]

  @property
  def representations(self):
    sizes = self.data["representations"].items()
    images = { image: url for image, url in sizes }

    return images

  @property
  def full(self):
    return self.representations["full"]

  @property
  def large(self):
    return self.representations["large"]

  @property
  def medium(self):
    return self.representations["medium"]

  @property
  def small(self):
    return self.representations["small"]

  @property
  def tall(self):
    return self.representations["tall"]

  @property
  def thumb(self):
    return self.representations["thumb"]

  @property
  def thumb_small(self):
    return self.representations["thumb_small"]

  @property
  def thumb_tiny(self):
    return self.representations["thumb_tiny"]

  @property
  def image(self):
    return self.data["view_url"]

  @property
  def faved_by(self):
    faved_by = "favourited_by_users"

    if not faved_by in self.data:
      if self.faves > 0:
        self._data[faved_by] = get_image_faves(self.id, proxies=self.proxies)
      else:
        self._data[faved_by] = []

    return self._data[faved_by]

  def comments(self):
    # filter_id used to get comments for any image
    return Comments(filter_id=56027, proxies=self.proxies).image_id(self.id)
       
  @property
  def url(self):
    return f"https://derpibooru.org/images/{self.id}"

  @property
  def data(self):
    return self._data

  def update(self):
    data = get_image_data(self.id, proxies=self.proxies)

    if data:
      self._data = data

  @property
  def artists(self):
    self_tag_list = '(' + '||'.join(f"name:{tag}" for tag in self.tags) + ')'
    art_tag_list = '(category:origin||name:artist needed||name:anonymous artist||name:kotobukiya)'
    tags = Tags(q=(self_tag_list,art_tag_list,), per_page=50, 
                limit=len(self_tag_list), proxies=self.proxies)
    for tag in tags:
      yield tag.name_in_namespace

  @property
  def rating(self):
    #all_ratings = {tag.name for tag in Tags(q={"category:rating"}, proxies=self.proxies)}
    all_ratings = {"safe","suggestive","questionable","explicit",
                   "semi-grimdark","grimdark","grotesque"}
    rating_tags = list(set(self.tags).intersection(all_ratings))
    return rating_tags

  @property
  def species(self):
    self_tag_list = '(' + '||'.join(f"name:{tag}" for tag in self.tags) + ')'
    sp_tag_list = '(category:species||name:humanized||name:anthro centaur||name:bat alicorn)'
    tags = Tags(q=(self_tag_list,sp_tag_list,), per_page=50, 
                limit=len(self_tag_list), proxies=self.proxies)
    for tag in tags:
      yield tag.name_in_namespace

  @property
  def characters(self):
    self_tag_list = '(' + '||'.join(f"name:{tag}" for tag in self.tags) + ')'
    ch_tag_list = '(category:character||category:oc)'
    tags = Tags(q=(self_tag_list,ch_tag_list,"-name:oc","-name:oc only"),
                per_page=50, limit=len(self_tag_list), proxies=self.proxies)
    for tag in tags:
      yield tag.name_in_namespace

  @property
  def spoiler(self):
    spoiler_tags = []
    self_tag_list = '(' + '||'.join(f"name:{tag}" for tag in self.tags) + ')'
    sp_tag_list = '(category:spoiler||category:content-official)'
    tags = Tags(q=(self_tag_list,sp_tag_list,), per_page=50,
                limit=len(self_tag_list), proxies=self.proxies)
    aliases = []
    for tag in tags:
      if tag.category == "spoiler" and tag.name != "leak":
        spoiler_tags.append(tag.name_in_namespace)
      elif tag.category == "content-official" and tag.aliases:
        aliases.extend(tag.aliases)
      elif tag.category == "content-official":
        spoiler_tags.append(tag.name_in_namespace)
    aliases = '||'.join(f"slug:{tag}" for tag in set(aliases))
    tags = Tags(q=(aliases,), per_page=50, limit=len(self_tag_list), proxies=self.proxies)
    for tag in tags:
      if tag.category == "spoiler" and tag.name != "leak":
        spoiler_tags.append(tag.name_in_namespace)
    for tag in sorted(set(spoiler_tags)):
      yield tag

  @property
  def source(self):
    if self.data['source_url']:
      return self.data['source_url']
    else:
      return self.url
  
  @property
  def upvoted(self):
    """
    Checking image in my:upvotes.
    """
    images = request_image({'key': self.key, 'filter_id': 56027, 'per_page': 1,
                            'q': (f'id:{self.id}','my:upvotes')}, proxies=self.proxies)
    for img in images:
      return True
    return False
  
  @property
  def downvoted(self):
    """
    Checking image in my:downvotes.
    """
    images = request_image({'key': self.key, 'filter_id': 56027, 'per_page': 1,
                            'q': (f'id:{self.id}','my:downvotes')}, proxies=self.proxies)
    for img in images:
      return True
    return False
  
  @property
  def uploaded(self):
    """
    Checking image in my:uploads.
    """
    images = request_image({'key': self.key, 'filter_id': 56027, 'per_page': 1,
                            'q': (f'id:{self.id}','my:uploads')}, proxies=self.proxies)
    for img in images:
      return True
    return False
  
  @property
  def faved(self):
    """
    Checking image in my:faves.
    """
    images = request_image({'key': self.key, 'filter_id': 56027, 'per_page': 1,
                            'q': (f'id:{self.id}','my:faves')}, proxies=self.proxies)
    for img in images:
      return True
    return False
  
  @property
  def watched(self):
    """
    Checking image in my:watches.
    """
    images = request_image({'key': self.key, 'filter_id': 56027, 'per_page': 1,
                            'q': (f'id:{self.id}','my:faves')}, proxies=self.proxies)
    for img in images:
      return True
    return False
  
  def next(self):
    """
    Get next Image in Search().
    """
    parameters = {**self._params, 'per_page': 1, 'sf': 'created_at'}
    parameters['q'].add(f'id.lt:{self.id}')
    data = request_image(parameters, proxies=self.proxies)
    try:
      return Image(next(data),
                   search_params={**self._params,
                                  'key': self.key if self.key else self._params['key']},
                   proxies=self.proxies)
    except StopIteration:
      return self
  
  def prev(self):
    """
    Get previous Image in Search().
    """
    parameters = {**self._params, 'per_page': 1, 'sf': 'created_at'}
    parameters['q'].add(f'id.gt:{self.id}')
    parameters['sd'] = 'desc' if self._params['sd']=='asc' else 'asc'
    data = request_image(parameters, proxies=self.proxies)
    try:
      return Image(next(data),
                   search_params={**self._params,
                                  'key': self.key if self.key else self._params['key']},
                   proxies=self.proxies)
    except StopIteration:
      return self
