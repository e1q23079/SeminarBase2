from bs4 import BeautifulSoup
import markdown
import bleach


class Doc:
    def __init__(self, content: str):
        '''
        ドキュメントを解析してレクチャーを抽出する
        '''
        self.lectures: list = []

        temp_content = None
        title = "無題"
        now_chapter = 1

        html_content = markdown.markdown(
            content,
            extensions=['extra', 'codehilite', 'nl2br', 'attr_list']
        )

        parse = BeautifulSoup(html_content, 'html.parser')

        for element in parse.contents:
            if element.name == 'h1':
                if temp_content is not None:
                    self.lectures.append(
                        {
                            'title': title,
                            'content': temp_content,
                            'chapter': now_chapter
                        }
                    )
                    self.lectures[now_chapter-1]['prev'] = now_chapter - 1 if now_chapter > 1 else None  # noqa: E501
                    self.lectures[now_chapter-1]['next'] = now_chapter + 1  # noqa: E501
                    now_chapter += 1
                    temp_content = None
                title = element.get_text()
                temp_content = ""
            else:
                if temp_content is not None:
                    temp_content += str(element).strip()
                else:
                    temp_content = str(element).strip()

        if temp_content is not None:
            self.lectures.append(
                {
                    'title': title,
                    'content': temp_content,
                    'chapter': now_chapter
                }
            )
            self.lectures[now_chapter-1]['prev'] = now_chapter - 1 if now_chapter > 1 else None  # noqa: E501
            self.lectures[now_chapter-1]['next'] = None  # noqa: E501

        for lecture in self.lectures:
            lecture['content'] = bleach.clean(
                lecture['content'],
                tags=[
                    'h1',
                    'h2',
                    'h3',
                    'h4',
                    'h5',
                    'h6',
                    'p',
                    'br',
                    'strong',
                    'em',
                    'ul',
                    'ol',
                    'li',
                    'code',
                    'pre',
                    'table',
                    'thead',
                    'tbody',
                    'tr',
                    'th',
                    'td',
                    'img',
                    'a'
                ],
                attributes={
                    'a':
                        [
                            'href',
                            'title'
                        ],
                    'img':
                        [
                            'src',
                            'alt'
                        ]
                    },
                strip=True
            )

    def get_lectures(self):
        '''
        ドキュメントからレクチャーのリストを取得する
        '''
        return self.lectures

    def get_lecture_titles(self):
        '''
        ドキュメントからレクチャーのタイトル・チャプター番号のリストを取得する
        '''
        return [
            {
                'title': lecture['title'],
                'chapter': lecture['chapter']
            } for lecture in self.lectures
        ]

    def get_lecture(self, page: int):
        '''
        ドキュメントからチャプター番号でレクチャーを取得する
        '''
        for lecture in self.lectures:
            if lecture['chapter'] == page:
                return lecture
        return None

    def get_lecture_count(self):
        '''
        ドキュメントからレクチャーの数を取得する
        '''
        return len(self.lectures)
