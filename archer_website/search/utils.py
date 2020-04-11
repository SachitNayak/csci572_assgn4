import csv
from multiprocessing.pool import ThreadPool
from os import system
import json


class LinkItem(object):
    def __init__(self, doc_id, title, url, desc):
        self.doc_id = doc_id
        self.title = title
        self.url = url
        self.desc = desc


def create_url_hash_map(file_path):
    url_hash_map = dict()
    with open(file_path, 'r') as csv_f:
        csv_reader = csv.reader(csv_f)
        for row in csv_reader:
            url_hash_map[row[0]] = row[1]
    return url_hash_map


def start_solr_server(cmd):
    system(cmd)


def activate_auxiliary_routines(cmd, file_path):
    thread_iterations = 2
    pool = ThreadPool(processes=thread_iterations)
    async_results = list()
    tasks = [start_solr_server, create_url_hash_map]
    kws_args = [{'cmd': cmd}, {'file_path': file_path}]
    for i in range(thread_iterations):
        async_results.append(pool.apply_async(tasks[i], kwds=kws_args[i]))
    for e, result in enumerate(async_results):
        if e == 1:
            urls_dict = result.get()
            urls_dict.pop("filename")
            json_filename = "hash_map.json"
            with open(json_filename, 'w') as jf:
                json.dump(urls_dict, jf)
            return urls_dict


if __name__ == "__main__":
    HOME_DIR = "/home/de11bu23n58k/"
    SOLR_PATH = HOME_DIR + "solr-7.7.2/"
    START_CMD = SOLR_PATH + "bin/solr start"
    URL_HTML_CSV_MAP_PATH = SOLR_PATH + 'LATIMES/URLtoHTML_latimes_news.csv'
    activate_auxiliary_routines(cmd=START_CMD, file_path=URL_HTML_CSV_MAP_PATH)
