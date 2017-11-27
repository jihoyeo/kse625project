from utils.preprocess import JSONLoader
from collections import defaultdict
import numpy as np
import pickle
import os
from os.path import join
import networkx as nx
from geopy.distance import vincenty

class Recommender:
    '''
    Class for making influence-based recommendations
    '''
            
    def __init__(self, data_raw, data_pkl, user_id, user_loc, G):
        '''
        Args:
            data_raw (str): directory where raw dataset resides
            data_pkl (str): directory where pickle files reside
            user_id (str): unique user id
            user_loc (tuple): (latitude, longitude) of the user
            G (Friendship): friendship and influence structure
        '''
        self.data_raw = data_raw
        self.data_pkl = data_pkl
        self.jl_rv = JSONLoader('review.json', data_raw, fields = ['user_id','business_id'])
        self.jl_b = JSONLoader('business.json', data_raw, fields = ['business_id'])
        self.G = G
        self.user = self.User(user_id, user_loc, G)
        self.rest_id = self.init_rest()
        self.sc = self.SimCalculator()
        self.dc = self.DistCalculator(data_raw)
        
    def recommend(self, category):
        '''
        Args:
            category (str): the category to make recommendations on
        Returns:
            
        '''
        categories = [category]
        self.jl_b.set_condition(categories = categories, business_id = self.rest_id)
        _, cat_ids = self.jl_b.sample(10000000)
        cat_ids = [i[0] for i in cat_ids]
        
        self.jl_rv.set_condition(stars = [5], business_id = cat_ids, user_id = self.user.popular_friends)
        _, reviews = self.jl_rv.sample(10000000)
        reviews = sorted(reviews, key = lambda x: -self.G.node[x[0]]['influence'])
        
#         print('The number of 5-star reviews from the popular friends: %i' % len(reviews))
        
        # Aggregate all users who recommended the items
        recs = defaultdict(lambda: [])
        for u_id, b_id in reviews:
            recs[b_id].append(u_id)
        recs = dict(recs)
        
        # Point size for Plotting, based on user influences
        point_size = {b_id: np.sum([self.G.node[u_id]['influence']
                                    for u_id in recs[b_id]]) for b_id in recs}
        
        att = {b_id: self.sc(category, b_id) for b_id in recs}
        loc = {b_id: self.dc(self.user.xy, self.dc.xy[b_id]) for b_id in recs}
        
        assert len(point_size) == len(att) and len(att) == len(loc)
        
        print('The number of recommendations: %i' % len(att))
        
        return category, point_size, att, loc
    
    def init_rest(self):
        with open('./data/business_doc', 'rb') as f:
            doc_business = pickle.load(f)
            rest_id = set(doc_business.keys())
            print('The number of restaurants: %i' % len(rest_id))
        
        return rest_id
        
    class User:
        '''
        Inner class that represents a user
        '''
        def __init__(self, user_id, user_xy, G):
            self.id = user_id
            self.xy = user_xy
            self.popular_friends = self.get_popular_friends(G)
            print('User id: %s' % user_id)
            print('User location: (%.3f,%.3f)' % user_xy)
            print('The number of popular friends: %i' % len(self.popular_friends))
            
        def get_popular_friends(self, G, k = 100000):
            '''
            Find popular friends of the user

            Args:
                G (utils.friendship.Friendship): the friendship structure and the friend's influences
            '''
            popular_friends = [friend for friend in G.neighbors(self.id)]
            popular_friends = sorted(popular_friends, key = lambda f: -G.node[f]['influence'])
            popular_friends = popular_friends[:k]
            
            return popular_friends
        
        def __call__(self):
            return self.id
        
    class SimCalculator:
    
        def __init__(self):
            self.categories =['Burgers','Seafood','Italian','Chinese','Japanese']
            self.sims = dict()
            for cat in self.categories:
                with open('./data/cos_sim_%s' % cat, 'rb') as f:
                    self.sims[cat] = dict(pickle.load(f))

        def __getitem__(self, key):
            return self.sims[key]
        
        def __call__(self, category, b_id):
            '''
            Returns:
                similarity between the category and business id
            '''
            return self[category][b_id]
    
    class DistCalculator:
        
        def __init__(self, data_dir):
            business = 'business.json'
            fields = ['business_id','latitude', 'longitude']
            categories =['Burgers','Seafood','Italian','Chinese','Japanese']
            city = ['Toronto']
            jl = JSONLoader(business, data_dir, fields = fields)
            jl.set_condition(city=city, categories=categories)
            _, rest_loc = jl.sample(10000000)
            
            self.xy = dict()
        
            for rest in rest_loc:
                b_id, x, y = rest
                self.xy[b_id] = (x,y)
        
        def __call__(self, xy_0, xy_1):
            '''
            Calculates the distances between the two points
            
            Args:
                xy_0, xy_1 (tuple): (latitude, longitude)
            '''
            
            return vincenty(xy_0, xy_1).meters