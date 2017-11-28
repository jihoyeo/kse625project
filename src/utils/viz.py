import matplotlib.pyplot as plt
import seaborn as sns
sns.set()
import pickle

def scatterplot(cat, ps, att, loc):
    '''
    Args:
        cat (str): the name of the attribute
        ps (dict): point sizes
        att (dict): attribute values
        loc (dict): location
    '''
    with open('./data/bid2name', 'rb') as f:
        bid2name = pickle.load(f)
    
    fig = plt.figure(figsize=(15,15))
    for bid in ps.keys():
        plt.scatter(x = loc[bid], y = att[bid], s = ps[bid] * 1000000, alpha=0.7)
        plt.annotate(bid2name[bid], (loc[bid], att[bid]))
    
    plt.xlabel('distance(meters)')
    plt.gca().invert_yaxis()
    plt.ylabel('similarity to %s' % cat)
    plt.show()