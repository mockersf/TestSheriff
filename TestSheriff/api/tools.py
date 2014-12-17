from flask import url_for
from werkzeug.routing import BuildError
from flask.ext.restful import reqparse


available_endpoints = {}


def new_endpoint(api, endpoint, path, rest_class, can_expand=False, function=None):
    api.add_resource(rest_class, path, endpoint=endpoint)
    if can_expand:
        available_endpoints[endpoint] = function


def build_url_other(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except BuildError:
        pass


def add_link_or_expand(dict_json, rel, endpoint, **kwargs):
    url = build_url_other(endpoint, **kwargs)
    dict_json['_links'][rel] = {'href': url}
    if rel is not 'self' and endpoint in available_endpoints:
        parser = reqparse.RequestParser()
        parser.add_argument('expand', type=str, required=False, location='args', action='append')
        args = parser.parse_args()
        expand = args['expand'] if args['expand'] is not None else []
        expand_all = []
        map(lambda i: expand_all.extend(i), [i.split(',') for i in expand])
        if rel not in expand_all:
            dict_json[rel] = url
        else:
            try:
                res_expand = available_endpoints[endpoint](**kwargs)
                dict_json[rel] = res_expand
            except Exception as e:
                dict_json[rel] = url
