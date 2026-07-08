#!/usr/bin/env python3
"""
MP3 Player - Main Entry Point

Usage:
    python claude/main.py [--mpd-host HOST] [--mpd-port PORT]
"""
import argparse
import logging
import sys

from claude.app import MP3PlayerApp


def setup_logging(level=logging.INFO):
    """Configure logging for the application"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('/tmp/mp3player.log')
        ]
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='MP3 Player Interface')
    parser.add_argument(
        '--mpd-host',
        default='localhost',
        help='MPD server host (default: localhost)'
    )
    parser.add_argument(
        '--mpd-port',
        type=int,
        default=6600,
        help='MPD server port (default: 6600)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = getattr(logging, args.log_level)
    setup_logging(log_level)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("MP3 Player Starting")
    logger.info(f"MPD Server: {args.mpd_host}:{args.mpd_port}")
    logger.info("=" * 60)

    try:
        # Create and start application
        app = MP3PlayerApp(mpd_host=args.mpd_host, mpd_port=args.mpd_port)
        app.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
