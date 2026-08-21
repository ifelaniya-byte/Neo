"""
PROJECT APEX: DEEP INTERNET RESEARCH INTEGRATION
Enables the agent swarm to conduct deep research across the internet.
Connects to academic papers, documentation, forums, and other sources.
"""

import time
import json
import asyncio
import aiohttp
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

class ResearchSource(Enum):
    """Types of research sources."""
    ACADEMIC_PAPERS = "ACADEMIC_PAPERS"
    DOCUMENTATION = "DOCUMENTATION"
    FORUMS = "FORUMS"
    BLOGS = "BLOGS"
    REPOSITORIES = "REPOSITORIES"
    NEWS = "NEWS"
    ENCYCLOPEDIA = "ENCYCLOPEDIA"
    DATABASES = "DATABASES"

class SearchEngine(Enum):
    """Search engines for research."""
    GOOGLE_SCHOLAR = "GOOGLE_SCHOLAR"
    ARXIV = "ARXIV"
    SEMANTIC_SCHOLAR = "SEMANTIC_SCHOLAR"
    PUBMED = "PUBMED"
    GITHUB = "GITHUB"
    STACK_OVERFLOW = "STACK_OVERFLOW"
    WIKIPEDIA = "WIKIPEDIA"
    BING = "BING"
    DUCKDUCKGO = "DUCKDUCKGO"

@dataclass
class ResearchSourceConfig:
    """Configuration for a research source."""
    source_type: ResearchSource
    base_url: str
    search_endpoint: str
    api_key: Optional[str]
    rate_limit: int  # requests per minute
    reliability: float
    last_accessed: str
    access_count: int
    
    def to_dict(self):
        return self.__dict__

@dataclass
class SearchResult:
    """Result from internet research."""
    source: SearchEngine
    url: str
    title: str
    content: str
    relevance_score: float
    citation_count: int
    publication_date: str
    authors: List[str]
    abstract: str
    metadata: Dict
    
    def to_dict(self):
        return self.__dict__

