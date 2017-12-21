from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.corpus import stopwords
from collections import defaultdict
from string import punctuation
from heapq import nlargest
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from json import loads
import numpy as np
from collections import Counter
import itertools
import string

from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout, RepeatVector
from keras.layers.wrappers import TimeDistributed
from keras.layers.recurrent import LSTM
from keras.layers.embeddings import Embedding
from keras.layers import Bidirectional
from keras.callbacks import TensorBoard
from keras.regularizers import l2
from keras.models import model_from_json
from rouge import Rouge
import pickle

BATCH_SIZE = 128
NUM_LAYERS = 1
HIDDEN_DIM = 300
EPOCHS = 50

MAX_LEN = 30
SUM_LEN = 10
VOCAB_SIZE = 40001



def convert_text(text, word2index, max_len=MAX_LEN):
    if max_len==0:
        max_len=max([len(a) for a in text])
    for cnt, line in enumerate(text):
        for i, word in enumerate(line):
            index=word2index.get(word,word2index.get('unk'))
            line[i]=index
        if len(line)< max_len:
            line.extend([0]*(max_len-len(line)))
        else:
            line_mod=line[:max_len]
            text[cnt]=line_mod
 
    return text
    
        

def load_data(article, summary, max_len, vocab_size):
    
    counter_art=Counter(itertools.chain.from_iterable(article))
    counter_summ=Counter(itertools.chain.from_iterable(summary))
    
    most_cmn_art=counter_art.most_common(vocab_size-1)
    most_cmn_summ=counter_summ.most_common(vocab_size-1)
    
    idx2word_art={id:i for id,(i,_) in enumerate(most_cmn_art,start=2)}
    idx2word_sum={id:i for id,(i,_) in enumerate(most_cmn_summ,start=2)}
    word2idx_art={i:id for id,(i,_) in enumerate(most_cmn_art,start=2)}
    word2idx_sum={i:id for id,(i,_) in enumerate(most_cmn_summ,start=2)}
    
    idx2word_art[0]='ZERO'
    idx2word_sum[0]='ZERO'
    word2idx_art['ZERO']=0
    word2idx_sum['ZERO']=0
    
    idx2word_art[1]='unk'
    idx2word_sum[1]='unk'
    word2idx_art['unk']=1
    word2idx_sum['unk']=1
    
    article, max_len=convert_text(article, word2idx_art)
    summary, _=convert_text(summary, word2idx_sum, max_len)
    
    return (np.array(article), max_len, idx2word_art, word2idx_art, np.array(summary), idx2word_sum, word2idx_sum)

def convert_to_onehot(input, max_len=MAX_LEN, vocab_length=VOCAB_SIZE+1):
    output=np.zeros((len(input), max_len, vocab_length))
    y= range(max_len)
    for i, sent in enumerate(input):      
        output[i, y, sent]=1
    return output

def read_file(file):
    content=[]
    with open(file,'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip().translate(str.maketrans('','',string.punctuation))
            line=line.split()
            if 's' in line:
                line.remove('s')
            content.append(line)
    return content

def generator(article, summary, batch_size):
    while True:
        index=np.random.choice(len(article), batch_size, replace=False)
        summ=convert_to_onehot(summary[index], MAX_LEN)
        art=article[index]
        yield art,summ

def create_UniLSTM(X_vocab_len, X_max_len, y_vocab_len, y_max_len, hidden_size, num_layers):
    model=Sequential()
    model.add(Embedding(X_vocab_len, 300, input_length=X_max_len))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True, recurrent_dropout=0.2)))
    model.add(Dropout(0.3))
    model.add(LSTM(hidden_size, return_sequences=True))
    model.add(TimeDistributed(Dense(y_vocab_len, activation='softmax')))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
    return model



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
    # n=max(1,len(sents)/20)
    n=min(2,len(sents))
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

  to_summarize=[]

  for i in range(len(content)):
    # content[i]['text']="".join(fs.summarize(content[i]['text'].encode('ascii','ignore'),2))
    content[i]['text']=fs.summarize(content[i]['text'].encode('ascii','ignore'),2)
    to_summarize.append(content[i]['text'])

    print(content[i]['text'])

  to_summ=convert_text(to_summarize,word2idx_art)
  predicted=model.predict(x= to_summ)
  prediction=np.argmax(prediction, axis=2)
  recover=[]
  for j, line in enumerate(prediction):
      lin=[]
      for i, word in enumerate(line):
          h=idx2word_sum[word]
          if h!='ZERO' and h!='unk':
              lin.append(h)
      recover.append(' '.join(lin))
  for i in range(len(content)):
    content[i]['text']=recover[i]
  return jsonify(content)

@app.route('/hello', methods=['GET'])
@cross_origin(supports_credentials=True)
def apicall_2():
  # content=request.get_json()
  # print(content)
  return "Hello World!"

if __name__ == '__main__':
  fs=FrequencySummarizer()
  json_file = open('model_noatt.json', 'r')
  loaded_model_json = json_file.read()
  json_file.close()
  model = model_from_json(loaded_model_json)
  # load weights into new model
  model.load_weights("model_noatt.h5")
  model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
  print("Loaded model from disk")

  with open('word_dicts_noatt.pickle', 'rb') as handle:
    idx2word_art,idx2word_sum, word2idx_art, word2idx_sum = pickle.load(handle)
  print("Loaded word_dicts_noatt from disk")

  app.run(host='0.0.0.0',port=80, debug=True)
