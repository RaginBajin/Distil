# Copyright (C) 2014 Catalyst IT Ltd
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from decorator import decorator
import flask
import itertools
import json
from distil.models import Tenant
from distil import config


def _validate(data, *args, **kwargs):
    for key in itertools.chain(args, kwargs.keys()):
        if not key in data:
            flask.abort(400, json.dumps({'error': 'missing parameter',
                                         'param': key}))
        for key, val in kwargs.iteritems():
            flask.abort(400, json.dumps({'error': 'validation failed',
                                         'param': key}))


def must(*args, **kwargs):
    """
    Asserts that a given set of keys are present in the request parameters.
    Also allows for keyword args to handle validation.
    """
    def tester(func):
        def funky(*iargs, **ikwargs):
            _validate(flask.request.params, *args, **kwargs)
            return func(*iargs, **ikwargs)
        return decorator(funky, func)
    return tester


@decorator
def returns_json(func, *args, **kwargs):
    status, content = func(*args, **kwargs)
    response = flask.make_response(
        json.dumps(content), status)
    response.headers['Content-type'] = 'application/json'
    return response


def json_must(*args, **kwargs):
    """Implements a simple validation system to allow for the required
       keys to be detected on a given callable."""
    def unpack(func):
        def dejson(f, *iargs):
            if (flask.request.headers.get('content-type', '') !=
                    "application/json"):
                flask.abort(400, json.dumps(
                    {"error": "must be in JSON format"})
                )
            # todo -- parse_float was handled specially
            _validate(flask.request.json, *args, **kwargs)
            return func(*iargs)
        return decorator(dejson, func)
    return unpack


def validate_tenant_id(tenant_id, session):
    """Tenant ID validation that check that the id you passed is valid,
       and that a tenant with this ID exists.
       - returns tenant query, or a tuple if validation failure."""
    if isinstance(tenant_id, unicode):
        tenant_query = session.query(Tenant).\
            filter(Tenant.id == tenant_id)
        if tenant_query.count() == 0:
            return 400, {"errors": ["No tenant matching ID found."]}
    elif tenant_id is not None:
        return 400, {"error": ["tenant must be a unicode string."]}
    else:
        return 400, {"missing parameter": {"tenant": "Tenant id."}}
    return tenant_query[0]


@decorator
def require_admin(func, *args, **kwargs):
    if config.auth.get('authenticate_clients'):
        roles = flask.request.headers['X-Roles'].split(',')
        if 'admin' not in roles:
            return flask.make_response(403, "Must be admin")

    return func(*args, **kwargs)
