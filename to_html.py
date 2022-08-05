
class HtmlTable:
    
    def __init__(self, headers):
        # Создаём класс, изначально прописав заголовки полей
        self.html = None
        self.clean_table(headers)

    def to_table(self, line):
        # Дописываем строку (1 автора) в таблицу
        self.html += '<tr>'
        for i in line:
            data = i
            if isinstance(i, dict):
                data = ''.join([f'{j}: {i[j]}<br>' for j in i])
            self.html += f'<td>{data}</td>'
        self.html += '</tr>'

    def clean_table(self, headers):
        self.html = '<table class="table"><thead><tr>'
        for i in headers:
            self.html += f'<th>{i}</th>'
        self.html += '</tr></thead><tbody>'

    def get_table(self):
        return self.html + '</tbody></table>'
    
