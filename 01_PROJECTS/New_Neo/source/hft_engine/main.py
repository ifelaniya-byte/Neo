"""
Main entry point for HFT Microstructure Prediction Engine
"""
import asyncio
import sys
import logging
from cli_interface import CLIInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hft_engine.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    # Configuration
    product_id = "BTC-USD"
    window_duration = 900  # 15 minutes in seconds
    
    logger.info("Starting HFT Microstructure Prediction Engine")
    logger.info(f"Product: {product_id}")
    logger.info(f"Window Duration: {window_duration} seconds")
    
    try:
        cli = CLIInterface(product_id, window_duration)
        await cli.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program terminated by user")
        sys.exit(0)