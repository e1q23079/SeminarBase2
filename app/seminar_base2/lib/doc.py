from bs4 import BeautifulSoup

class Doc:
    def __init__(self, content: str):
        '''
        ドキュメントを解析してレクチャーを抽出する
        '''
        self.lectures : list = []
        
        temp_content = None
        now_chapter = 1
        
        parse = BeautifulSoup(content, 'html.parser')
        
        for element in parse.find_all():
            if element.name == 'h1':
                if temp_content:
                    self.lectures.append({'title': title, 'content': temp_content, 'chapter': now_chapter})
                    self.lectures[now_chapter-1]['prev'] = now_chapter - 1 if now_chapter > 1 else None
                    self.lectures[now_chapter-1]['next'] = now_chapter + 1
                    now_chapter += 1
                    temp_content = None
                title = element.get_text()
            else:
                if temp_content is not None:
                    temp_content += str(element)
                else:
                    temp_content = str(element)
                    
        if temp_content:
            self.lectures.append({'title': title, 'content': temp_content, 'chapter': now_chapter})
            self.lectures[now_chapter-1]['prev'] = now_chapter - 1 if now_chapter > 1 else None
            self.lectures[now_chapter-1]['next'] = None
        
    def get_lectures(self):
        '''
        ドキュメントからレクチャーのリストを取得する
        '''
        return self.lectures
    
    def get_lecture_titles(self):
        '''
        ドキュメントからレクチャーのタイトル・チャプター番号のリストを取得する
        '''
        return [{'title': lecture['title'], 'chapter': lecture['chapter']} for lecture in self.lectures]
    
    def get_lecture(self, page: int):
        '''
        ドキュメントからチャプター番号でレクチャーを取得する
        '''
        for lecture in self.lectures:
            if lecture['chapter'] == page:
                return lecture
        return None
