from datetime import datetime


class UrlLastUpdateModel:
	def __init__(self, url: str, last_update: datetime = None):
		self.url = url
		self.update_dates = last_update if last_update is not None else datetime.now()

	def __str__(self):
		return (
			f"UrlLastUpdate("
			f"url={self.url}, "
			f"update_dates={self.update_dates}"
			f")"
		)

	def __eq__(self, other):
		return self.url == other.url

	def __hash__(self):
		return hash(self.url)
