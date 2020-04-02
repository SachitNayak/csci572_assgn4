import json
from copy import deepcopy
from urllib.parse import urlencode, quote_plus
from urllib.request import *

from django.shortcuts import render

from . import utils

HOME_DIR = "/home/de11bu23n58k/"
SOLR_PATH = HOME_DIR + "solr-7.7.2/"
START_CMD = SOLR_PATH + "bin/solr start"
URL_HTML_CSV_MAP_PATH = SOLR_PATH + 'LATIMES/URLtoHTML_latimes_news.csv'
DELAY = 3
NORMAL_CORE_NAME = 'latimes_core'
PAGE_RANK_CORE_NAME = 'page_rank_core'
URL_HTML_HASH_MAP = dict()


def index(request):
    global URL_HTML_HASH_MAP
    URL_HTML_HASH_MAP = utils.activate_auxiliary_routines(cmd=START_CMD, file_path=URL_HTML_CSV_MAP_PATH)
    return render(request, 'search/index.html')


def process(request):
    global URL_HTML_HASH_MAP, NORMAL_CORE_NAME, PAGE_RANK_CORE_NAME
    user_query = request.GET.get('search_box')
    user_query = user_query.replace('"', '').replace('"', '')
    search_method = request.GET.get('search_switch')
    original_case_user_query = deepcopy(user_query)
    user_query = user_query.strip().lower()
    print("query was: ", user_query)
    if search_method == "ns":
        core_name = NORMAL_CORE_NAME
    else:
        core_name = PAGE_RANK_CORE_NAME
    base_solr_url = 'http://localhost:8983/solr/' + core_name + '/select?'
    get_params = dict()
    get_params['q'] = '\"' + user_query + '\"'
    get_params['wt'] = 'json'
    get_params['indent'] = 'on'
    get_params['fl'] = 'id, title, description'
    get_params['rows'] = 10
    if search_method == 'prs':
        get_params['sort'] = 'pageRankFile desc'
    payload = urlencode(get_params, quote_via=quote_plus)
    connection = urlopen(base_solr_url + payload)
    response = json.load(connection)
    num_docs = response['response']['numFound']
    doc_encoded_id_list_of_dicts = response['response']['docs']
    res_row_count = len(doc_encoded_id_list_of_dicts)
    search_result_links = list()
    for item in doc_encoded_id_list_of_dicts:
        link_doc_id = item['id']
        link_val = URL_HTML_HASH_MAP[item['id'].split('/')[-1]]
        link_desc = ' '.join(item['description']) if 'description' in item.keys() else "No description was found."
        link_item = utils.LinkItem(link_doc_id, item['title'][0], link_val, link_desc)
        search_result_links.append(link_item)
    print(num_docs, "documents found.")
    context = dict(user_query=original_case_user_query, num_docs=num_docs, links=search_result_links,
                   num_rows=res_row_count)
    return render(request, 'search/results.html', context)
