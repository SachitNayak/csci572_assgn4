import csv
from bs4 import BeautifulSoup
from os import listdir
import ipdb
import networkx as nx

HOME_DIR = "/home/de11bu23n58k/"
SOLR_PATH = HOME_DIR + "solr-7.7.2/"
START_CMD = SOLR_PATH + "bin/solr start"
URL_HTML_CSV_MAP_PATH = SOLR_PATH + 'LATIMES/URLtoHTML_latimes_news.csv'
DATA_DIR = SOLR_PATH+'latimes_data/'
ADJ_LIST_FILENAME = SOLR_PATH + 'graph_sp.adjlist'
PAGE_RANK_OUTPUT = SOLR_PATH + 'external_pageRankFile.txt'

FILE_TO_URL_MAP = dict()
URL_TO_FILE_MAP = dict()
ALL_LINKS = set()
ALL_ADJ_ROWS = list()


def create_hash_maps(file_path):
    global FILE_TO_URL_MAP, URL_TO_FILE_MAP, ALL_LINKS
    with open(file_path, 'r') as csv_f:
        csv_reader = csv.reader(csv_f)
        for row in csv_reader:
            FILE_TO_URL_MAP[row[0]] = row[1]
            URL_TO_FILE_MAP[row[1]] = row[0]
    ALL_LINKS = set(URL_TO_FILE_MAP.keys())


def extract_urls(dir_path):
    global FILE_TO_URL_MAP, URL_TO_FILE_MAP, ALL_LINKS, ALL_ADJ_ROWS
    for filename in listdir(dir_path):
        current_file_adj_list = list()
        full_filename = DATA_DIR+filename
        with open(full_filename, 'r') as f:
            # print("current file: ", filename)
            # print("current file's URL: ", FILE_TO_URL_MAP[filename])
            lines = f.read()
        soup = BeautifulSoup(lines, "html.parser")
        for a_link in soup.findAll("a"):
            href = a_link.attrs.get("href")
            if (href != "" or href is not None) and href in ALL_LINKS:
                # print("Found: ", href, "in: ", filename)
                out_link_filename = URL_TO_FILE_MAP[href]
                full_out_link_filename = DATA_DIR+out_link_filename
                current_file_adj_list.append(full_out_link_filename)
            else:
                continue
        current_file_adj_list.insert(0, full_filename)
        ALL_ADJ_ROWS.append(current_file_adj_list)

    with open(ADJ_LIST_FILENAME, 'w') as csv_f:
        writer = csv.writer(csv_f, delimiter=' ')
        writer.writerows(ALL_ADJ_ROWS)

    print("Finished generating adjacency lists. Written to: ", ADJ_LIST_FILENAME)


def generate_digraph():
    G = nx.read_adjlist(ADJ_LIST_FILENAME, create_using=nx.DiGraph())
    pr = nx.pagerank(G, max_iter=30)
    with open(PAGE_RANK_OUTPUT, 'w') as wf:
        for k, v in pr.items():
            line = k+"="+str(v)+"\n"
            wf.write(line)
    print("Finished generating PageRank file.")


if __name__ == "__main__":
    # create_hash_maps(URL_HTML_CSV_MAP_PATH)
    # extract_urls(DATA_DIR)
    generate_digraph()

