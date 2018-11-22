import numpy as np
from collections import namedtuple
import heapq


class SimulationClock:
    def __init__(self, starting_time = 0):
        self.time = starting_time
    
    def increment(self, delta):
        self.time = self.time + delta


class Exchange:
    def __init__(self, clock):
        self.asks = []
        self.bids = []
        self.order = namedtuple('order', ['price','t','quantity','trader','order_type'])
        # type: 0 -> marketable limit order; 1 -> market order;
        self.trades = [] 
        # time of execution; time of post; price; quantity; aggresor; passor; ag order type
        self.priority = ['price','t']
        self.clock = clock
        self.lastprice = None
        
    def post(self, price, quantity, trader, order_type):
        self.process_order(self.order(price, self.clock.time, quantity, trader, order_type))
        
    def get_best_ask(self):
        best_ask = heapq.nsmallest(1,self.asks)
        if best_ask == []:
            return None
        else:
            return best_ask[0]
        
    def get_best_bid(self):
        best_bid = heapq.nsmallest(1,self.bids)
        if best_bid == []:
            return None
        else:
            return best_bid[0]
        
    def process_order(self,order):
        if order.quantity > 0:
            # a bid
            price = order.price
            quantity = order.quantity
            # try to match any asks
            matching = True
            while matching:
                best_ask = self.get_best_ask()
                if best_ask == None:
                    matching = False
                else:
                    if price >= best_ask.price:
	                	if best_ask.trader == order.trader:
	                		# matched with self; cancel old order; queue new order
	                		heapq.heappop(self.asks)
	                		matching = False
	                	else:
	                        # order can be matched
	                        trade_price = best_ask.price
	                        if quantity < best_ask.quantity:
	                            new_ask = best_ask._replace(quantity = best_ask.quantity - quantity)
	                            heapq.heapreplace(self.asks,new_ask)
	                            trade_quantity = quantity
	                            quantity = 0
	                            matching = False
	                        elif quantity == best_ask.quantity:
	                            heapq.heappop(self.asks)
	                            trade_quantity = quantity
	                            quantity = 0
	                            matching = False
	                        elif quantity > best_ask.quantity:
	                            heapq.heappop(self.asks)
	                            trade_quantity = best_ask.quantity
	                            quantity = quantity - best_ask.quantity
	                        self.lastprice = trade_price
	                        self.trades.append((self.clock.time,best_ask.t,
	                                       trade_price,trade_quantity,
	                                       order.trader,best_ask.trader,1))
                    else:
                        matching = False
            # put onto order book
            if quantity != 0:
                new_bid = order._replace(price = -price, quantity = quantity)
                heapq.heappush(self.bids, new_bid)

        if order.quantity < 0:
            # an ask
            price = -order.price
            quantity = -order.quantity
            # try to match any bids
            matching = True
            while matching:
                best_bid = self.get_best_bid()
                if best_bid == None:
                    matching = False
                else:
                    if price >= best_bid.price:
                    	if best_bid.trader == order.trader:
	                		# matched with self; cancel old order; queue new order
	                		heapq.heappop(self.bids)
	                		matching = False
	                	else:
	                        # order can be matched
	                        trade_price = -best_bid.price
	                        if quantity < best_bid.quantity:
	                            new_bid = best_bid._replace(quantity = best_bid.quantity - quantity)
	                            heapq.heapreplace(self.bids,new_bid)
	                            trade_quantity = quantity
	                            quantity = 0
	                            matching = False
	                        elif quantity == best_bid.quantity:
	                            heapq.heappop(self.bids)
	                            trade_quantity = quantity
	                            quantity = 0
	                            matching = False
	                        elif quantity > best_bid.quantity:
	                            heapq.heappop(self.bids)
	                            trade_quantity = best_bid.quantity
	                            quantity = quantity - best_bid.quantity
	                        self.lastprice = trade_price
	                        self.trades.append((self.clock.time,best_bid.t,
	                                       trade_price,trade_quantity,
	                                       order.trader,best_bid.trader,-1))
                    else:
                        matching = False
            # put onto order book
            if quantity != 0:
                new_ask = order._replace(price = -price, quantity = quantity)
                heapq.heappush(self.asks, new_ask)

