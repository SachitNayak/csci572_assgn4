from os import listdir
from tika import parser
import re

data_root = '/home/sachinpnaikhazard/latimes/'
output_file = '/home/sachinpnaikhazard/big_news.txt'

for filename in listdir(data_root):
    full_filename = data_root + filename
    parsed = parser.from_file(full_filename)
    content = parsed["content"]
    cleaned_content = re.sub("\s\s+", " ", content)
    sep_cleaned_content = cleaned_content+"\n\n"
    with open(output_file, 'a') as f:
        f.write(sep_cleaned_content)
print("done.")
