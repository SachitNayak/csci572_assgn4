import csv
import json
from copy import deepcopy
from urllib.parse import urlencode, quote_plus
from urllib.request import *
import matplotlib.pyplot as plt

import ipdb


import numpy as np

HOME_DIR = "/home/de11bu23n58k/"
SOLR_PATH = HOME_DIR + "solr-7.7.2/"
URL_HTML_CSV_MAP_PATH = SOLR_PATH + 'LATIMES/URLtoHTML_latimes_news.csv'

FILE_TO_URL_MAP = dict()
NORMAL_CORE_URL = 'http://localhost:8983/solr/latimes_core/select?'
PAGE_RANK_CORE_URL = 'http://localhost:8983/solr/page_rank_core/select?'
query_list = (
    'Cannes', 'Congress', 'Democrats', 'Patriot Movement', 'Republicans', 'Senate', 'Olympics 2020', 'Stock', 'Virus')
NORMAL_LIST = list()
PG_LIST = list()


def create_hash_maps(file_path):
    global FILE_TO_URL_MAP
    with open(file_path, 'r') as csv_f:
        csv_reader = csv.reader(csv_f)
        for row in csv_reader:
            FILE_TO_URL_MAP[row[0]] = row[1]


def overlap_calculator():
    global NORMAL_CORE_URL, PAGE_RANK_CORE_URL, query_list, NORMAL_LIST, PG_LIST, FILE_TO_URL_MAP
    ns_get_params = dict()
    ns_get_params['wt'] = 'json'
    ns_get_params['indent'] = 'on'
    ns_get_params['fl'] = 'id'
    ns_get_params['rows'] = 10
    pg_get_params = dict()
    pg_get_params['wt'] = 'json'
    pg_get_params['indent'] = 'on'
    pg_get_params['fl'] = 'id'
    pg_get_params['rows'] = 10
    pg_get_params['sort'] = 'pageRankFile desc'
    for query in query_list:
        cur_normal_list = list()
        cur_pg_list = list()

        original_case_user_query = deepcopy(query)
        user_query = query.strip().lower()
        print("query was: ", original_case_user_query)

        ns_get_params['q'] = '\"' + user_query + '\"'
        pg_get_params['q'] = '\"' + user_query + '\"'

        ns_payload = urlencode(ns_get_params, quote_via=quote_plus)
        pg_payload = urlencode(pg_get_params, quote_via=quote_plus)
        ns_connection = urlopen(NORMAL_CORE_URL + ns_payload)
        pg_connection = urlopen(PAGE_RANK_CORE_URL + pg_payload)
        ns_response = json.load(ns_connection)
        pg_response = json.load(pg_connection)

        ns_doc_encoded_id_list_of_dicts = ns_response['response']['docs']
        pg_doc_encoded_id_list_of_dicts = pg_response['response']['docs']

        for item in ns_doc_encoded_id_list_of_dicts:
            link_doc_id = item['id'].split('/')[-1]
            link_val = FILE_TO_URL_MAP[link_doc_id]
            cur_normal_list.append(link_val)

        for item in pg_doc_encoded_id_list_of_dicts:
            link_doc_id = item['id'].split('/')[-1]
            link_val = FILE_TO_URL_MAP[link_doc_id]
            cur_pg_list.append(link_val)

        NORMAL_LIST.append(cur_normal_list)
        PG_LIST.append(cur_pg_list)


def analyze(list1, list2):
    length1 = len(list1)
    length2 = len(list2)
    overlap_count = 0
    overlap_percent = 0
    di2_list = list()
    if length2 >= 1:
        overlap_count = len(tuple(set(list1).intersection(set(list2))))
        for i in range(length1):
            for j in range(length2):
                url_1 = list1[i].replace("https://", "").replace("http://", "")
                url_2 = list2[j].replace("https://", "").replace("http://", "")
                if url_1.endswith("/"):
                    url_1 = url_1[:-1]
                if url_2.endswith("/"):
                    url_2 = url_2[:-1]
                if url_1.lower() == url_2.lower():
                    di2_list.append((i - j) ** 2)
        overlap_percent = (overlap_count / ((length1+length2)-overlap_count)) * 100
    return [overlap_count, overlap_percent, di2_list]


if __name__ == "__main__":
    create_hash_maps(URL_HTML_CSV_MAP_PATH)
    overlap_calculator()
    assert len(NORMAL_LIST) == len(query_list)
    assert len(PG_LIST) == len(query_list)

    rows = list()
    counter = 0
    averages_list = np.zeros((len(query_list), 3))
    for k in range(len(NORMAL_LIST)):
        counter += 1
        semi_result = analyze(NORMAL_LIST[k], PG_LIST[k])
        di2_sum = sum(semi_result[2])
        overlap_c = semi_result[0]
        denom = (overlap_c * (overlap_c ** 2 - 1))
        right_term = 0
        try:
            right_term = (6 * di2_sum) / denom
            spearman_coeff = 1 - right_term
        except ZeroDivisionError as ze:
            # see piazza @10 for explanation.
            if overlap_c == 1 and semi_result[2][0] == 0:
                # case where n=1 (exactly one overlap) and google_rank == ask_rank
                spearman_coeff = 1
            else:
                # case when n=0 (zero overlaps) OR ( n=1 (exactly 1 overlap) and google_rank != ask_rank )
                spearman_coeff = 0

        row = [query_list[k], semi_result[0], semi_result[1], spearman_coeff]
        averages_list[counter - 1][0] = semi_result[0]
        averages_list[counter - 1][1] = semi_result[1]
        averages_list[counter - 1][2] = spearman_coeff
        rows.append(row)

    average = np.average(averages_list, axis=0)
    average_row = ['Averages', average[0], average[1], average[2]]

    for r in rows:
        print(r)
    print(average_row)

    # plot overlap graph
    fig = plt.figure()
    x_values = query_list
    ov_counts = [r[1] for r in rows]
    y_pos = np.arange(len(query_list))
    # Create bars
    plt.bar(y_pos, ov_counts)
    # Create names on the x-axis
    plt.xticks(y_pos, x_values)
    plt.title('OVERLAP GRAPH')
    plt.xlabel('QUERIES')
    plt.ylabel('OVERLAP COUNT')

    # Show graphic
    plt.show()

    # # generate table
    # q_col = list()
    # for k in range(len(query_list)):
    #     spaces_list = [' ']*len(NORMAL_LIST[k])
    #     temp_list = [query_list[k]] + spaces_list
    #     q_col.extend(temp_list)
    #     spaces_list.clear()
    #     temp_list.clear()
    #
    # nl_col = list()
    # pg_col = list()
    # for k in range(len(query_list)):
    #     NORMAL_LIST[k].append(' ')
    #     PG_LIST[k].append(' ')
    #     nl_col.extend(NORMAL_LIST[k])
    #     pg_col.extend(PG_LIST[k])
    #
    # assert len(q_col) == len(nl_col)
    # assert len(q_col) == len(pg_col)
    #
    # header_row = ["Query", "Normal Lucene Search Results", "PageRank Search Results"]
    # csv_rows = zip(q_col, nl_col, pg_col)
    # with open('tables.csv', 'w') as csv_f:
    #     csv_writer = csv.writer(csv_f)
    #     csv_writer.writerow(header_row)
    #     csv_writer.writerows(csv_rows)
print("Done.")
