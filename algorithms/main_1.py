#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from audio_processing_system.core.engine import AudioProcessingApplication

def parse_args():
    parser = argparse.ArgumentParser(
        description='Audio Processing System'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--sample-rate',
        type=int,
        default=44100,
        help='Sample rate (default: 44100)'
    )
    parser.add_argument(
        '--buffer-size',
        type=int,
        default=1024,
        help='Buffer size (default: 1024)'
    )
    return parser.parse_args()

def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Initialize application
        app = AudioProcessingApplication(
            sample_rate=args.sample_rate,
            buffer_size=args.buffer_size
        )
        
        # Load configuration if provided
        if args.config:
            app.load_config(args.config)
            
        # Initialize and run
        app.initialize()
        app.run()
        
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'app' in locals():
            app.shutdown()

if __name__ == '__main__':
    main() 