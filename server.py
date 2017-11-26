from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from json import loads

class FrequencySummarizer:
  def __init__(self, min_cut=0.1, max_cut=0.9):
    """
     Initilize the text summarizer.
     Words that have a frequency term lower than min_cut 
     or higer than max_cut will be ignored.
    """
    self._min_cut = min_cut
    self._max_cut = max_cut 
    self._stopwords = set(stopwords.words('english') + list(punctuation))

  def _compute_frequencies(self, word_sent):
    """ 
      Compute the frequency of each of word.
      Input: 
       word_sent, a list of sentences already tokenized.
      Output: 
       freq, a dictionary where freq[w] is the frequency of w.
    """
    freq = defaultdict(int)
    for s in word_sent:
      for word in s:
        if word not in self._stopwords:
          freq[word] += 1
    # frequencies normalization and fitering
    m = float(max(freq.values()))
    for w in freq.keys():
      freq[w] = freq[w]/m
      if freq[w] >= self._max_cut or freq[w] <= self._min_cut:
        del freq[w]
    return freq

  def summarize(self, text, n):
    """
      Return a list of n sentences 
      which represent the summary of text.
    """
    sents = sent_tokenize(text)
    n=max(1,len(sents)/20)
    word_sent = [word_tokenize(s.lower()) for s in sents]
    self._freq = self._compute_frequencies(word_sent)
    ranking = defaultdict(int)
    for i,sent in enumerate(word_sent):
      for w in sent:
        if w in self._freq:
          ranking[i] += self._freq[w]
    sents_idx = self._rank(ranking, n)    
    return [sents[j] for j in sents_idx]

  def _rank(self, ranking, n):
    """ return the first n sentences with highest ranking """
    return nlargest(n, ranking, key=ranking.get)


app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/summarize', methods=['POST'])
@cross_origin(supports_credentials=True)
def apicall():
  content=request.get_json()

  for i in range(len(content)):
    content[i]['text']="".join(fs.summarize(content[i]['text'].encode('ascii','ignore'),2))
    print(content[i]['text'])

 
  return jsonify(content)

@app.route('/hello', methods=['GET'])
@cross_origin(supports_credentials=True)
def apicall_2():
  # content=request.get_json()
  # print(content)
  return "Hello World!"

if __name__ == '__main__':
  fs=FrequencySummarizer()
  app.run(host='0.0.0.0',debug=True)
