[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Ftimuralp%2Fswift-jpeg-meta.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Ftimuralp%2Fswift-jpeg-meta?ref=badge_shield)

OpenStack Swift middleware to extract JPEG EXIF metadata
========================================================

The middleware extracts all of the EXIF metadata while the image is being
written to the object store. After a successful write, the middleware submits an
additional request (POST), which applies the metadata to the object.

The extraction is done by the
[exif-stream](https://github.com/timuralp/exif-stream) library (a streaming JPEG
EXIF parser).

How do I set this up?
---------------------

The middleware can be installed in a fashion similar to all other OpenStack
Swift middleware. Specifically, you need to install the python package on the
proxy node and add it to the pipeline.

Until a version of this middleware is published on PyPI (or elsewhere), the best
bet is to build it from source:
```
<virtualenv>/bin/python setup.py sdist
```

This will create a source tarball in `dist`.

Upload the tarball to the server and install with:
```
pip install jpeg_extract-0.0.1.tar.gz
```

**NOTE**: on some distributions the installed middleware may not be readable in
the installed directory (e.g. `/usr/local/lib/python<version>/dist-packages`)
and you'll need to make sure it is world-readable.

After this, add the middleware to your Swift pipeline in the proxy file. The
filter entry does not require any parameters. For example, the entry may look
like this:

```
[pipeline]
pipeline = jpeg_extract proxy-server

[filter:jpeg_extract]
use = egg:jpeg_extract#jpeg_extract
```

After restarting the proxy-server you can test the middleware by uploading any
.jpg file and then checking whether the metadata was successfully extracted and
applied (by making a HEAD request).


Elasticsearch mapping
---------------------

If you plan to ingest the metadata into Elasticsearch, a mapping is required for
the EXIF types. By default, Elasticsearch will index all fields as strings.
Below is an example mapping to apply to the index that would allow search by
proper types, e.g. by integer for image width or height.

```
{
    "properties": {
        "exif-image-height":            {"type": "integer"},
        "exif-image-width":             {"type": "integer"},
        "exposure-bias-value":          {"type": "float"},
        "exposure-mode":                {"type": "integer"},
        "exposure-program":             {"type": "integer"},
        "exposure-time":                {"type": "string",
                                         "index": "not_analyzed"},
        "f-number":                     {"type": "string",
                                         "index": "not_analyzed"},
        "flash":                        {"type": "integer"},
        "flashpix-version":             {"type": "string"},
        "focal-length":                 {"type": "string",
                                         "index": "not_analyzed"},
        "focal-length-in-35mm-film":    {"type": "integer"},
        "gps-altitude":                 {"type": "string",
                                         "index": "not_analyzed"},
        "gps-altitude-reference":       {"type": "string",
                                         "index": "not_analyzed"},
        "gps-date":                     {"type": "string",
                                         "index": "not_analyzed"},
        "gps-latitude":                 {"type": "float"},
        "gps-latitude-reference":       {"type": "string"},
        "gps-longitude":                {"type": "float"},
        "gps-longitude-reference":      {"type": "string"},
        "gps-time-stamp":               {"type": "string",
                                         "index": "not_analyzed"},
        "gps-version-id":               {"type": "string"},
        "image-digitized-date/time":    {"type": "date"},
        "image-id":                     {"type": "string"},
        "image-taken-date/time":        {"type": "date"},
        "isospeedratings":              {"type": "integer"},
        "make":                         {"type": "string",
                                         "index": "not_analyzed"},
        "metering-mode":                {"type": "integer"},
        "model":                        {"type": "string"},
        "resolution-unit":              {"type": "integer"},
        "scene-capture-type":           {"type": "integer"},
        "scene-type":                   {"type": "string"},
        "sensing-mode":                 {"type": "integer"},
        "shutter-speed":                {"type": "string",
                                         "index": "not_analyzed"},
        "software":                     {"type": "string"},
        "white-balance":                {"type": "integer"},
        "xresolution":                  {"type": "integer"},
        "ycbcrpositioning":             {"type": "integer"},
        "yresolution":                  {"type": "integer"}
    }
}
```

Note that for some fields, we do not currently do the proper conversion. For
example, the `exposure-time` is given as a string "1/5531", for example. In the
future, this could be represented as a float to allow for searching by exposure
time, but currently it is a string.

The GPS coordinates could also make use of the Elasticsearch Geo Point type,
however, currently the extracted metadata is only specified as the separate
coordinates.


## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Ftimuralp%2Fswift-jpeg-meta.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Ftimuralp%2Fswift-jpeg-meta?ref=badge_large)