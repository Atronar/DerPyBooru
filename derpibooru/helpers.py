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

from urllib.parse import quote_plus

__all__ = [
  "tags",
  "search_comments_fields",
  "api_key",
  "validate_filter",
  "validate_url",
  "validate_description",
  "sort_format",
  "user_option",
  "format_params",
  "join_params",
  "set_limit",
  "set_distance",
  "slugging_tag",
  "destructive_slug"
]

from .sort import sort
from .user import user

def tags(q):
  if isinstance(q, str):
    q = q.split(',')
  tags = {str(tag).strip() for tag in q if tag}

  return tags if tags else set()

def search_comments_fields(q, author="", body="", created_at="", comment_id="", \
                           image_id="", my=None, user_id=""):
  if ',' in q:
    q = q.split(',')

  if isinstance(body,str):
     if body:
       tags = body.split(',');
     else:
       tags = []
  elif hasattr(body,"__iter__"): # iterable: lists, sets, etc.
    tags = list(body)
  else:
    tags = []

  for tag in q:
    if tag:
      tag = str(tag).strip()
      if tag.startswith("author:"):
        if not author:
          author = tag.replace("author:","",1)
      elif tag.startswith("created_at:"):
        if not created_at:
          created_at = tag.replace("created_at:","",1)
      elif tag.startswith("comment_id:"):
        if not comment_id:
          comment_id = tag.replace("comment_id:","",1)
      elif tag.startswith("image_id:"):
        if not image_id:
          image_id = tag.replace("image_id:","",1)
      elif tag.startswith("user_id:"):
        if not user_id:
          user_id = tag.replace("user_id:","",1)
      elif tag.startswith("-my:"): # -my:comments
        if my is None: 
          if tag == "-my:comments":
            my = False
      elif tag.startswith("my:"): # my:comments
        if not my: 
          if tag == "my:comments":
            my = True
      else:
        tags.append(tag)

  if author:
    tags.append(f"author:{author}")
  if created_at:
    tags.append(f"created_at:{created_at}")
  if comment_id:
    tags.append(f"id:{comment_id}")
  if image_id:
    tags.append(f"image_id:{image_id}")
  if user_id:
    tags.append(f"user_id:{user_id}")
  if my is not None:
    if my:
      tags.append("my:comments")
    else:
      tags.append("-my:comments")

  tags = set(tags)

  return tags if tags else set()

def api_key(api_key):
  return str(api_key) if api_key else ""

def validate_filter(filter_id):
  # is it always an number?
  return str(filter_id) if filter_id else None

def validate_url(url):
  if url:
    norm_url = str(url).strip().strip('/')
    if any(norm_url.startswith(scheme) for scheme in {"http://", "https://"}):
      return norm_url
    elif "://" in norm_url:
      return ""
    else:
      return f"http://{norm_url}"
  else:
    return ""

def validate_description(string):
  if len(string.encode('utf-8'))<50000:
    return string
  else:
    n=50000
    while True:
      try:
        cutted_string = string.encode('utf-8')[:n].decode('utf-8')
        return cutted_string
      except UnicodeDecodeError:
        n -= 1

def sort_format(sf):
  if sf not in sort.methods and not sf.startswith("gallery_id:"):
    raise AttributeError(sf)
  else:
    return sf

def user_option(option):
  if option: 
    if option not in user.options:
      raise AttributeError(option)
    else:
      return option
  else:
    return ""

def format_params(params):
  p = {}

  for key, value in params.items():
    if key == "q":
      p["q"] = ",".join(value) if value else "*"
    elif key == "reverse_url" and value:
      p["url"] = value
    elif key == "distance":
      if "reverse_url" in params and params["reverse_url"]:
        p[key] = value
    elif value:
      p[key] = value

  return p

def format_params_url_galleries(params):
  p = {}

  for key, value in params.items():
    if key == "q":
      q = ",".join(value) if value else "*"
      q = (i.strip() for i in q.split(","))
      for tag in q:
        if tag.startwith("title:"):
          p["gallery[title]"] = tag[6:]
        elif tag.startwith("description:"):
          p["gallery[description]"] = tag[12:]
        elif tag.startwith("user:"):
          p["gallery[creator]"] = tag[5:]
        elif tag.startwith("image_ids:"):
          p["gallery[include_image]"] = tag[10:]
    elif value:
      p[key] = value

  return p

def join_params(old_params, new_params):
  new_dict = {**old_params, **new_params}

  return new_dict

def set_limit(limit):

  if limit is not None:
    l = int(limit)
  else:
    l = None

  return l

def set_distance(distance):
  if distance:
    try:
      d = float(distance)
      if d < 0.2:
        d = 0.2
      elif d >= 1:
        d = 0.5
    except:
      d = 0.25
  else:
    d = 0.25
  return d

def slugging_tag(tag):
  slug = tag.strip().lower()
  do_slug = False
  for char in slug:
    if char in '/\\:.+ ':
      do_slug = True
      break
  if not do_slug and '-' in slug:
    for char in ('-dash-','-fwslash','-bwslash-','-colon-','-dot-','-plus-','stop'):
      if char in slug and char != 'stop':
        break
      elif char == 'stop':
        do_slug = True
  if do_slug:
    for i,j in {'-':'-dash-', '/':'-fwslash', '\\':'-bwslash-',
                ':':'-colon-', '.':'-dot-', '+':'-plus-'}.items():
      slug = slug.replace(i,j)
    slug = quote_plus(slug)
  return slug

def destructive_slug(string):
  output = string
  for char in string:
    if ord(char) not in range(ord(" "),ord("~")) or char=="'":
      output = output.replace(char,"")
    elif ord(char) not in range(ord("a"),ord("z")) \
     and ord(char) not in range(ord("A"),ord("Z")) \
     and ord(char) not in range(ord("0"),ord("9")):
      output = output.replace(char,"-")
  while "--" in output:
    output = output.replace("--","-")
  output = output.strip("-").lower()
  return output

def url_abs(url_domain,url):
  if url.startswith('//'):
    return f"https:{url}"
  if url.startswith('/'):
    return f"{url_domain}{url}"
  else:
    return url