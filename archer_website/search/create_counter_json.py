import json
import re
from collections import Counter

common_words = Counter()
filename = "big_news.txt"
json_filename = "counter_json.json"
with open(filename, "r", encoding='utf-8') as f:
    for line in f:
        for match in re.finditer(r'\w+', line.lower()):
            word = match.group()
            if len(word) > 3:
                common_words[word] += 1

print(common_words.most_common(50))

with open(json_filename, 'w') as jf:
    json.dump(common_words, jf)
