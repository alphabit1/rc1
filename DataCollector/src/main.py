import os
from os.path import join, dirname
from dotenv import load_dotenv

import Db
import HistoryCollectorManager as HCM

dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

db = Db.Db()
hcm = HCM.HistoryCollectorManager(db)
hcm.start()
