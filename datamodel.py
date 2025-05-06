from dataclasses import dataclass

@dataclass
class PillarPage:
    def __init__(self, supporting_pages: list[str] = [], supporting_blog_topics: list[str] = []):
        self.supporting_pages = supporting_pages
        self.supporting_blog_topics = supporting_blog_topics

    def __repr__(self):
        return (f"PillarPage(supporting_pages={self.supporting_pages}, "
                f"supporting_blog_topics={self.supporting_blog_topics})")
    
@dataclass
class TopicalMap:
    def __init__(self, money_keyword: str):
        self.money_keyword = money_keyword
        self.pillar_pages : list[PillarPage] = []

    def add_topic(self, topic : PillarPage):
        self.pillar_pages.append(topic)

    def __repr__(self):
        return f"TopicalMap(money_keyword={self.money_keyword}, pillar_pages={self.pillar_pages})"

    