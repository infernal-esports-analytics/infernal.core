import os
import sys
import json
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print(logger)

# Load environment
if os.path.exists('dev.env'):
    try:
        with open('dev.env') as f:
            _env = json.load(f)
        os.environ.update(_env)
        logging.info(f'Updated environment with dev.env')
    except Exception as e:
        logging.error(f'Cannot load dev.env due to {e}')