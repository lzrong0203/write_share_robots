from django.core.management.base import BaseCommand
from stock_app.ptt_crawler import crawl_ptt_stock


class Command(BaseCommand):
    help = 'Crawl PTT Stock board posts and upload to Firebase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            default=1,
            help='Number of pages to crawl'
        )

    def handle(self, *args, **options):
        pages = options['pages']
        self.stdout.write(self.style.SUCCESS(f'Starting to crawl {pages} page(s) from PTT Stock board...'))
        
        try:
            uploaded_count = crawl_ptt_stock(pages)
            self.stdout.write(self.style.SUCCESS(f'Successfully uploaded {uploaded_count} posts to Firebase'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}')) 