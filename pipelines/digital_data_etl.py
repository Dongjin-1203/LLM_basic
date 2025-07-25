# libraries
from zenml import pipeline

# module
from steps.etl import crawl_links, get_or_create_user

@pipeline
def digital_data_etl(user_full_name: str, links: list[str]):
    """Pipeline to extract, transform, and load digital data."""
    user = get_or_create_user(user_full_name)
    last_step = crawl_links(user=user, links=links)

    return last_step.invocation_id