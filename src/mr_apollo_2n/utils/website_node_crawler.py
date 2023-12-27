import json
import logging
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime
from time import sleep
from typing import Dict, List, Literal, Optional
from urllib.parse import urljoin

from mr_apollo_2n.model.website_node_model import WebsiteNodeModel
from mr_apollo_2n.utils.base_class import BaseClass
from mr_apollo_2n.utils.request_session_utils import RequestSession
from mr_apollo_2n.utils.utils import build_domain_name


class WebsiteNodeCrawler(BaseClass):
	def __init__(
		self,
		home_url: str,
		request_headers: Optional[str] = None,
		sleep_time: Optional[float] = 2.0,
		processed_by_type: Optional[Literal["manual", "scheduled"]] = "manual",
		processed_by: Optional[str] = None,
		processed_at: Optional[datetime] = None,
		request_data=None,
		method: Optional[str] = "GET",
		allow_redirects: Optional[bool] = True,
		robots_resource: Optional[str] = "robots.txt",
	):
		"""
		Reads the sitemap and publishes the urls to the topic.

		Parameters
		----------
		home_url : str
				The Home URL of the website.
		request_headers : Optional[str], optional
				The request headers to use (default is None).
		sleep_time : int, optional
				The sleep time between requests (default is 5).
		processed_by : Optional[str], optional
				The name of the processor (default is None).
		processed_at : Optional[datetime], optional
				The time of processing (default is datetime.now()).
		request_data : Any, optional
				The request data to use (default is None).
		method : Optional[str], optional
				The request method to use (default is "GET").
		robots_resource : Optional[str], optional
				The URL of the robots.txt file (default is ROBOTS).
		"""
		super().__init__(logger_name=__name__, log_level=logging.INFO)
		if processed_at is None:
			processed_at = datetime.now()
		self.allow_redirects = allow_redirects
		self.home_url = home_url
		if request_headers is None:
			self.request_headers = {}
		elif isinstance(request_headers, str):
			self.request_headers = json.loads(request_headers)
		self.sleep_time = sleep_time if sleep_time is not None else 2.0
		self.processed_by_type = processed_by_type
		if processed_by is None:
			self.processed_by = (
				f"website_node_crawler"
				f"___{build_domain_name(home_url)}"
				f"___{self.processed_by_type}"
				f"___{processed_at.strftime('%Y%m%d_%H%M')}"
			)
		else:
			self.processed_by = processed_by
		self.processed_at = processed_at
		self.request_data = request_data
		self.method = method
		self.robots_resource = robots_resource
		self.session_request = RequestSession(
			self.method,
			self.request_data,
			self.request_headers,
			self.allow_redirects,
		)

	def fetch_and_parse(self, url: str) -> Optional[ET.Element]:
		"""
		Fetch the URL and parse the XML content.

		Parameters
		----------
		url : str
				The URL to fetch and parse.
		"""
		content = self.session_request.exec_request(url)
		if content:
			return ET.fromstring(content)
		return None

	def extract_sitemaps(self) -> Optional[List[str]]:
		"""
		Extracts all the sitemaps listed in a robots.txt file of a given URL.

		Returns
		-------
		List[str]
				A list of sitemap URLs.
		"""
		url = urljoin(self.home_url, self.robots_resource)
		self.logger.info(f"Extracting sitemaps from '{url}'.")
		content = self.session_request.exec_request(url)
		if content:
			lines = content.splitlines()
			sitemaps = [
				line.split(": ", 1)[1]
				for line in lines
				if line.lower().startswith("sitemap:")
			]
			return sitemaps
		else:
			raise Exception(
				f"Failed to retrieve or parse content from {self.robots_resource}"
			)

	def process_all_sitemaps(self) -> Optional[List[WebsiteNodeModel]]:
		"""
		Process all the sitemaps listed in a robots.txt file of a given URL.

		Returns
		-------
		List[WebsiteNodeModel]
				A list of WebsiteNodeModel objects.
		"""
		sitemaps = self.extract_sitemaps()
		if not sitemaps:
			self.logger.warning("No sitemaps found.")
			return None
		else:
			processed_elements = []
			for i, sm in enumerate(sitemaps):
				self.logger.info(
					f"Processing sitemap {i + 1} of {len(sitemaps)}: '{sm}'."
				)
				elements_from_sitemap = self.process_sitemap(sm)
				if elements_from_sitemap:
					processed_elements.extend(elements_from_sitemap)
				else:
					self.logger.warning(f"Failed to process sitemap '{sm}'.")

			self.logger.info(
				f"Total processed elements from all sitemaps: {len(processed_elements)}"
			)
			return processed_elements

	def process_node(self, node: ET.Element) -> Dict:
		data = {}
		for child in node:
			tag = child.tag.split("}")[-1]
			if len(child) > 0:
				data[tag] = self.process_node(child)
			elif child.text:
				data[tag] = child.text  # type: ignore
		return data

	def process_sitemap(self, url: str) -> Optional[List[WebsiteNodeModel]]:
		"""
		Processes a sitemap and returns a list of WebsiteNodeModel objects.

		Parameters
		----------
		url : str
				The URL of the sitemap to process.
		"""
		root = self.fetch_and_parse(url)
		if root is None:
			self.logger.warning(f"Could not fetch or parse sitemap '{url}'.")
			return None

		queue = deque([(url, root)])
		processed_elements = []

		while queue:
			parent_url, current_root = queue.popleft()
			total_enqueued = 0
			total_elements = 0

			for sitemap_node in current_root:
				node_tag = sitemap_node.tag
				if node_tag.endswith("url"):
					url_data = self.process_node(sitemap_node)
					element = WebsiteNodeModel(
						url_data["loc"],
						parent_url,
						"URL",
						url_data.copy(),
						meta={
							"processed_by": self.processed_by,
							"processed_at": self.processed_at,
							"processed_by_type": self.processed_by_type,
							"created_at": datetime.now(),
						},
					)
					processed_elements.append(element)
					total_elements += 1
				elif node_tag.endswith("sitemap"):
					url_data = self.process_node(sitemap_node)
					child_root = self.fetch_and_parse(url_data["loc"])
					if child_root:
						sitemap_element = WebsiteNodeModel(
							url_data["loc"],
							parent_url,
							"SITEMAP",
							url_data.copy(),
							meta={
								"processed_by": self.processed_by,
								"processed_at": self.processed_at,
								"processed_by_type": self.processed_by_type,
								"created_at": datetime.now(),
							},
						)
						processed_elements.append(sitemap_element)
						total_enqueued += 1
						queue.append((url_data["loc"], child_root))
				else:
					self.logger.warning(f"Unknown tag '{node_tag}' in sitemap '{url}'.")

			self.logger.info(
				f"Processed page '{parent_url}', "
				f"total successful elements {total_elements} added, "
				f"and enqueued {total_enqueued} elements."
			)
			sleep(self.sleep_time)

		self.logger.debug(
			f"Total processed elements from sitemap '{url}': {len(processed_elements)}"
		)
		return processed_elements
