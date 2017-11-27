from utils.preprocess import JSONLoader
import nltk
import networkx as nx
import matplotlib.pyplot as plt

class WordNet(nx.Graph):
    
    adj = {'JJ','JJR','JJS'}

    def __init__(self, keyword):
        super().__init__()
        self.keyword = keyword
        self.add_node(keyword)
        self.node[keyword]['count'] = 0
        
    def process_sentence(self, sent):
        sent = sent.lower()
        words = nltk.wordpunct_tokenize(sent)
#         print(words)
        if self.keyword not in words:
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