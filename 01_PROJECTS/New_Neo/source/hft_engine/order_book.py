"""
Limit Order Book Management for Coinbase L3 Data
Handles order book reconstruction, sequence validation, and state management
"""
import asyncio
import json
import aiohttp
from collections import defaultdict
from sortedcontainers import SortedDict
from datetime import datetime
import time


class OrderBook:
    def __init__(self, product_id="BTC-USD"):
        self.product_id = product_id
        self.bids = SortedDict()  # price -> {order_id: size}
        self.asks = SortedDict()  # price -> {order_id: size}
        self.orders = {}  # order_id -> {side, price, size}
        self.sequence = 0
        self.last_update_time = None
        
    def get_best_bid(self):
        if not self.bids:
            return None, 0
        best_price = next(reversed(self.bids))
        total_size = sum(self.bids[best_price].values())
        return best_price, total_size
    
    def get_best_ask(self):
        if not self.asks:
            return None, 0
        best_price = next(iter(self.asks))
        total_size = sum(self.asks[best_price].values())
        return best_price, total_size
    
    def get_mid_price(self):
        bid_price, _ = self.get_best_bid()
        ask_price, _ = self.get_best_ask()
        if bid_price is None or ask_price is None:
            return None
        return (bid_price + ask_price) / 2
    
    def get_spread(self):
        bid_price, _ = self.get_best_bid()
        ask_price, _ = self.get_best_ask()
        if bid_price is None or ask_price is None:
            return None
        return ask_price - bid_price
    
    def get_depth(self, levels=5):
        """Get top N levels of bid and ask"""
        bid_levels = []
        ask_levels = []
        
        # Get top bids (highest prices)
        for price in reversed(list(self.bids.keys())[-levels:]):
            total_size = sum(self.bids[price].values())
            bid_levels.append((price, total_size))
        
        # Get top asks (lowest prices)
        for price in list(self.asks.keys())[:levels]:
            total_size = sum(self.asks[price].values())
            ask_levels.append((price, total_size))
        
        return bid_levels, ask_levels
    
    def process_received(self, order_id, price, size, side):
        """Process a new limit order"""
        price = float(price)
        size = float(size)
        
        if side == 'buy':
            if price not in self.bids:
                self.bids[price] = {}
            self.bids[price][order_id] = size
        else:
            if price not in self.asks:
                self.asks[price] = {}
            self.asks[price][order_id] = size
        
        self.orders[order_id] = {'side': side, 'price': price, 'size': size}
    
    def process_open(self, order_id, price, size, side):
        """Process an order opening (same as received for L3)"""
        self.process_received(order_id, price, size, side)
    
    def process_done(self, order_id, price=None, size=None, reason=None):
        """Process an order completion (fill or cancel)"""
        if order_id not in self.orders:
            return
        
        order = self.orders[order_id]
        side = order['side']
        order_price = order['price']
        
        if side == 'buy':
            if order_price in self.bids and order_id in self.bids[order_price]:
                del self.bids[order_price][order_id]
                if not self.bids[order_price]:
                    del self.bids[order_price]
        else:
            if order_price in self.asks and order_id in self.asks[order_price]:
                del self.asks[order_price][order_id]
                if not self.asks[order_price]:
                    del self.asks[order_price]
        
        del self.orders[order_id]
    
    def process_match(self, trade_id, size, price, side):
        """Process a trade execution"""
        # Matches are already reflected in done messages for L3
        # This is for tracking trade information
        pass
    
    def process_change(self, order_id, new_size):
        """Process an order size change"""
        if order_id not in self.orders:
            return
        
        order = self.orders[order_id]
        side = order['side']
        price = order['price']
        new_size = float(new_size)
        
        if side == 'buy':
            if price in self.bids and order_id in self.bids[price]:
                self.bids[price][order_id] = new_size
        else:
            if price in self.asks and order_id in self.asks[price]:
                self.asks[price][order_id] = new_size
        
        order['size'] = new_size
    
    def clear(self):
        """Clear the order book"""
        self.bids.clear()
        self.asks.clear()
        self.orders.clear()
        self.sequence = 0
    
    def get_book_state(self):
        """Get current book state for snapshot"""
        return {
            'sequence': self.sequence,
            'bids': self.get_depth(10)[0],
            'asks': self.get_depth(10)[1],
            'mid_price': self.get_mid_price(),
            'spread': self.get_spread(),
            'timestamp': datetime.utcnow().isoformat()
        }