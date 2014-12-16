from flask import url_for
from werkzeug.routing import BuildError
from flask.ext.restful import reqparse


available_endpoints = {}


def new_endpoint(endpoint, function):
    available_endpoints[endpoint] = function


def build_url_other(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except BuildError:
        pass


def add_link_or_expand(dict_json, rel, endpoint, expand=True, **kwargs):
    url = build_url_other(endpoint, **kwargs)
    dict_json['_links'][rel] = {'href': url}
    if expand:
        parser = reqparse.RequestParser()
        parser.add_argument('expand', type=str, required=False, location='args', action='append')
        args = parser.parse_args()
        if args['expand'] is None or rel not in args['expand']:
            dict_json[rel] = url
        else:
            try:
                res_expand = available_endpoints[endpoint](**kwargs)
                dict_json[rel] = res_expand
            except Exception as e:
                dict_json[rel] = url
