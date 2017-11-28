from utils.preprocess import JSONLoader
import nltk
import networkx as nx
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from itertools import chain
from os.path import join
import pickle

class WNet(nx.Graph):
    
    adj = {'JJ','JJR','JJS'}

    def __init__(self, keywords):
        super().__init__()
        self.keywords = keywords
        for keyword in keywords:
            self.add_node(keyword)
        self.node[keyword]['count'] = 0
        
    def process_sentence(self, sent):
        sent = sent.lower()
        words = nltk.wordpunct_tokenize(sent)
#         print(words)
        if self.keywords not in words:
            return
        words = [word for word in words if word != self.keyword]
        words_tagged = nltk.pos_tag(words)
#         print(words_tagged)
        adjs = [word for (word, tag) in words_tagged if tag in WordNet.adj]
#         print(len(adjs))
        for adj in adjs:
            if not self.has_node(adj):
                self.add_edge(self.keyword, adj)
                self.node[adj]['count'] = 0
            self.node[adj]['count'] += 1
        
    def __call__(self, sent):
        self.process_sentence(sent)
        
    def draw(self, k = 5, cmap = 'Blues'):
        top_k = sorted(self.nodes(), key=lambda n: -self.node[n]['count'])[:k]
        counts = [self.node[n]['count'] for n in top_k]
        node_size = [(c - min(counts))/max(counts)*300 + 300 for c in counts]
        nodelist = top_k + [self.keyword]
        node_size = node_size + [max(node_size) * 1.3]
        edgelist = [(self.keyword, n) for n in top_k]
        pos = nx.spring_layout(self.subgraph(nodes=nodelist))
        labels = {n: n for n in nodelist}
        node_color = list(range(len(nodelist)))[::-1]
        #print(node_color)
#         nx.draw(self, pos, nodelist=nodelist,node_size=node_size,edgelist=edgelist, cmap=plt.cm.Blues)
        nx.draw_networkx_nodes(self, pos, nodelist=nodelist, node_size=node_size,
                               node_color = node_color, cmap = plt.cm.get_cmap(cmap))
        nx.draw_networkx_edges(self, pos, edgelist=edgelist)
        nx.draw_networkx_labels(self, pos, labels)

class WCloud:
    
    adj = {'JJ','JJR','JJS'}
    keywords = dict()
    keywords_types = ['price','food','atmosphere','staff']
    keywords['price'] = {'price', 'prices', 'cost', 'costs'}
    keywords['food'] = {'food','foods' 'menus','menu', 'meal', 'meals', 'drinks',
                 'taste', 'tastes', 'meats','meat','quality', 'qualities'}
    keywords['atmosphere'] = {'places','place','area','areas','atmospheres',
                           'atmosphere','decors','decoration','interiors','interior'}
    keywords['staff'] = {'services','service', 'staffs','staff', 'server',
                      'servers', 'waitresses','waitress','waiters','waiter'}
    with open('./data/bid2name', 'rb') as f:
        bid2name = pickle.load(f)

    def __init__(self, docs):
        super().__init__()
        self.docs = docs
    
    def process(self, bid):
        # Initialize
        wclouds = dict()
        
        for type in WCloud.keywords_types:
            words = []
            for sent in self.docs[bid]:
                words.extend(self.process_sent(sent, type))
            wclouds[type] = WordCloud(background_color='white', width=800, height=600).generate(' '.join(words))
            
        self.bid = bid
        self.wclouds = wclouds
    
    def process_sent(self, sent, type):
        sent = sent.lower()
        words = nltk.wordpunct_tokenize(sent)
        if len(set(WCloud.keywords[type]) & set(words)) == 0:
            words = []
            return words
        words_tagged = nltk.pos_tag(words)
        adjs = [word for (word, tag) in words_tagged if tag in WCloud.adj]
        words = [adj for adj in adjs if adj not in WCloud.keywords[type]]
        
        return words
        
    def __call__(self, doc, bid):
        return self.process_doc(doc, bid)
        
    def draw(self, show=True):
        for type in self.wclouds:
            plt.figure(figsize=(15,15))
            plt.imshow(self.wclouds[type], interpolation='bilinear',)
            plt.axis('off')
            if show:
                plt.show()
            else:
                fname = join('./data','wordcloud_%s_%s' % (WCloud.bid2name[self.bid], type))
                plt.savefig(fname)
                plt.close()
        
def load_reviews(data_dir):
    fields = ['business_id']
    city = ['Toronto']
    categories = ['Burgers','Seafood','Italian','Chinese','Japanese']
    business = 'business.json'
    review = 'review.json'

    jl = JSONLoader(business, data_dir, fields = fields)
    jl.set_condition(city=city, categories=categories)
    f_b, business_id = jl.sample(10000000)
    business_id = set([i[0] for i in business_id])

    # Get the reviews for the businesses in Toronto, and whose
    # categories are 'Burgers','Seafood','Italian','Chinese','Japanese'
    fields = ['business_id','text']
    jl = JSONLoader(review, data_dir, fields = fields)
    jl.set_condition(business_id = business_id)
    f_, rv = jl.sample(10000000)

    # dicionary of business, docs pair
    from collections import defaultdict
    business_doc = defaultdict(lambda: [])
    for b_id, b_rv in rv:
        # split into sentences and add
        sents = nltk.sent_tokenize(b_rv.lower())
        business_doc[b_id].extend(sents)
        
    print('The number of businesses: %i' % len(business_doc))
        
    return business_doc

def dociterator(docs, n_docs = None, print_every = 1000):
    for i, (b_id, sents) in enumerate(docs.items()):
        if n_docs != None and i >= n_docs:
            break
        if i % print_every == 0:
            print('Processing the document #%i' % i)
        for sent in sents:
            yield sent