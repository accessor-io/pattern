from functools import lru_cache
import pickle
from pathlib import Path
import atexit
from .logger import configure_puzzle_logger

logger = configure_puzzle_logger()
CACHE_DIR = Path.home() / '.btc_puzzle_cache'
CACHE_FILE = CACHE_DIR / 'transformation_cache.pkl'

def _get_cache() -> lru_cache:
    from ..core import Puzzle66Solver
    return Puzzle66Solver._apply_transformation

def persist_cache():
    """Save cache to disk automatically on exit"""
    cache = _get_cache()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with CACHE_FILE.open('wb') as f:
        pickle.dump({
            'cache': cache.cache_info(),
            'data': dict(cache._cache.items())
        }, f)
    logger.debug(f"Persisted cache with {cache.cache_info().currsize} entries")

def load_cache():
    """Load cache from disk at startup"""
    if CACHE_FILE.exists():
        try:
            with CACHE_FILE.open('rb') as f:
                data = pickle.load(f)
                cache = _get_cache()
                cache.cache_clear()
                cache._cache.update(data['data'])
                logger.info(f"Loaded cache with {len(data['data'])} entries")
        except Exception as e:
            logger.error(f"Cache load failed: {str(e)}")
            CACHE_FILE.unlink()

def validate_cache():
    """Ensure cache integrity"""
    cache = _get_cache()
    if hasattr(cache, '_cache'):
        return len(cache._cache) == cache.cache_info().currsize
    return False

# Register automatic persistence
atexit.register(persist_cache) 