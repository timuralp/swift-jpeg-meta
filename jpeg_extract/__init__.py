import exifstream
import exifstream.stream

from swift.common.constraints import MAX_META_VALUE_LENGTH
from swift.common.http import is_success
from swift.common.utils import split_path, get_logger
from swift.common.wsgi import WSGIContext, make_pre_authed_request

class MetaExtractor(object):
    INIT_HEADER_SIZE = 12

    def __init__(self, stream):
        self.stream = stream
        self.exif_parser = exifstream.stream.StreamProcessor()

    def read(self, size=None):
        try:
            data = self.stream.read(size)
            self.exif_parser.process(data)
        except Exception as e:
            print 'Caught an exception: ', e
        return data


class JPEGExtractMiddleware(WSGIContext):
    def __init__(self, app, conf):
        self.app = app
        self.logger = get_logger(conf, log_route='jpeg_extract')

    def __call__(self, env, start_response):
        if env['REQUEST_METHOD'] != 'PUT':
            return self.app(env, start_response)

        version, account, container, obj = split_path(env['PATH_INFO'], 1, 4, True)
        if not obj or not obj.endswith('.jpg'):
            return self.app(env, start_response)

        extractor = MetaExtractor(env['wsgi.input'])
        env['wsgi.input'] = extractor
        try:
            resp = self._app_call(env)
        except Exception as e:
            resp = HTTPServerError(request=req, body="error")
            return resp(env, start_response)
        start_response(self._response_status, self._response_headers,
                       self._response_exc_info)
        status = int(self._response_status.split()[0])
        if status < 200 or status > 300:
            return resp

        headers = {}
        for tag in extractor.exif_parser.tags:
            if tag.tag().startswith('Unknown'):
                continue
            if len(tag.value()) > MAX_META_VALUE_LENGTH:
                continue
            header = 'X-Object-Meta-' + tag.tag().replace(' ', '-')
            headers[header] = tag.value()

        # TODO: merge with the PUT headers
        self.logger.info(headers)
        post_req = make_pre_authed_request(env, method='POST',
                                           swift_source='JpegMeta',
                                           path=env['PATH_INFO'],
                                           headers=headers)
        post_resp = post_req.get_response(self.app)
        if not is_success(post_resp.status_int):
            self.logger.info('POST with JPEG headers failed: ' + str(post_resp.body))
        return resp


def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def jpeg_extract(app):
        return JPEGExtractMiddleware(app, conf)

    return jpeg_extract
