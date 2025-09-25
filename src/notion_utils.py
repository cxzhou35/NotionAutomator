import logging
import structlog
from typing import List
from notion_client import Client

from .base_utils import DotDict

logger = structlog.wrap_logger(
    logging.getLogger("notion-client"),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
)

def init_notion_client(notion_token, log_level=logging.INFO):
    """Initializes a notion client."""
    try:
        client = Client(auth=notion_token, logger=logger, log_level=log_level)
        return client
    except Exception as e:
        logger.error(f"Failed to initialize the notion client: {e}")
        breakpoint()


def query_db(client: Client, database_id: str, filter: DotDict = None):
    """Queries the database and returns the metadata of the pages."""
    results = client.databases.query(
        **{
            "database_id": database_id,
            "filter": filter
        }
    ).get("results")

    num_pages = len(results)
    db_meta = [DotDict(result) for result in results]
    return db_meta, num_pages

def query_db_props(db_meta: List[DotDict], target_props: List[str]) -> DotDict:
    """Queries the properties from the metadata of the pages."""
    queried_results = DotDict()

    for object in db_meta:
        page_id = object['id']
        properties = object['properties']
        all_query_keys = properties.keys()
        object_meta = DotDict()

        for prop in target_props:
            if prop not in all_query_keys:
                raise ValueError(f"Property {prop} not found in the database.")
            else:
                prop_type = properties[prop]['type']
                prop_value = properties[prop][prop_type]
                object_meta[prop] = prop_value

        queried_results[page_id] = object_meta

    return queried_results


def update_db_pages(client: Client, target_prop_metas: DotDict, page_ids: List[str]) -> None:
    """Updates the specific pages with the given properties."""
    try:
        for page_id in page_ids:
            client.pages.update(
                page_id=page_id,
                properties=target_prop_metas,
            )
    except Exception as e:
        logger.error(f"Failed to update the pages: {e}")
        breakpoint()


def create_db_pages(database_id: str, client: Client, target_prop_metas: DotDict) -> None:
    """Creates a new page in the database with the given properties."""
    try:
        client.pages.create(
            parent={"database_id": database_id},
            properties=target_prop_metas,
        )
        logger.info(f"Created the page successfully.")
    except Exception as e:
        logger.error(f"Failed to create the page: {e}")
        breakpoint()


def fetch_page_ids(pages: DotDict) -> List[str]:
    """Fetches the page IDs from the queried pages."""
    assert len(pages) != 0, "The target page is not found."
    page_ids = [page.id for page in pages]
    return page_ids
