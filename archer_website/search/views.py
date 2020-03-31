from django.shortcuts import render
from urllib.request import *
from urllib.parse import urlencode, quote_plus
import json


def index(request):
    return render(request, 'search/index.html')


def process(request):
    user_query = request.GET.get('search_box')
    user_query = user_query.strip().lower()
    print("query was: ", user_query)
    base_solr_url = 'http://localhost:8983/solr/latimes_core/select?'
    get_params = dict()
    get_params['q'] = '\"'+user_query+'\"'
    get_params['wt'] = 'json'
    get_params['indent'] = 'on'
    get_params['fl'] = 'id'
    payload = urlencode(get_params, quote_via=quote_plus)
    connection = urlopen(base_solr_url+payload)
    response = json.load(connection)
    num_docs = response['response']['numFound']
    print(num_docs, "documents found.")
    context = {'user_query': user_query, 'num_docs': num_docs}
    return render(request, 'search/results.html', context)
