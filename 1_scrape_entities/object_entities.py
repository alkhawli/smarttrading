from typing import TypedDict, List, Optional


class Comment(TypedDict):
    body: str
    score: int


# class PostClass(TypedDict):
#     title: str
#     score: int
#     url: str
#     comments: List[Comment]


class MainStock(TypedDict):
    name: str
    mentions: int
    comments: List[Comment]
    actual_stock_value: Optional[str]


class AllStocks(TypedDict):
    stock_list: List[MainStock]

# {"name": "TSLA",
#  "mentions": 150,
#  "posts": [{"title": "Test",
#             "score": "150",
#             "url": "www.test-url.de",
#             "comments": [{"body": "TSLA is awesome",
#                           "score": 100},
#                          {"body": "TSLA is still awesome",
#                           "score": 80}
#                          ]
#             },
#            {"title": "NEU",
#             "score": "120",
#             "url": "www.url-test.de",
#             "comments": [{"body": "TSLA is shit",
#                           "score": 50},
#                          {"body": "TSLA is still shit",
#                           "score": 50}
#                          ]
#             }
#            ]
#  }
