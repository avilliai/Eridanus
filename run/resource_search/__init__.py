dynamic_imports = {
    "run.resource_search.resource_search": [
        "search_book_info", "call_asmr", "call_download_book","call_jm"
    ],
    "run.resource_search.engine_search": ["search_net", "read_html"],
}
function_declarations=[
    {
        "name": "call_jm",
        "description": "jmcomic漫画查询、预览、下载。“验车”是预览的另一种称呼",
        "parameters": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string", "enum": ["preview","download","search"],"description": "预览和下载需要comic_id，搜索需要query_target"
                },
                "comic_id": {
                    "type": "integer",
                    "description": "漫画id。预览和下载时使用"
                },
                "serach_topic": {
                    "type": "string",
                    "description": "搜索关键字"
                }
            },
            "required": [
                "mode"
            ]
        }
    },
    {
                "name": "search_book_info",
                "description": "search book information by book_name or author_name",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "info": {
                            "type": "string",
                            "description": "book_name or author_name"
                        }
                    },
                    "required": [
                        "info"
                    ]
                }
            },
    {
        "name": "call_asmr",
        "description": "向用户发送asmr助眠音频。",
        "parameters": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string", "enum": ["hotest", "random", "latest"], "description": "热门asmr，随机asmr，最新asmr"
                }
            },
            "required": [
                "mode"
            ]

        }
    },
    {
        "name": "call_download_book",
        "description": "从zlibrary下载书籍。",
        "parameters": {
            "type": "object",
            "properties": {
                "book_id": {
                    "type": "string",
                    "description": "书籍的id。"
                },
                "hash": {
                    "type": "string",
                    "description": "书籍的hash。"
                }
            },
            "required": [
                "book_id",
                "hash"
            ]
        }
    },
    {
        "name": "search_net",
        "description": "当用户明确告知上网查或是你无法回答用户问题时，上网查询相关信息并总结(不要管点歌指令或是搜图指令)",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "你认为合适的上网查询的关键词或句子，注意，如果用户想知道当前时间，直接查询‘百度时间’；如果用户告知你要‘深度搜索’某一个内容，在调用此函数后获取到的所有url中选取你觉得合适的url，再调用read_html函数进行网页阅读"
                }
            },
            "required": [
                "query"
            ]
        }
    },
    {
        "name": "read_html",
        "description": "当需要阅读具体网址的内容时，调用此函数",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "需要阅读的url，注意你可以先判断一下这是不是一个合法的url，如果是一个下载链接，你不要阅读"
                }
            },
            "required": [
                "url"
            ]
        }
    },
]