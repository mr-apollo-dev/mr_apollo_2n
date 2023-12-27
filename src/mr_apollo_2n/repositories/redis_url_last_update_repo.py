import logging
from datetime import datetime
from functools import cached_property
from typing import Optional, Set

import redis

from mr_apollo_2n.model.url_last_update import UrlLastUpdateModel
from mr_apollo_2n.repositories.iurl_last_update_repo import IUrlLastUpdateRepo


class RedisUrlLastUpdateRepo(IUrlLastUpdateRepo):
	def __init__(
		self,
		host: Optional[str] = "redis",
		port: Optional[int] = 6379,
		db: Optional[int] = 0,
	):
		self.host = host
		self.port = port
		self.db = db
		self.logger = logging.getLogger(__name__)

	@cached_property
	def redis_client(self):
		self.logger.info(f"Connecting to Redis on '{self.host}:{self.port}'.")
		return redis.StrictRedis(host=self.host, port=self.port, db=self.db)

	def find_by_url(self, url: str) -> Optional[UrlLastUpdateModel]:
		last_update = self.redis_client.get(url)
		return (
			UrlLastUpdateModel(url, datetime.fromisoformat(last_update.decode()))
			if last_update
			else None
		)

	def save_or_update_batch(self, url_last_updates: Set[UrlLastUpdateModel]) -> None:
		for url_last_update in url_last_updates:
			self.save_or_update(url_last_update)

	def check_urls_to_process(self, urls: Set[str], last_update: datetime) -> Set[str]:
		stored_updates = self.redis_client.mget(list(urls))
		to_process = set()
		for url, stored_update in zip(urls, stored_updates):
			if (
				not stored_update
				or datetime.fromisoformat(stored_update.decode()) < last_update
			):
				to_process.add(url)
		return to_process

	def check_url_to_process(self, url: str, last_update: datetime) -> bool:
		stored_update = self.redis_client.get(url)
		return (
			not stored_update
			or datetime.fromisoformat(stored_update.decode()) < last_update
		)

	def save_or_update(self, url_last_update: UrlLastUpdateModel) -> None:
		self.redis_client.set(
			url_last_update.url, url_last_update.update_dates.isoformat()
		)
