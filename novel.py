class Novel:
    def __init__(self, title: str, author: str, description: str, type: str = '', count: int = 0, id: int = 0):
        self.id = id
        self.title = title
        self.author = author
        self.type = type
        self.description = description
        self.count = count

    def __str__(self):
        return '标题：' + self.title + '\n' + \
               'ID：' + str(self.id) + '\n' + \
               '字数：' + str(self.count) + '\n' + \
               '类型：' + self.type + '\n' + \
               '作者：' + self.author + '\n' + \
               '简介：' + self.description + '\n'
