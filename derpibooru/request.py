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
from .helpers import format_params, format_params_url_galleries

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
  if "reverse_url" in params and params["reverse_url"]:
    search, p = "https://derpibooru.org/api/v1/json/search/reverse", format_params(params)
    p = {i:p[i] for i in p if i in ('url','distance')}
    request = post(search, params=p, proxies=proxies)
    p["per_page"] = 50
  else:
    search, p = "https://derpibooru.org/api/v1/json/search/images", format_params(params)
    p = {i:p[i] for i in p if i not in ('url','distance')}
    request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    images, image_count = request.json()["images"], 0
    for image in images:
      yield image
      image_count += 1
    if image_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_images(params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = request(params, proxies=proxies)
      for index, image in enumerate(r, start=1):
        yield image
        if index >= limit:
          break
  else:
    r = request(params, proxies=proxies)
    for image in r:
      yield image

def get_image_data(id_number, proxies={}):
  '''id_number can be "featured"'''
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
  search, p = f"https://derpibooru.org/images/{id_number}/related", format_params(params)
  request = get(search, params=p, proxies=proxies)

  # It should be temporary solution, until related returns to API
  if request.status_code == codes.ok:
    images = [f"""id:{image.split('"',1)[0]}""" for image in request.text.split('<div class="media-box" data-image-id="')][1:]
  params['q'] = (" || ".join(images),)
  params['sf'] = "_score"
  params['sd'] = "desc"
  search, p = "https://derpibooru.org/api/v1/json/search/images", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    images, image_count = request.json()["images"], 0
    for image in images:
      yield image
      image_count += 1
    if image_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_related(id_number, params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = request_related(id_number, params, proxies=proxies)
      for index, image in enumerate(r, start=1):
        yield image
        if index >= limit:
          break
  else:
    r = request_related(id_number, params, proxies=proxies)
    for image in r:
      yield image

def url_comments(params):
  p = format_params(params)
  p["qc"]=p["q"]
  del(p["q"])
  url = f"https://derpibooru.org/comments?{urlencode(p)}"

  return url

def comments_requests(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/comments", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    comments, comment_count = request.json()["comments"], 0
    for comment in comments:
      yield comment
      comment_count += 1
    if comment_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_comments(params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = comments_requests(params, proxies=proxies)
      for index, comment in enumerate(r, start=1):
        yield comment
        if index >= limit:
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

def url_tags(params):
  p = format_params(params)
  p["tq"]=p["q"]
  del(p["q"])
  url = f"https://derpibooru.org/tags?{urlencode(p)}"

  return url

def tags_requests(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/tags", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    tags, tag_count = request.json()["tags"], 0
    for tag in tags:
      yield tag
      tag_count += 1
    if tag_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_tags(params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = tags_requests(params, proxies=proxies)
      for index, tag in enumerate(r, start=1):
        yield tag
        if index >= limit:
          break
  else:
    r = tags_requests(params, proxies=proxies)
    for tag in r:
      yield tag

def get_tag_data(tag, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/tags/{tag}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    return data["tag"]

def get_user_id_by_name(username, proxies={}):
  url = f"https://derpibooru.org/profiles/{username.replace(' ','+')}"

  request = get(url, proxies=proxies)

  profile_data = request.text
  user_id = profile_data.split("/conversations?with=",1)[-1].split('">',1)[0]
  return user_id

def get_user_data(user_id, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/profiles/{user_id}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    return data["user"]

def filters_requests(filter_id, params, proxies={}):
  search, p = f"https://derpibooru.org/api/v1/json/filters/{filter_id}", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    filters, filter_count = request.json()["filters"], 0
    for filter_item in filters:
      yield filter_item
      filter_count += 1
    if filter_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_filters(filter_id, params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = filters_requests(filter_id, params, proxies=proxies)
      for index, filter_item in enumerate(r, start=1):
        yield filter_item
        if index >= limit:
          break
  else:
    r = filters_requests(filter_id, params, proxies=proxies)
    for filter_item in r:
      yield filter_item

def get_filter_data(filter_id, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/filters/{filter_id}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    return data["filter"]

def url_galleries(params):
  p = format_params_url_galleries(params)
  url = f"https://derpibooru.org/galleries?{urlencode(p)}"

  return url

def galleries_requests(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/galleries", format_params(params)
  request = get(search, params=p, proxies=proxies)
  print(format_params(params))
  while request.status_code == codes.ok:
    galleries, gallery_count = request.json()["galleries"], 0
    for gallery in galleries:
      yield gallery
      gallery_count += 1
    if gallery_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_galleries(params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = galleries_requests(params, proxies=proxies)
      for index, gallery in enumerate(r, start=1):
        yield gallery
        if index >= limit:
          break
  else:
    r = galleries_requests(params, proxies=proxies)
    for gallery in r:
      yield gallery

def forums_request(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/forums", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    forums, forum_count = request.json()["forums"], 0
    for forum in forums:
      yield forum
      forum_count += 1
    if forum_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_forums(params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = forums_request(params, proxies=proxies)
      for index, forum in enumerate(r, start=1):
        yield forum
        if index >= limit:
          break
  else:
    r = forums_request(params, proxies=proxies)
    for forum in r:
      yield forum

def get_forum_data(short_name, proxies={}):
  url = f"https://www.derpibooru.org/api/v1/json/forums/{short_name}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()
    return data["forum"]

def url_topics(forum_short_name, params):
  p = format_params(params)
  url = f"https://derpibooru.org/forums/{forum_short_name}?{urlencode(p)}"
  return url

def topics_request(forum_short_name, params, proxies={}):
  search, p = f"https://derpibooru.org/api/v1/json/forums/{forum_short_name}/topics", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    topics, topic_count = request.json()["topics"], 0
    for topic in topics:
      yield topic
      topic_count += 1
    if topic_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_topics(forum_short_name, params, limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = topics_request(forum_short_name, params, proxies=proxies)
      for index, topic in enumerate(r, start=1):
        yield topic
        if index >= limit:
          break
  else:
    r = topics_request(forum_short_name, params, proxies=proxies)
    for topic in r:
      yield topic

def get_topic_data(forum_short_name, topic_slug, proxies={}):
  url = f"https://www.derpibooru.org/api/v1/json/forums/{forum_short_name}/topics/{topic_slug}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()
    return data["topic"]

def url_search_posts(params):
  p = format_params(params)
  url = f"https://derpibooru.org/posts?{urlencode(p)}"
  return url

def url_posts(forum_short_name, topic_slug, params):
  import math
  p = format_params(params)
  api_page = p['page']
  api_per_page = p['per_page']
  web_per_page = 25
  api_last_post_on_page = api_page * api_per_page
  api_first_post_on_page = api_last_post_on_page - api_per_page + 1 
  p['page'] = math.ceil(api_first_post_on_page / 25)
  del(p['per_page'])
  url = f"https://derpibooru.org/forums/{forum_short_name}/topics/{topic_slug}?{urlencode(p)}"
  return url

def posts_request(params, forum_short_name="", topic_slug="", proxies={}):
  if forum_short_name and topic_slug:
    search, p = f"https://derpibooru.org/api/v1/json/forums/{forum_short_name}/topics/{topic_slug}/posts", format_params(params)
  else:
    search, p = "https://derpibooru.org/api/v1/json/search/posts", format_params(params)
  request = get(search, params=p, proxies=proxies)

  while request.status_code == codes.ok:
    posts, post_count = request.json()["posts"], 0
    for post in posts:
      yield post
      post_count += 1
    if post_count < p["per_page"]:
      break

    p["page"] += 1

    request = get(search, params=p, proxies=proxies)

def get_posts(params, forum_short_name="", topic_slug="", limit=50, proxies={}):
  if limit is not None:
    if limit > 0:
      r = posts_request(params, forum_short_name=forum_short_name, topic_slug=topic_slug, proxies=proxies)
      for index, post in enumerate(r, start=1):
        yield post
        if index >= limit:
          break
  else:
    r = posts_request(params, forum_short_name=forum_short_name, topic_slug=topic_slug, proxies=proxies)
    for post in r:
      yield post

def get_post_data(id_number, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/posts/{id_number}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()
    return data["post"]