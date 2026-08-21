"""
Coinbase WebSocket Client for L3 Order Book Data
Handles connection, subscription, message processing, and reconnection
"""
import asyncio
import json
import websockets
import aiohttp
from datetime import datetime
import logging
import hmac
import hashlib
import base64
from order_book import OrderBook
from error_handler import retry_on_error, global_error_handler
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoinbaseWebSocketClient:
    def __init__(self, product_id="BTC-USD"):
        self.product_id = product_id
        self.order_book = OrderBook(product_id)
        self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        self.rest_url = "https://api.exchange.coinbase.com"
        self.websocket = None
        self.running = False
        self.reconnect_delay = 1
        self.max_reconnect_delay = 30
        self.message_queue = asyncio.Queue()
        self.callback = None
        
        # API credentials
        self.api_key = config.COINBASE_API_KEY
        self.api_secret = config.COINBASE_API_SECRET
        self.api_passphrase = config.COINBASE_API_PASSPHRASE
        
        # Check if we have API credentials for L3
        self.use_l3 = bool(self.api_key and self.api_secret)
        self.data_source = config.DATA_SOURCE if hasattr(config, 'DATA_SOURCE') else "l3"  # Default to L3 now with credentials
        
        # Message counters for debugging
        self.message_counts = {
            'ticker': 0,
            'l2update': 0,
            'snapshot': 0,
            'heartbeat': 0,
            'unknown': 0
        }
        
        if self.use_l3 or self.data_source == "l3":
            logger.info("Configured for L3 data with API credentials")
        else:
            logger.info("Configured for L2 data (public, no credentials required)")
    
    def generate_signature(self, timestamp, method, request_path, body=''):
        """Generate HMAC signature for Coinbase API authentication"""
        message = timestamp + method + request_path + body
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message.encode('utf-8'), hashlib.sha256).digest()
        return base64.b64encode(signature).decode('utf-8')
    
    async def make_authenticated_request(self, method, request_path, body=''):
        """Make authenticated request to Coinbase API"""
        timestamp = str(int(datetime.utcnow().timestamp()))
        signature = self.generate_signature(timestamp, method, request_path, body)
        
        headers = {
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-SIGN': signature,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'Content-Type': 'application/json'
        }
        
        if self.api_passphrase:
            headers['CB-ACCESS-PASSPHRASE'] = self.api_passphrase
        
        async with aiohttp.ClientSession() as session:
            url = self.rest_url + request_path
            async with session.request(method, url, headers=headers, data=body if body else None) as response:
                return await response.json()
    
    async def get_prediction_market_target(self):
        """Fetch prediction market target price from CF Benchmarks or Coinbase"""
        # Try CF Benchmarks first (most accurate for prediction markets)
        if config.CF_BENCHMARKS_API_KEY and config.CF_BENCHMARKS_API_USERNAME:
            try:
                return await self.get_cf_benchmarks_rti()
            except Exception as e:
                logger.error(f"Error fetching CF Benchmarks RTI: {e}")
        
        # Fallback to Coinbase spot price
        try:
            ticker = await self.make_authenticated_request('GET', f'/products/{self.product_id}/ticker')
            return float(ticker.get('price', 0))
        except Exception as e:
            logger.error(f"Error fetching Coinbase ticker: {e}")
            # Final fallback to public API
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.rest_url}/products/{self.product_id}/ticker") as response:
                        if response.status == 200:
                            data = await response.json()
                            return float(data.get('price', 0))
            except Exception as e2:
                logger.error(f"Error fetching fallback ticker: {e2}")
                return None
    
    async def get_cf_benchmarks_rti(self):
        """Fetch CF Benchmarks Real Time Index for accurate prediction market targets"""
        try:
            # CF Benchmarks API requires Basic Auth
            import base64
            credentials = f"{config.CF_BENCHMARKS_API_USERNAME}:{config.CF_BENCHMARKS_API_KEY}"
            encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
            
            headers = {
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json'
            }
            
            # Try to get BRTI (Bitcoin Real Time Index)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config.CF_BENCHMARKS_API_URL}/index/brti",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Parse the RTI value from response
                        # Response structure may vary based on actual API
                        if 'index' in data:
                            return float(data['index'])
                        elif 'price' in data:
                            return float(data['price'])
                        elif 'last' in data:
                            return float(data['last'])
                    else:
                        logger.error(f"CF Benchmarks API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching CF Benchmarks RTI: {e}")
            return None
        
    async def connect(self):
        """Establish WebSocket connection"""
        while self.running:
            try:
                logger.info(f"Connecting to {self.ws_url}")
                self.websocket = await websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=30
                )
                logger.info("WebSocket connected successfully")
                self.reconnect_delay = 1
                await self.subscribe()
                await self.listen()
            except Exception as e:
                global_error_handler.record_error("websocket_client", e)
                logger.error(f"Connection error: {e}")
                if self.running:
                    await self.handle_reconnect()
    
    async def handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        logger.info(f"Reconnecting in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)
        self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
    
    async def subscribe(self):
        """Subscribe to appropriate channels based on configuration"""
        if self.use_l3 or self.data_source == "l3":
            # L3 subscription (requires authentication)
            subscribe_message = {
                "type": "subscribe",
                "product_ids": [self.product_id],
                "channels": [
                    {"name": "level3", "product_ids": [self.product_id]},
                    {"name": "heartbeat", "product_ids": [self.product_id]},
                    {"name": "ticker", "product_ids": [self.product_id]}
                ]
            }
            logger.info(f"Subscribing to L3 channels for {self.product_id}")
        else:
            # L2 subscription (public) - try different channel names
            subscribe_message = {
                "type": "subscribe",
                "product_ids": [self.product_id],
                "channels": [
                    {"name": "level2", "product_ids": [self.product_id]},
                    {"name": "heartbeat", "product_ids": [self.product_id]},
                    {"name": "ticker", "product_ids": [self.product_id]}
                ]
            }
            logger.info(f"Subscribing to L2, heartbeat, and ticker for {self.product_id}")
        
        await self.websocket.send(json.dumps(subscribe_message))
        logger.info(f"Subscription sent for {self.product_id}")
    
    async def get_snapshot(self):
        """Fetch L2 order book snapshot via REST API"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.rest_url}/products/{self.product_id}/book?level=2"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Failed to fetch snapshot: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching snapshot: {e}")
            return None
    
    async def synchronize_book(self):
        """Synchronize order book with REST snapshot (L2 format)"""
        logger.info("Synchronizing order book with REST snapshot...")
        snapshot = await self.get_snapshot()
        
        if snapshot:
            self.order_book.clear()
            
            # Process bids (L2 format: [price, size, num_orders])
            for bid in snapshot.get('bids', []):
                price = float(bid[0])
                size = float(bid[1])
                order_id = f"bid_{price}"
                self.order_book.process_received(order_id, price, size, 'buy')
            
            # Process asks (L2 format: [price, size, num_orders])
            for ask in snapshot.get('asks', []):
                price = float(ask[0])
                size = float(ask[1])
                order_id = f"ask_{price}"
                self.order_book.process_received(order_id, price, size, 'sell')
            
            self.order_book.sequence = snapshot.get('sequence', 0)
            logger.info(f"Book synchronized at sequence {self.order_book.sequence}")
            return True
        
        return False
    
    async def listen(self):
        """Listen for WebSocket messages"""
        async for message in self.websocket:
            try:
                data = json.loads(message)
                await self.process_message(data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def process_message(self, data):
        """Process incoming WebSocket message"""
        msg_type = data.get('type')
        
        # Count message types for debugging
        if msg_type in self.message_counts:
            self.message_counts[msg_type] += 1
        else:
            self.message_counts['unknown'] += 1
        
        # Log every 50 messages to see what we're getting
        total_messages = sum(self.message_counts.values())
        if total_messages % 50 == 0:
            logger.info(f"Message counts: {self.message_counts}")
        
        if msg_type == 'heartbeat':
            # Ignore heartbeats
            pass
        
        elif msg_type == 'snapshot':
            # Handle initial snapshot
            await self.handle_snapshot(data)
        
        elif msg_type == 'l2update':
            # Handle L2 order book updates
            await self.handle_l2_update(data)
        
        elif msg_type == 'ticker':
            # Handle ticker updates for price
            await self.handle_ticker(data)
        
        elif msg_type in ['received', 'open', 'done', 'match', 'change']:
            await self.handle_book_update(data)
        
        elif msg_type == 'error':
            logger.error(f"Error message: {data.get('message')}")
        
        elif msg_type == 'subscriptions':
            logger.info("Subscription confirmed")
            logger.info(f"Subscribed channels: {data.get('channels', [])}")
        
        else:
            # Log unknown message types for debugging
            if msg_type not in ['subscriptions', 'error']:
                logger.debug(f"Unknown message type: {msg_type}")
    
    async def handle_snapshot(self, data):
        """Handle initial snapshot message (L2 format)"""
        self.order_book.clear()
        
        # Process bids (L2 format: [price, size, num_orders])
        for bid in data.get('bids', []):
            price = float(bid[0])
            size = float(bid[1])
            # Generate a fake order ID for L2 aggregated data
            order_id = f"bid_{price}"
            self.order_book.process_received(order_id, price, size, 'buy')
        
        # Process asks (L2 format: [price, size, num_orders])
        for ask in data.get('asks', []):
            price = float(ask[0])
            size = float(ask[1])
            # Generate a fake order ID for L2 aggregated data
            order_id = f"ask_{price}"
            self.order_book.process_received(order_id, price, size, 'sell')
        
        self.order_book.sequence = data.get('sequence', 0)
        logger.info(f"Processed L2 snapshot at sequence {self.order_book.sequence}")
    
    async def handle_l2_update(self, data):
        """Handle L2 order book updates"""
        changes = data.get('changes', [])
        if not changes:
            return
        
        logger.debug(f"Processing {len(changes)} order book changes")
        
        for change in changes:
            if len(change) < 3:
                continue
                
            side = change[0]  # 'buy' or 'sell'
            price = float(change[1])
            size = float(change[2])
            
            order_id = f"{side}_{price}"
            
            if size == 0:
                # Remove order if size is 0
                self.order_book.process_done(order_id)
            else:
                # Update or add order
                if order_id in self.order_book.orders:
                    self.order_book.process_change(order_id, size)
                else:
                    self.order_book.process_received(order_id, price, size, side)
        
        # Increment sequence for local tracking
        self.order_book.sequence += 1
        
        # Queue message for processing
        await self.message_queue.put(data)
        
        # Call callback if registered
        if self.callback:
            await self.callback(data, self.order_book)
    
    async def handle_ticker(self, data):
        """Handle ticker updates for current price"""
        # Update current price from ticker
        price = data.get('price')
        if price:
            # We could update a separate current price tracker here
            pass
        
        # Queue message for processing
        await self.message_queue.put(data)
        
        # Call callback if registered
        if self.callback:
            await self.callback(data, self.order_book)
    
    async def handle_book_update(self, data):
        """Handle order book update message"""
        sequence = data.get('sequence', 0)
        
        # Check for sequence gap
        if self.order_book.sequence > 0 and sequence != self.order_book.sequence + 1:
            logger.warning(f"Sequence gap detected: expected {self.order_book.sequence + 1}, got {sequence}")
            await self.synchronize_book()
            return
        
        self.order_book.sequence = sequence
        msg_type = data.get('type')
        
        if msg_type == 'received':
            order_id = data.get('order_id')
            price = data.get('price')
            size = data.get('size')
            side = data.get('side')
            if order_id and price and size and side:
                self.order_book.process_received(order_id, price, size, side)
        
        elif msg_type == 'open':
            order_id = data.get('order_id')
            price = data.get('price')
            size = data.get('remaining_size')
            side = data.get('side')
            if order_id and price and size and side:
                self.order_book.process_open(order_id, price, size, side)
        
        elif msg_type == 'done':
            order_id = data.get('order_id')
            price = data.get('price')
            size = data.get('remaining_size')
            reason = data.get('reason')
            if order_id:
                self.order_book.process_done(order_id, price, size, reason)
        
        elif msg_type == 'match':
            trade_id = data.get('trade_id')
            size = data.get('size')
            price = data.get('price')
            side = data.get('side')
            if trade_id and size and price:
                self.order_book.process_match(trade_id, size, price, side)
        
        elif msg_type == 'change':
            order_id = data.get('order_id')
            new_size = data.get('new_size')
            if order_id and new_size:
                self.order_book.process_change(order_id, new_size)
        
        # Queue message for processing
        await self.message_queue.put(data)
        
        # Call callback if registered
        if self.callback:
            await self.callback(data, self.order_book)
    
    def register_callback(self, callback):
        """Register callback function for processing updates"""
        self.callback = callback
    
    async def start(self):
        """Start the WebSocket client"""
        self.running = True
        await self.connect()
    
    async def stop(self):
        """Stop the WebSocket client"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("WebSocket connection closed")
    
    def get_order_book(self):
        """Get current order book state"""
        return self.order_book