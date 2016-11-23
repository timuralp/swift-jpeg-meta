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
pip install jpeg_extract-0.0.1.linux-x86_64.tar.gz
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
