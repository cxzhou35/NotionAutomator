import argparse

from src.config_utils import load_config
from src.notion_utils import init_notion_client, query_db, query_db_props, update_db_pages, fetch_page_ids
from src.handler_utils import HandlerFactory


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/default.yaml",
        help="The path to the config file.",
    )
    return parser.parse_args()

def main():
    args = parse_args()

    cfg = load_config(args.config)
    notion_token, database_id = cfg.NOTION_TOKEN, cfg.DATABASE_ID
    client = init_notion_client(notion_token)
    filters = cfg.filter

    # fetch all pages in the database
    db_meta, num_pages = query_db(client, database_id, filter=filters.all)
    queried_results = query_db_props(db_meta, cfg.target_props)

    # create and use the appropriate database handler
    if hasattr(cfg, 'handler_type'):
        handler = HandlerFactory.create_handler(cfg.handler_type)
    elif hasattr(cfg, 'processor_config'):
        if isinstance(cfg.processor_config, list):
            handler = HandlerFactory.create_multi_handler(cfg.processor_config)
        else:
            handler = HandlerFactory.create_custom_handler(cfg.processor_config)
    else:
        handler = HandlerFactory.create_custom_handler({
            'type': 'sum',
            'properties': cfg.target_props
        })

    # process the data using the handler
    target_metas = handler.process_data(queried_results)

    # fetch the target pages
    target_pages, _ = query_db(client, database_id, filter=filters.target)
    page_ids = fetch_page_ids(target_pages)

    # update the properties of the target pages
    update_db_pages(client, target_metas, page_ids)


if __name__ == "__main__":
    main()
