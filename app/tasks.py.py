from celery import Celery
from .email_extractor import EmailExtractor

celery = Celery(__name__, broker='redis://localhost:6379/0')

@celery.task(bind=True)
def process_extraction(self, url, depth):
    extractor = EmailExtractor()
    extractor.scrape_page(url, max_depth=depth)
    results = {
        'emails': list(extractor.valid_emails),
        'stats': {
            'pages_crawled': len(extractor.visited_urls),
            'valid_emails': len(extractor.valid_emails)
        }
    }
    return results