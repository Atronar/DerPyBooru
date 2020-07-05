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

from .request import get_comment_data, url_domain

__all__ = [
  "Comment"
]

class Comment(object):
  def __init__(self, data, comment_id=None, proxies={}):
    self.proxies = proxies
    if data is None and comment_id:
      self._data = data = get_comment_data(comment_id, proxies=proxies)
    else:
      self._data = data
    for field, body in self.data.items():
      if not hasattr(self, field):
        setattr(self, field, body)

  def __str__(self):
    if self.author:
      return '''Comment({}: "{}")'''.format(self.id,
                                            self.body.replace('\r','').strip().split('\n',1)[0][:27]+'...' \
                                              if len(self.body.replace('\r',''))>30 \
                                              else self.body.replace('\r','').strip().split('\n',1)[0]
                                           )
    else:
      return f'''Deleted comment({self.id} in image {self.image_id})'''

  @property
  def data(self):
    return self._data
       
  @property
  def url(self):
    return f"{url_domain}/images/{self.image_id}#comment_{self.id}"

  def update(self):
    data = get_comment_data(self.id, proxies=self.proxies)

    if data:
      self._data = data

