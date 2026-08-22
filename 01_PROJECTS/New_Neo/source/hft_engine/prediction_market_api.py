"""
Prediction Market API Client
Automatically fetches prediction market targets from public APIs
"""
import aiohttp
import asyncio
from datetime import datetime
import logging
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionMarketAPI:
    def __init__(self):
        self.api_source = config.PREDICTION_MARKET_API
        self.api_urls = {
            'sequence': config.SEQUENCE_API_URL,
            'vezta': config.VEZTA_API_URL,
            'polymarket': config.POLYMARKET_API_URL,
            'kalshi': config.KALSHI_API_URL,
            'coinmarketcap': 'https://pro-api.coinmarketcap.com/public-api/v1/simple/price',
            'terminalfeed': 'https://terminalfeed.io/api/btc-price',
            'sintra': 'https://sintra.fi/api/btcusd'
        }
        self.last_target = None
        self.last_fetch_time = None
    
    async def fetch_btc_target(self):
        """Fetch current BTC prediction market target from public API"""
        try:
            # Try CoinMarketCap keyless API first (most reliable)
            target = await self.fetch_coinmarketcap_target()
            if target:
                return target
            
            # Try TerminalFeed
            target = await self.fetch_terminalfeed_target()
            if target:
                return target
            
            # Try Sintra
            target = await self.fetch_sintra_target()
            if target:
                return target
            
            # Fallback to prediction market APIs
            if self.api_source == 'sequence':
                return await self.fetch_sequence_target()
            elif self.api_source == 'vezta':
                return await self.fetch_vezta_target()
            elif self.api_source == 'polymarket':
                return await self.fetch_polymarket_target()
            elif self.api_source == 'kalshi':
                return await self.fetch_kalshi_target()
            else:
                logger.warning(f"Unknown API source: {self.api_source}")
                return None
        except Exception as e:
            logger.error(f"Error fetching prediction market target: {e}")
            return None
    
    async def fetch_sequence_target(self):
        """Fetch BTC target from Sequence API (unified Polymarket/Kalshi)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for BTC markets
                params = {
                    'q': 'BTC 15 minute',
                    'active': 'true',
                    'limit': 10
                }
                
                async with session.get(self.api_urls['sequence'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Parse the response for BTC 15-minute markets
                        if 'results' in data:
                            for market in data['results']:
                                if 'BTC' in market.get('question', '').upper() and '15' in market.get('question', ''):
                                    # Extract target price from market rules/question
                                    target = self.extract_target_from_question(market.get('question', ''))
                                    if target:
                                        logger.info(f"Sequence API fetched target: ${target}")
                                        return target
                        
                        logger.warning("No BTC 15-minute market found in Sequence API")
                        return None
                    else:
                        logger.error(f"Sequence API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching from Sequence API: {e}")
            return None
    
    async def fetch_vezta_target(self):
        """Fetch BTC target from Vezta API (aggregated prediction markets)"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get crypto markets
                params = {
                    'category': 'crypto',
                    'limit': 20
                }
                
                async with session.get(f"{self.api_urls['vezta']}/crypto/latest", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Look for BTC 15-minute markets
                        if 'markets' in data:
                            for market in data['markets']:
                                if 'BTC' in market.get('question', '').upper():
                                    target = self.extract_target_from_question(market.get('question', ''))
                                    if target:
                                        logger.info(f"Vezta API fetched target: ${target}")
                                        return target
                        
                        logger.warning("No BTC market found in Vezta API")
                        return None
                    else:
                        logger.error(f"Vezta API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching from Vezta API: {e}")
            return None
    
    async def fetch_polymarket_target(self):
        """Fetch BTC target from Polymarket API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for BTC markets
                params = {
                    'query': 'BTC 15',
                    'limit': 10
                }
                
                async with session.get(f"{self.api_urls['polymarket']}/markets", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data:
                            for market in data['data']:
                                question = market.get('question', '')
                                if 'BTC' in question.upper() and '15' in question:
                                    target = self.extract_target_from_question(question)
                                    if target:
                                        logger.info(f"Polymarket API fetched target: ${target}")
                                        return target
                        
                        logger.warning("No BTC 15-minute market found in Polymarket API")
                        return None
                    else:
                        logger.error(f"Polymarket API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching from Polymarket API: {e}")
            return None
    
    async def fetch_kalshi_target(self):
        """Fetch BTC target from Kalshi API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Search for BTC markets
                params = {
                    'limit': 20
                }
                
                async with session.get(f"{self.api_urls['kalshi']}/events", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'events' in data:
                            for event in data['events']:
                                if 'BTC' in event.get('title', '').upper():
                                    # Get markets for this event
                                    event_id = event.get('event_id')
                                    markets_response = await session.get(
                                        f"{self.api_urls['kalshi']}/markets",
                                        params={'event_id': event_id}
                                    )
                                    if markets_response.status == 200:
                                        markets_data = await markets_response.json()
                                        if 'markets' in markets_data:
                                            for market in markets_data['markets']:
                                                if '15' in market.get('title', ''):
                                                    target = self.extract_target_from_question(market.get('title', ''))
                                                    if target:
                                                        logger.info(f"Kalshi API fetched target: ${target}")
                                                        return target
                        
                        logger.warning("No BTC 15-minute market found in Kalshi API")
                        return None
                    else:
                        logger.error(f"Kalshi API returned status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching from Kalshi API: {e}")
            return None
    
    async def fetch_coinmarketcap_target(self):
        """Fetch BTC price from CoinMarketCap keyless API (no auth required)"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'ids': '1',  # BTC ID
                    'convert': 'USD'
                }
                
                async with session.get(self.api_urls['coinmarketcap'], params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data and '1' in data['data']:
                            btc_data = data['data']['1']
                            price = btc_data.get('quote', {}).get('USD', {}).get('price')
                            if price:
                                logger.info(f"CoinMarketCap API fetched price: ${price}")
                                return float(price)
                    
                    logger.warning("No BTC price found in CoinMarketCap API")
                    return None
        except Exception as e:
            logger.error(f"Error fetching from CoinMarketCap API: {e}")
            return None
    
    async def fetch_terminalfeed_target(self):
        """Fetch BTC price from TerminalFeed API (no auth required)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_urls['terminalfeed']) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'price' in data:
                            price = data['price']
                            logger.info(f"TerminalFeed API fetched price: ${price}")
                            return float(price)
                    
                    logger.warning("No BTC price found in TerminalFeed API")
                    return None
        except Exception as e:
            logger.error(f"Error fetching from TerminalFeed API: {e}")
            return None
    
    async def fetch_sintra_target(self):
        """Fetch BTC price from Sintra API (no auth required)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.api_urls['sintra']) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'price' in data:
                            price = data['price']
                            logger.info(f"Sintra API fetched price: ${price}")
                            return float(price)
                    
                    logger.warning("No BTC price found in Sintra API")
                    return None
        except Exception as e:
            logger.error(f"Error fetching from Sintra API: {e}")
            return None
    
    def extract_target_from_question(self, question):
        """Extract target price from prediction market question"""
        import re
        
        # Common patterns for price targets in questions
        patterns = [
            r'\$?(\d{4,5}(?:\.\d{2})?)',  # $63500 or 63500.00
            r'(\d{4,5}(?:\.\d{2})?)\s*USD',  # 63500.00 USD
            r'(\d{4,5}(?:\.\d{2})?)\s*USDT',  # 63500.00 USDT
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, question)
            if matches:
                try:
                    # Return the first numeric match as target
                    target = float(matches[0])
                    # Validate it's a reasonable BTC price (between 10k and 200k)
                    if 10000 < target < 200000:
                        return target
                except ValueError:
                    continue
        
        return None
    
    async def get_target_with_fallback(self):
        """Get target with multiple API fallbacks"""
        target = await self.fetch_btc_target()
        
        if target:
            self.last_target = target
            self.last_fetch_time = datetime.utcnow()
            return target
        
        # Fallback to other APIs if primary fails
        logger.warning(f"Primary API ({self.api_source}) failed, trying fallbacks")
        
        fallback_apis = ['coinmarketcap', 'terminalfeed', 'sintra', 'sequence', 'vezta', 'polymarket', 'kalshi']
        
        for api in fallback_apis:
            if api == 'coinmarketcap':
                target = await self.fetch_coinmarketcap_target()
            elif api == 'terminalfeed':
                target = await self.fetch_terminalfeed_target()
            elif api == 'sintra':
                target = await self.fetch_sintra_target()
            elif api == 'sequence':
                target = await self.fetch_sequence_target()
            elif api == 'vezta':
                target = await self.fetch_vezta_target()
            elif api == 'polymarket':
                target = await self.fetch_polymarket_target()
            elif api == 'kalshi':
                target = await self.fetch_kalshi_target()
            
            if target:
                self.last_target = target
                self.last_fetch_time = datetime.utcnow()
                logger.info(f"Successfully fetched target from fallback API: {api}")
                return target
        
        logger.error("All APIs failed")
        return None
    
    async def continuous_target_fetch(self, callback, interval=60):
        """Continuously fetch targets and call callback function"""
        while True:
            try:
                target = await self.get_target_with_fallback()
                if target:
                    await callback(target)
                else:
                    logger.warning("Failed to fetch target, will retry")
                
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in continuous target fetch: {e}")
                await asyncio.sleep(interval)