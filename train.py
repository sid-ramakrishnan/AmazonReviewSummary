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
from rouge import Rouge
from attention_decoder import AttentionDecoder

BATCH_SIZE = 128
NUM_LAYERS = 1
HIDDEN_DIM = 300
EPOCHS = 15

MAX_LEN = 200
SUM_LEN = 10
VOCAB_SIZE = 40000

def convert_text(text, word2index, max_len=0):
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
 
    return text, max_len
    
        

def load_data(article, summary, max_len, vocab_size):
    
    counter_art=Counter(itertools.chain.from_iterable(article))
    counter_summ=Counter(itertools.chain.from_iterable(summary))
    
    most_cmn_art=counter_art.most_common(vocab_size-1)
    most_cmn_summ=counter_summ.most_common(vocab_size-1)
    
#     print(most_cmn_art)
    
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
    # TO-DO
    # create and return the model for unidirectional LSTM encoder decoder
    model=Sequential()
    model.add(Embedding(X_vocab_len, 300, input_length=X_max_len))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True, recurrent_dropout=0.2)))
    model.add(Dropout(0.3))
    model.add(LSTM(hidden_size, return_sequences=True))
    model.add(TimeDistributed(Dense(y_vocab_len, activation='softmax')))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
    return model

def create_UniLSTMwithAttention(X_vocab_len, X_max_len, y_vocab_len, y_max_len, hidden_size, num_layers, return_probabilities = False):
    model=Sequential()
    model.add(Embedding(X_vocab_len, 300, input_length=X_max_len))
    model.add(Bidirectional(LSTM(hidden_size, return_sequences=True, recurrent_dropout=0.2)))
    model.add(AttentionDecoder(hidden_size, name='decoder', output_dim=y_vocab_len, return_probabilities= return_probabilities, trainable=True))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['acc'])
    return model




if __name__ == '__main__':

    article_train=read_file('review.txt')
    summary_train=read_file('summary.txt')

    print(article_train[0])

    article_trn, max_length, idx2word_art, word2idx_art, summary_trn, idx2word_sum, word2idx_sum= load_data(article_train, summary_train, MAX_LEN, VOCAB_SIZE)

    MAX_LEN = max_length

    model=create_UniLSTM(VOCAB_SIZE+1, MAX_LEN, VOCAB_SIZE+1, MAX_LEN, HIDDEN_DIM, 1)
    model.summary()
    tensorboard = TensorBoard(log_dir='./logs/{}'.format(7),histogram_freq=0, write_graph=True, write_images=False)
    model.fit_generator(generator(article_trn, summary_trn, BATCH_SIZE), epochs=EPOCHS, steps_per_epoch=100, callbacks=[tensorboard])

    # Saving summarization model to json

    model_json = model.to_json()
    with open("model_noatt.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model_noatt.h5")
    print("Saved model to disk")

    article_test=read_file('rev.txt')
    article_tst,_= convert_text(article_test, word2idx_art, MAX_LEN)
    article_tst=np.array(article_tst)
    
    prediction= model.predict(x= article_tst)
    prediction=np.argmax(prediction, axis=2)

    recover=[]
    for j, line in enumerate(prediction):
        lin=[]
        for i, word in enumerate(line):
            h=idx2word_sum[word]
            if h!='ZERO':
                lin.append(h)
        recover.append(' '.join(lin))

    summary_test=read_file('test_title.txt')
    original=[' '.join(li) for li in summary_test]

    rouge=Rouge()
    scores = rouge.get_scores(recover, original, avg=True)
    print(scores)
