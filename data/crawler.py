from data.misc.misc import CoinType, TimeRange


class SocialMediaCrawler(object):
    def collect_posts(self, coin: CoinType, time_range: TimeRange, limit: int):
        pass


class MarketPriceCrawler(object):
    def collect_prices(self, coin: CoinType, time_range: TimeRange, resolution: str):
        pass
