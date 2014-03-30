from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import request
from werkzeug.datastructures import Headers
from werkzeug.contrib.cache import SimpleCache
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key
import boto
import os
import re
import requests
import argparse
import yaml

app = Flask(__name__)
cache = SimpleCache()

def apply_rewrite_rules(input_str):
    for name, rule in config["rewrite_rules"].iteritems():
        input_str = rule["r"].sub(rule["to"], input_str)
        print "applied rule", name
        print "new url", input_str
    return input_str

def get_S3Key(url):
    S3Key = cache.get(url)
    if S3Key is None:
        S3Key = bucket.lookup("/" + url)
        try:
            size = S3Key.size
        except:
            return None
        cache.set(url, S3Key, timeout=5 * 60)
    return S3Key

@app.route('/files/<path:url>', methods=["HEAD"])
def head_file(url):
    url = apply_rewrite_rules(url)
    headers = Headers()
    S3Key = get_S3Key(url)
    try:
        size = S3Key.size
    except:
        return Response(None, 404)
    headers.add("Content-Length", size)
    return Response(headers=headers, direct_passthrough=True)

@app.route('/files/<path:url>', methods=["GET"])
def get_file(url):
    url = apply_rewrite_rules(url)
    range_header = request.headers.get('Range', None)
    headers = Headers()
    S3Key = get_S3Key(url)
    try:
        size = S3Key.size
    except:
        return Response(None, 404)

    if range_header:
        print "%s: %s (size=%d)" % (url, range_header, size)
        start_range, end_range = [int(x) for x in range_header.split("=")[1].split("-")]
        data = S3Key.get_contents_as_string(headers={'Range' : "bytes=%d-%d" % (start_range, end_range)})
        headers.add('Accept-Ranges', 'bytes')
        headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start_range, end_range, size))
        headers.add('Content-Length', end_range-start_range+1)
        return Response(data, 206, headers=headers, direct_passthrough=True)
    else:
        print "%s: all data (size=%d)" % (url, size)
        data = S3Key.get_contents_as_string()
        return Response(data, 200, headers=headers, direct_passthrough=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--config", "-c", action="store", default="config.yaml")
    args = parser.parse_args()

    # load AWS credentials and bucket
    config = yaml.load(open(args.config,'r'))
    conn = S3Connection(config["AWS_ACCESS_KEY_ID"], config["AWS_SECRET_ACCESS_KEY"])
    bucket = conn.get_bucket(config["bucket_name"])

    # Load the rewrite rules:
    for name, rule in config["rewrite_rules"].iteritems():
        config["rewrite_rules"][name]["r"] = re.compile(rule["from"])

    app.run(debug=args.debug)
