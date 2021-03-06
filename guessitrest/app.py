#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, make_response
from flask_restful import Api, Resource, reqparse
from flask.ext.cors import CORS  # pylint:disable=no-name-in-module,import-error


import guessit
from guessit.jsonutils import GuessitEncoder

from . import __version__

app = Flask(__name__)
CORS(app)
api = Api(app)
app.debug = os.environ.get('GUESSIT-REST-DEBUG', False)

if not app.debug:
    handler = RotatingFileHandler('guessit-rest.log', maxBytes=5*1024*1024, backupCount=5)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=GuessitEncoder, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp


class GuessIt(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='store', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        return guessit.guessit(args.filename, args.options)

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


class GuessItVersion(Resource):
    def get(self):
        return {'guessit' : guessit.__version__, 'rest': __version__}

api.add_resource(GuessIt, '/')
api.add_resource(GuessItVersion, '/version/')


def main():  # pragma:no cover
    app.run(host='0.0.0.0')

if __name__ == '__main__':  # pragma:no cover
    main()
