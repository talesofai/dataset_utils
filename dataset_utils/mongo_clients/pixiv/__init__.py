from typing import Union
from dataset_utils.mongo_clients.pixiv.hf_tars import HFTarsClient
from dataset_utils.mongo_clients.mongo_client import MongoDBClient

class PixivDB:
    db_name = "pixiv"

    def __init__(self, mongo_client_or_uri: Union[MongoDBClient, str]):
        self.mongo_client = MongoDBClient(mongo_client_or_uri)
        self.hf_tars = HFTarsClient(self.mongo_client)
