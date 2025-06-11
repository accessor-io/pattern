import logging

def configure_puzzle_logger():
    logger = logging.getLogger('BitcoinPuzzleSolver')
    logger.setLevel(logging.DEBUG)
    
    # File handler
    fh = logging.FileHandler('puzzle_solver.log')
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    fh.setFormatter(fh_formatter)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(ch_formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger 