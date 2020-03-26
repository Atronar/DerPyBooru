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

from requests import get, post, codes
from urllib.parse import urlencode
from .helpers import format_params, join_params

__all__ = [
  "url",
  "request",
  "get_images",
  "get_image_data",
  "set_limit"
]

def url(params):
  p = format_params(params)
  url = f"https://derpibooru.org/search?{urlencode(p)}"

  return url

def request(params, proxies={}):
  if "reverse_url" in params:
    search, p = "https://derpibooru.org/api/v1/json/search/reverse", format_params(params)
    p = {i:p[i] for i in p if i in ('url','distance')}
    request = post(search, params=p, proxies=proxies)
  else:
    search, p = "https://derpibooru.org/api/v1/json/search/images", format_params(params)
    p = {i:p[i] for i in p if i not in ('url','distance')}
    request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    images, image_count = request.json()["images"], 0
    for image in images:
      yield image
      image_count += 1
    if image_count < 50:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_images(params, limit=50, proxies={}):
  if limit is not None:
    l = limit
    if l > 0:
      r, counter = request(params, proxies=proxies), 0

      for index, image in enumerate(r, start=1):
        yield image
        if index >= l:
          break
  else:
    r = request(params, proxies=proxies)
    for image in r:
      yield image

def get_image_data(id_number, proxies={}):
  """id_number can be featured"""
  url = f"https://derpibooru.org/api/v1/json/images/{id_number}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    if "duplicate_of" in data:
      return get_image_data(data["duplicate_of"], proxies=proxies)
    else:
      return data["image"]

def get_image_faves(id_number, proxies={}):
  url = f"https://derpibooru.org/images/{id_number}/favorites"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.text.rsplit('</h5>',1)[-1].strip()
    if data.endswith('</a>'):
       data = data[:-4]
    data = data.split("</a> <")
    data = [useritem.rsplit('">',1)[-1] for useritem in data]
    return data

def url_related(id_number, params):
  p = format_params(params)
  url = f"https://derpibooru.org/images/{id_number}/related?{urlencode(p)}"

  return url

def request_related(id_number, params, proxies={}):
  search, p = f"https://www.derpibooru.org/images/{id_number}/related.json", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    images, image_count = request.json()["images"], 0
    for image in images:
      image['view_url'] = image['image']
      yield image
      image_count += 1
    if image_count < 50:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_related(id_number, params, limit=50, proxies={}):
  if limit is not None:
    l = limit
    if l > 0:
      r, counter = request_related(id_number, params, proxies=proxies), 0

      for index, image in enumerate(r, start=1):
        yield image
        if index >= l:
          break
  else:
    r = request_related(id_number, params, proxies=proxies)
    for image in r:
      yield image

def get_user_id_by_name(username, proxies={}):
  url = f"https://derpibooru.org/profiles/{username.replace(' ','+')}"

  request = get(url, proxies=proxies)

  profile_data = request.text
  user_id = profile_data.split("/conversations?with=",1)[-1].split('">',1)[0]
  return user_id

def url_comments(params):
  p = format_params(params)
  p["qc"]=p["q"]
  del(p["q"])
  url = f"https://derpibooru.org/comments?{urlencode(p)}"

  return url

def comments_requests(params, limit=50, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/comments", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    comments, comment_count = request.json()["comments"], 0
    for comment in comments:
      yield comment
      comment_count += 1
    if comment_count < 50:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_comments(parameters, limit=50, proxies={}):
  params = parameters

  if limit is not None:
    l = limit
    if l > 0:
      r, counter = comments_requests(params, proxies=proxies), 0

      for index, comment in enumerate(r, start=1):
        yield comment
        if index >= l:
          break
  else:
    r = comments_requests(params, proxies=proxies)
    for comment in r:
      yield comment

def get_comment_data(id_number, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/comments/{id_number}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    return data["comment"]