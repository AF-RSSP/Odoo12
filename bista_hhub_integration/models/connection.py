# -*- coding: utf-8 -*-

import hmac
import hashlib
import datetime
import requests


class HhubConService(object):

    # def get_product_api(self, product_url, api_key, secret_key):
    #     current_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    #     apiKey = '%s%s' %(api_key,current_utc)
    #     secretKey = '%s%s' %(secret_key,api_key)
    #     token = hmac.new(secretKey.encode('utf-8'), apiKey.encode('utf-8'), hashlib.sha256).hexdigest()
    #     bin = token.rstrip()
    #     url = product_url
    #     headers = {'content-type': 'application/json', "x-api-key": api_key,
    #                'x-date-stamp': current_utc, 'Authorization': 'HH-HMAC ' + bin}
    #     products = requests.get(url, headers=headers)
    #     return products

    def get_order_api(self, order_url, api_key, secret_key):
        current_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        apiKey = '%s%s' %(api_key,current_utc)
        secretKey = '%s%s' %(secret_key,api_key)
        token = hmac.new(secretKey.encode('utf-8'), apiKey.encode('utf-8'), hashlib.sha256).hexdigest()
        bin = token.rstrip()
        url = order_url
        headers = {'content-type': 'application/json', "x-api-key": api_key,
                   'x-date-stamp': current_utc, 'Authorization': 'HH-HMAC ' + bin}
        orders = requests.get(url, headers=headers)
        return orders

    def post_dispatch_api(self, request, dispatch_url, api_key, secret_key):
        current_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        apiKey = '%s%s' %(api_key,current_utc)
        secretKey = '%s%s' %(secret_key,api_key)
        token = hmac.new(secretKey.encode('utf-8'), apiKey.encode('utf-8'), hashlib.sha256).hexdigest()
        bin = token.rstrip()
        url = dispatch_url
        headers = {'content-type': 'application/json', "x-api-key": api_key,
                   'x-date-stamp': current_utc, 'Authorization': 'HH-HMAC ' + bin}
        dispatch = requests.post(url, headers=headers, data=request)
        return dispatch