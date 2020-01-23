import nltk
import os
from nltk import word_tokenize, pos_tag, ne_chunk
from nltk.corpus import stopwords
from nltk.tag import StanfordNERTagger

# library stanford untuk ner
st = StanfordNERTagger('stanford-ner-2018-10-16/classifiers/english.muc.7class.distsim.crf.ser.gz',
					   'stanford-ner-2018-10-16/stanford-ner-3.9.2.jar',
					   encoding='utf-8')

# path environment java
path = "C:/Program Files/Java/jdk1.8.0_101/bin/java.exe"
os.environ['JAVAHOME'] = path

# method untuk mendeteksi jenis jawaban dari pertanyaan
def type_detection(query):
    questions = ["who", "what", "where", "when", "how"]
    query = word_tokenize(query)

    question_word = ""
    type = ""
    for word in query:
        if word.lower() in questions:
            question_word = word.lower()
    
    if question_word == "who":
        type = "PERSON"
    elif question_word == "what":
        type = "PERSON ORGANIZATION"
    elif question_word == "where":
        type = "LOCATION"
    elif question_word == "when":
        type = "DATE"
    elif question_word == "how":
        for word in query:
            if word in ["much", "many"]:
                type = "MONEY"
    return type

# method untuk mencari fokus pertanyaan/formulation
# dengan cara menghapuskan stopword dan melakukan tokenisasi
def query_formulation(query):
    stop_words = set(stopwords.words('english'))
    tokenized_word = word_tokenize(query)
    filtererd_query = [word.lower() for word in tokenized_word if word.lower() not in stop_words]
    filtererd_query = [query for query in filtererd_query if query not in "?"]
    return filtererd_query

# method untuk memberi nilai/bobot pada kalimat yang relevan
# kemudian dari tiap kalimat diambil bobot paling maksima
def rank_docoument (query, documents):
    formulas = query_formulation(query)
    documents = [[word.lower() for word in sentence ]for sentence in documents]
    weight = []
    for document in documents:
        val = 0
        for formula in formulas:
            if formula in document:
                val += 1
        weight.append(val)
    
    idxTopDoc = weight.index(max(weight))
    print(documents[idxTopDoc], weight[idxTopDoc])
    return idxTopDoc

# standford ner melakukan chunking perkata
# sehingga kata berjenis noun phrase harus digabungkan
# method ini digunakan untuk menggabungkan ner untuk noun phrase
def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []
    
    for token, tag in tagged_sent:
        if tag != "O":
            current_chunk.append((token, tag))
        else:
            if current_chunk: 
                # jika current_chunk tidak kosong
                continuous_chunk.append(current_chunk)
                current_chunk = []

    if current_chunk:
        continuous_chunk.append(current_chunk)

    ner_join = [(" ".join([token for token, tag in ne]), ne[0][1]) for ne in continuous_chunk]
    return ner_join

# method untuk melakukan retreive sentence yang relevan
def passage_document(query, text):
    # process corpus
    sentences = nltk.sent_tokenize(text)
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
    ner_sentences = st.tag_sents(tokenized_sentences)

    # get Answer Type Entities
    type = type_detection(query)
    print("AET:", type)

    # get index top document
    idxTopDoc = rank_docoument(query, tokenized_sentences)

    # combine the entities
    named_entities = get_continuous_chunks(ner_sentences[idxTopDoc])
    print(named_entities)

    
    answer = "None"
    for  entity in named_entities:
        if entity[1] in type:
            answer = entity[0]

    print("A:", answer)
    
text = "World War II or second world war happened from 1st September 1939-1945. The war is motivated by Benito Mussolini in Italy that make a movement to make a Great Italy. In Germany, the war was spearheaded by Adolf Hitler by forming Nazi. Great powers country joined this war and make two opposing alliances. This war called as the biggest war in history because the parties that joined this war use all potential they have like economics, industry, and scientific ability as much as they. World War II began when Germany make an invantion to Poland in 1 September 1939 - 6 October 1939. The war ended with Japan signed Japanese Instrument of Surrender documents on board the USS Missouri. World War II happened at three old continent namely Africa, Asia, and Europe. World War II cost $4.1 trillion, according to data from the Congressional Research Service."

# query = "who is motivated war in Italy?"
# print("Q:", query)
# passage_document(query, text)

# query = "when were world war 2 happened?"
# print("Q:", query)
# passage_document(query, text)

# query = "where were the war spearheaded by Adolf Hitler ?"
# print("Q:", query)
# passage_document(query, text)

# query = "who was spearheaded the war by forming the NAZI?"
# print("Q:", query)
# passage_document(query, text)

# query = "how many cost caused by word war II according to data from the Congressional Research Service ?"
# print("Q:", query)
# passage_document(query, text)

# # salah
# query = "what was Adolf Hitler forming to spearheaded the war ?"
# print("Q:", query)
# passage_document(query, text) 

# query = "what data says world war costs a lot?"
# print("Q:", query)
# passage_document(query, text)

# # salah
# query = "when was Germany make an invation to Poland?"
# print("Q:", query)
# passage_document(query, text)

# # salah
# query = "where were Benito Mussolini make Great Italy ?"
# print("Q:", query)
# passage_document(query, text)

# query = "where were japan signed documents surrender ?"
# print("Q:", query)
# passage_document(query, text)

query = "what was the country that benito mussolino motivated?"
print("Q:", query)
passage_document(query, text)