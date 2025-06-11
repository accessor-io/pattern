from .logger import configure_puzzle_logger

def inspect_cache():
    logger = configure_puzzle_logger()
    from btc_puzzle_solver.core import Puzzle66Solver
    cache_info = Puzzle66Solver._apply_transformation.cache_info()
    logger.info(f"Cache stats: {cache_info}")
    return cache_info 