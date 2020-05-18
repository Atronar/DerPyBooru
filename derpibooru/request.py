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
from .helpers import format_params, format_params_url_galleries, slugging_tag

__all__ = [
  "url", "request", "get_images", "get_image_data", "get_image_faves",
  "url_related", "request_related", "get_related",
  "url_comments", "request_comments", "get_comments", "get_comment_data",
  "url_tags", "request_tags", "get_tags", "get_tag_data",
  "get_user_id_by_name", "get_user_data",
  "request_filters",
  "get_filters", "get_filter_data",
  "url_galleries", "request_galleries", "get_galleries",
  "request_forums", "get_forums", "get_forum_data",
  "url_topics", "request_topics", "get_topics", "get_topic_data",
  "url_search_posts",
  "url_posts", "request_posts", "get_posts", "get_post_data"
]

def request_content(search, p, items_name, post_request=False, proxies={}):
  if post_request:
    request = post(search, params=p, proxies=proxies)
  else:
    request = get(search, params=p, proxies=proxies)
  if "per_page" not in p:
    p["per_page"] = 50
  while request.status_code == codes.ok:
    items, item_count = request.json()[items_name], 0
    for item in items:
      yield item
      item_count += 1
    if item_count < p["per_page"]:
      break
    p["page"] += 1
    request = get(search, params=p, proxies=proxies)

def get_content(request_func, *request_args, limit=50, **request_kwargs):
  if limit is not None:
    if limit > 0:
      r = request_func(*request_args, **request_kwargs)
      for index, content_item in enumerate(r, start=1):
        yield content_item
        if index >= limit:
          break
  else:
    r = request_func(*request_args, **request_kwargs)
    for content_item in r:
      yield content_item

def url(params):
  p = format_params(params)
  url = f"https://derpibooru.org/search?{urlencode(p)}"
  return url

def request(params, proxies={}):
  if "reverse_url" in params and params["reverse_url"]:
    search, p = "https://derpibooru.org/api/v1/json/search/reverse", format_params(params)
    p = {i:p[i] for i in p if i in ('url','distance')}
    post_request = True
  else:
    search, p = "https://derpibooru.org/api/v1/json/search/images", format_params(params)
    p = {i:p[i] for i in p if i not in ('url','distance')}
    post_request = False
  for image in request_content(search, p, "images", post_request=post_request, proxies=proxies):
    yield image

def get_images(params, limit=50, proxies={}):
  for image in get_content(request, params, limit=limit, proxies=proxies):
    yield image

def get_image_data(id_number, proxies={}):
  '''id_number can be "featured"'''
  url = f"https://derpibooru.org/api/v1/json/images/{id_number}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    if data["image"]["duplicate_of"]:
      return get_image_data(data["image"]["duplicate_of"], proxies=proxies)
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

  for image in request_content(search, p, "images", proxies=proxies):
    yield image

def get_related(id_number, params, limit=50, proxies={}):
  for image in get_content(request_related, id_number, params,
                           limit=limit, proxies=proxies):
    yield image

def url_comments(params):
  p = format_params(params)
  p["qc"]=p["q"]
  del(p["q"])
  url = f"https://derpibooru.org/comments?{urlencode(p)}"
  return url

def request_comments(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/comments", format_params(params)
  for comment in request_content(search, p, "comments", proxies=proxies):
    yield comment

def get_comments(params, limit=50, proxies={}):
  for comment in get_content(request_comments, params,
                             limit=limit, proxies=proxies):
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

def request_tags(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/tags", format_params(params)
  for tag in request_content(search, p, "tags", proxies=proxies):
    yield tag

def get_tags(params, limit=50, proxies={}):
  for tag in get_content(request_tags, params, limit=limit, proxies=proxies):
    yield tag

def get_tag_data(tag, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/tags/{tag}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()

    return data["tag"]

def get_user_id_by_name(username, proxies={}):
  url = f"https://derpibooru.org/profiles/{slugging_tag(username)}"

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

def request_filters(filter_id, params, proxies={}):
  '''filter_id can be "system"'''
  search, p = f"https://derpibooru.org/api/v1/json/filters/{filter_id}", format_params(params)
  for filter_item in request_content(search, p, "filters", proxies=proxies):
    yield filter_item

def get_filters(filter_id, params, limit=50, proxies={}):
  for filter_item in get_content(request_filters, filter_id, params,
                                 limit=limit, proxies=proxies):
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

def request_galleries(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/search/galleries", format_params(params)
  for gallery in request_content(search, p, "galleries", proxies=proxies):
    yield gallery

def get_galleries(params, limit=50, proxies={}):
  for gallery in get_content(request_galleries, params, limit=limit, proxies=proxies):
    yield gallery

def request_forums(params, proxies={}):
  search, p = "https://derpibooru.org/api/v1/json/forums", format_params(params)
  for forum in request_content(search, p, "forums", proxies=proxies):
    yield forum

def get_forums(params, limit=50, proxies={}):
  for forum in get_content(request_forums, params, limit=limit, proxies=proxies):
    yield forum

def get_forum_data(short_name, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/forums/{short_name}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()
    return data["forum"]

def url_topics(forum_short_name, params):
  p = format_params(params)
  url = f"https://derpibooru.org/forums/{forum_short_name}?{urlencode(p)}"
  return url

def request_topics(forum_short_name, params, proxies={}):
  search, p = f"https://derpibooru.org/api/v1/json/forums/{forum_short_name}/topics", format_params(params)
  for topic in request_content(search, p, "topics", proxies=proxies):
    yield topic

def get_topics(forum_short_name, params, limit=50, proxies={}):
  for topic in get_content(request_topics, forum_short_name, params,
                           limit=limit, proxies=proxies):
    yield topic

def get_topic_data(forum_short_name, topic_slug, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/forums/{forum_short_name}/topics/{topic_slug}"

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

def request_posts(params, forum_short_name="", topic_slug="", proxies={}):
  if forum_short_name and topic_slug:
    search, p = f"https://derpibooru.org/api/v1/json/forums/{forum_short_name}/topics/{topic_slug}/posts", format_params(params)
  else:
    search, p = "https://derpibooru.org/api/v1/json/search/posts", format_params(params)
  for post in request_content(search, p, "posts", proxies=proxies):
    yield post

def get_posts(params, forum_short_name="", topic_slug="", limit=50, proxies={}):
  for post in get_content(request_posts, params,
                          limit=limit, forum_short_name=forum_short_name,
                          topic_slug=topic_slug, proxies=proxies):
    yield post

def get_post_data(id_number, proxies={}):
  url = f"https://derpibooru.org/api/v1/json/posts/{id_number}"

  request = get(url, proxies=proxies)

  if request.status_code == codes.ok:
    data = request.json()
    return data["post"]