class DeepInternetResearch:
    """
    Deep internet research integration for agent swarm.
    Connects to multiple sources for comprehensive research.
    """
    
    def __init__(self, api_keys: Dict[str, str] = None):
        self.api_keys = api_keys or {}
        self.source_configs = self._initialize_sources()
        self.search_history = []
        self.cache = {}
        self.session = requests.Session()
        self.async_session = None
        
    def _initialize_sources(self) -> Dict[str, ResearchSourceConfig]:
        """Initialize research source configurations."""
        return {
            'arxiv': ResearchSourceConfig(
                source_type=ResearchSource.ACADEMIC_PAPERS,
                base_url="https://arxiv.org",
                search_endpoint="/api/query",
                api_key=None,
                rate_limit=10,
                reliability=0.95,
                last_accessed="",
                access_count=0
            ),
            'semantic_scholar': ResearchSourceConfig(
                source_type=ResearchSource.ACADEMIC_PAPERS,
                base_url="https://api.semanticscholar.org",
                search_endpoint="/graph",
                api_key=self.api_keys.get('semantic_scholar'),
                rate_limit=5,
                reliability=0.90,
                last_accessed="",
                access_count=0
            ),
            'github': ResearchSourceConfig(
                source_type=ResearchSource.REPOSITORIES,
                base_url="https://api.github.com",
                search_endpoint="/search",
                api_key=self.api_keys.get('github'),
                rate_limit=30,
                reliability=0.92,
                last_accessed="",
                access_count=0
            ),
            'stack_overflow': ResearchSourceConfig(
                source_type=ResearchSource.FORUMS,
                base_url="https://api.stackexchange.com",
                search_endpoint="/2.3/search/advanced",
                api_key=self.api_keys.get('stack_overflow'),
                rate_limit=30,
                reliability=0.88,
                last_accessed="",
                access_count=0
            ),
            'wikipedia': ResearchSourceConfig(
                source_type=ResearchSource.ENCYCLOPEDIA,
                base_url="https://en.wikipedia.org",
                search_endpoint="/w/api.php",
                api_key=None,
                rate_limit=30,
                reliability=0.85,
                last_accessed="",
                access_count=0
            )
        }
    
    async def search_academic_papers(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search academic papers across multiple sources."""
        results = []
        
        # Search arXiv
        arxiv_results = await self.search_arxiv(query, max_results // 2)
        results.extend(arxiv_results)
        
        # Search Semantic Scholar
        semantic_results = await self.search_semantic_scholar(query, max_results // 2)
        results.extend(semantic_results)
        
        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results[:max_results]
    
    async def search_arxiv(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search arXiv for academic papers."""
        config = self.source_configs['arxiv']
        
        try:
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(config.base_url + config.search_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for entry in data.get('entries', []):
                            result = SearchResult(
                                source=SearchEngine.ARXIV,
                                url=entry.get('id', ''),
                                title=entry.get('title', ''),
                                content=entry.get('summary', ''),
                                relevance_score=self._calculate_relevance(query, entry.get('title', '')),
                                citation_count=0,
                                publication_date=entry.get('published', ''),
                                authors=entry.get('authors', []),
                                abstract=entry.get('summary', ''),
                                metadata={'source': 'arxiv', 'entry': entry}
                            )
                            results.append(result)
                        
                        return results
        except Exception as e:
            print(f"[RESEARCH] Error searching arXiv: {e}")
        
        return []
    
    async def search_semantic_scholar(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search Semantic Scholar for academic papers."""
        config = self.source_configs['semantic_scholar']
        
        if not config.api_key:
            print("[RESEARCH] Semantic Scholar API key not provided")
            return []
        
        try:
            params = {
                'query': query,
                'limit': max_results,
                'fields': 'title,abstract,authors,url,citationCount,publicationDate'
            }
            
            headers = {'x-api-key': config.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(config.base_url + config.search_endpoint, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for paper in data.get('data', {}):
                            result = SearchResult(
                                source=SearchEngine.SEMANTIC_SCHOLAR,
                                url=paper.get('url', ''),
                                title=paper.get('title', ''),
                                content=paper.get('abstract', ''),
                                relevance_score=self._calculate_relevance(query, paper.get('title', '')),
                                citation_count=paper.get('citationCount', 0),
                                publication_date=paper.get('publicationDate', ''),
                                authors=[a.get('name', '') for a in paper.get('authors', [])],
                                abstract=paper.get('abstract', ''),
                                metadata={'source': 'semantic_scholar', 'paper': paper}
                            )
                            results.append(result)
                        
                        return results
        except Exception as e:
            print(f"[RESEARCH] Error searching Semantic Scholar: {e}")
        
        return []
    
    async def search_documentation(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search technical documentation."""
        results = []
        
        # Search GitHub repositories
        github_results = await self.search_github(query, max_results // 2)
        results.extend(github_results)
        
        # Search Stack Overflow
        stackoverflow_results = await self.search_stack_overflow(query, max_results // 2)
        results.extend(stackoverflow_results)
        
        results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return results[:max_results]
    
    async def search_github(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search GitHub repositories."""
        config = self.source_configs['github']
        
        try:
            params = {
                'q': query,
                'per_page': max_results,
                'sort': 'stars'
            }
            
            headers = {}
            if config.api_key:
                headers['Authorization'] = f"token {config.api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(config.base_url + config.search_endpoint, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('items', []):
                            result = SearchResult(
                                source=SearchEngine.GITHUB,
                                url=item.get('html_url', ''),
                                title=item.get('name', ''),
                                content=item.get('description', ''),
                                relevance_score=self._calculate_relevance(query, item.get('name', '')),
                                citation_count=item.get('stargazers_count', 0),
                                publication_date=item.get('created_at', ''),
                                authors=[],
                                abstract=item.get('description', ''),
                                metadata={'source': 'github', 'repository': item}
                            )
                            results.append(result)
                        
                        return results
        except Exception as e:
            print(f"[RESEARCH] Error searching GitHub: {e}")
        
        return []
    
    async def search_stack_overflow(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search Stack Overflow for technical solutions."""
        config = self.source_configs['stack_overflow']
        
        try:
            params = {
                'order': 'desc',
                'sort': 'votes',
                'q': query,
                'site': 'stackoverflow',
                'pagesize': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(config.base_url + config.search_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('items', []):
                            result = SearchResult(
                                source=SearchEngine.STACK_OVERFLOW,
                                url=item.get('link', ''),
                                title=item.get('title', ''),
                                content=item.get('body', ''),
                                relevance_score=self._calculate_relevance(query, item.get('title', '')),
                                citation_count=item.get('score', 0),
                                publication_date=item.get('creation_date', ''),
                                authors=[item.get('owner', {}).get('display_name', '')],
                                abstract=item.get('body', ''),
                                metadata={'source': 'stackoverflow', 'question': item}
                            )
                            results.append(result)
                        
                        return results
        except Exception as e:
            print(f"[RESEARCH] Error searching Stack Overflow: {e}")
        
        return []
    
    async def search_wikipedia(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search Wikipedia for general information."""
        config = self.source_configs['wikipedia']
        
        try:
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(config.base_url + config.search_endpoint, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        for item in data.get('query', {}).get('search', []):
                            # Get page content
                            page_content = await self.get_wikipedia_page(item['title'])
                            
                            result = SearchResult(
                                source=SearchEngine.WIKIPEDIA,
                                url=f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                                title=item['title'],
                                content=page_content,
                                relevance_score=self._calculate_relevance(query, item['title']),
                                citation_count=0,
                                publication_date='',
                                authors=[],
                                abstract=page_content[:500],
                                metadata={'source': 'wikipedia', 'page': item}
                            )
                            results.append(result)
                        
                        return results
        except Exception as e:
            print(f"[RESEARCH] Error searching Wikipedia: {e}")
        
        return []
    
    async def get_wikipedia_page(self, title: str) -> str:
        """Get full content of a Wikipedia page."""
        try:
            params = {
                'action': 'query',
                'prop': 'extracts',
                'explaintext': 'true',
                'titles': title,
                'format': 'json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get('query', {}).get('pages', {})
                        if pages:
                            page_id = next(iter(pages))
                            return pages[page_id].get('extract', '')
        except Exception as e:
            print(f"[RESEARCH] Error getting Wikipedia page: {e}")
        
        return ""
    
    def _calculate_relevance(self, query: str, title: str) -> float:
        """Calculate relevance score based on query and title."""
        query_words = set(query.lower().split())
        title_words = set(title.lower().split())
        
        if not query_words or not title_words:
            return 0.0
        
        intersection = query_words & title_words
        union = query_words | title_words
        
        jaccard_similarity = len(intersection) / len(union) if union else 0.0
        
        return jaccard_similarity
    
    async def comprehensive_search(self, query: str, sources: List[SearchEngine], 
                                  max_results_per_source: int = 5) -> List[SearchResult]:
        """Perform comprehensive search across multiple sources."""
        all_results = []
        
        # Create async tasks for each source
        tasks = []
        
        for source in sources:
            if source == SearchEngine.ARXIV:
                tasks.append(self.search_arxiv(query, max_results_per_source))
            elif source == SearchEngine.SEMANTIC_SCHOLAR:
                tasks.append(self.search_semantic_scholar(query, max_results_per_source))
            elif source == SearchEngine.GITHUB:
                tasks.append(self.search_github(query, max_results_per_source))
            elif source == SearchEngine.STACK_OVERFLOW:
                tasks.append(self.search_stack_overflow(query, max_results_per_source))
            elif source == SearchEngine.WIKIPEDIA:
                tasks.append(self.search_wikipedia(query, max_results_per_source))
        
        # Execute all searches concurrently
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result_list in results_lists:
            if isinstance(result_list, list):
                all_results.extend(result_list)
        
        # Sort by relevance
        all_results.sort(key=lambda r: r.relevance_score, reverse=True)
        
        return all_results
    
    def extract_content(self, url: str) -> str:
        """Extract and clean content from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Get text content
                text = soup.get_text(separator=' ')
                
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                
                return text
        except Exception as e:
            print(f"[RESEARCH] Error extracting content from {url}: {e}")
        
        return ""
    
    def get_search_statistics(self) -> Dict:
        """Get statistics about search operations."""
        return {
            'total_searches': len(self.search_history),
            'sources_used': list(self.source_configs.keys()),
            'cache_size': len(self.cache),
            'avg_relevance': sum(r.relevance_score for r in self.search_history) / len(self.search_history) if self.search_history else 0.0
        }