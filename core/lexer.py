from sly import Lexer


class ErroLexico(Exception):
    def __init__(self, mensagem, linha):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha


class DartLexer(Lexer):
    tokens = {
        ID,
        LPAREN, RPAREN, LBRACE, RBRACE, SEMI,
    }

    ignore = ' \t\r'
   
    ignore_comentario_linha = r'//[^\n]*'

    @_(r'/\*[\s\S]*?\*/')
    def ignore_comentario_bloco(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)

    ID = r'[a-zA-Z_$][a-zA-Z0-9_$]*'

    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    SEMI = r';'

    def error(self, t):
        raise ErroLexico(f"caractere inválido {t.value[0]!r}", self.lineno)