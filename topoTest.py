#! /usr/bin/env python
import logging

from db import db

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%b/%d/%Y %H:%M:%S %Z', level=logging.INFO)

db = db(url="http://127.0.0.1:7474", username="neo4j", pwd="popeye", logger=logger)

res = db.getGraph2()
logger.info(res)
