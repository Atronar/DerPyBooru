# DerPyBooruPhi

Python bindings for Philomena-based boorus' API like Ponybooru, Derpibooru, etc.

License: **Simplified BSD License**

Version: **0.10.3**

## Features

- High-level abstraction over Philomena's REST API
- Parameter chaining for ease of manipulation
- Syntactic sugar for queries, e.g., "query.score >= 100" compiling to "score.gte:100"
- Design focusing on iterables and lazy generation for network efficiency

## Dependencies

- python3.6 or newer
- requests

## How to install

### Python 3.x

    $ pip3 install derpybooruphi
 
## Checking documentation

### Python 3.x

    $ pydoc3 derpibooru

## Typical usage

### Getting images currently on Derpibooru's front page

```python
from derpibooru import Search

for image in Search():
  id_number, score, tags = image.id, image.score, ", ".join(image.tags)
  print("#{} - score: {:>3} - {}".format(id_number, score, tags))
```

### Searching posts by tag

```python
from derpibooru import Search

for image in Search().query("rarity", "twilight sparkle"):
  print(image.url)
```

### Getting images from other booru

```python
from derpibooru import Search

for image in Search(url_domain='https:\\your.booru.example').query("rarity", "twilight sparkle"):
  print(image.url)
```

### Crawling Derpibooru from first to last post

```python
from derpibooru import Search

# This is only an example and shouldn't be used in practice as it abuses
# Derpibooru's licensing terms
for image in Search().ascending().limit(None):
  id_number, score, tags = image.id, image.score, ", ".join(image.tags)
  print("#{} - score: {:>3} - {}".format(id_number, score, tags))
```

### Getting random posts

```python
from derpibooru import Search, sort

for post in Search().sort_by(sort.RANDOM):
  print(post.url)
```

### Getting top 100 posts
```python
from derpibooru import Search, sort

top_scoring = [post for post in Search().sort_by(sort.SCORE).limit(100)]
```

### Storing and passing new search parameters

```python
from derpibooru import Search, sort

params = Search().sort_by(sort.SCORE).limit(100).parameters

top_scoring = Search(**params)
top_animated = top_scoring.query("animated")
```

### Filtering by metadata

```python
from derpibooru import Search, query

q = {
  "wallpaper",
  query.width == 1920,
  query.height == 1080,
  query.score >= 100
}

wallpapers = [image for image in Search().query(*q)]
```
### Getting the latest images from a watchlist

```python

from derpibooru import Search, user

key = "your_api_key"

for post in Search().key(key).watched(user.ONLY):
  id_number, score, tags = post.id, post.score, ", ".join(post.tags)
  print("#{} - score: {:>3} - {}".format(id_number, score, tags))
```

## Changes in fork

- Only python >=3.6
- Available using proxies 
- Extended Search and Image (like paging, getting top, ratings, reverse search, etc.)
- Getting Image data by id:
```python
  i_want_ponies_ponified = Image(None,image_id=0)
  print(i_want_ponies_ponified.url)
```
- Getting comments:
```python
  for image in Search():
    for comment in image.comments:
      print(f"{comment.author}: {comment.body}")
```
  And by id:
```python
  which_video = Comment(None, id_comment=1000)
    print("Comment from",which_video.image_id)
```
- Work with tags: category, alliaces, implies, etc.
- Getting profiles
- Getting filters
- Getting galleries
- Work with forums
- Updated sort and query lists
- Posting images:
```python
  new_img = PostImage().key(API_KEY).image_url("https://pbs.twimg.com/media/EW4YtdmWAAEPaae.png:orig").description(description).tag_input("safe", "artist:dilarus", "ts", "pp").source_url("https://twitter.com/Dilarus/status/1255968549052583941")
  posted_img = new_img.post()
  id_number, score, tags = posted_img.id, posted_img.score, ", ".join(posted_img.tags)
```