from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Set

from mr_apollo_2n.model.url_last_update import UrlLastUpdateModel


class IUrlLastUpdateRepo(ABC):
	@abstractmethod
	def save_or_update(self, url_last_update: UrlLastUpdateModel) -> None:
		"""
		Save or update a UrlLastUpdateModel instance to the DB.

		Parameters
		----------
		url_last_update: UrlLastUpdateModel
				The UrlLastUpdateModel instance to save or update.
		"""
		pass

	@abstractmethod
	def find_by_url(self, url: str) -> Optional[UrlLastUpdateModel]:
		"""
		Find a UrlLastUpdateModel instance by its URL.

		Parameters
		----------
		url: str
				The URL to find.

		Returns
		-------
		Optional[UrlLastUpdateModel]
				The UrlLastUpdateModel instance if it exists, None otherwise.
		"""
		pass

	@abstractmethod
	def save_or_update_batch(self, url_last_updates: Set[UrlLastUpdateModel]) -> None:
		"""
		Save or update a set of UrlLastUpdateModel instances to the database.

		Parameters
		----------
		url_last_updates: Set[UrlLastUpdateModel]
				The set of UrlLastUpdateModel instances to save or update.
		"""
		pass

	@abstractmethod
	def check_urls_to_process(self, urls: Set[str], last_update: datetime) -> Set[str]:
		"""
		Get the URLs that need to be processed.

		Parameters
		----------
		urls: Set[str]
				The set of URLs to check.
		last_update: datetime
				The last update date.
		"""
		pass

	@abstractmethod
	def check_url_to_process(self, url: str, last_update: datetime) -> bool:
		"""
		Get the URLs that need to be processed.

		Parameters
		----------
		url: str
				The URL to check.
		last_update: datetime
				The last update date.
		"""
		pass
