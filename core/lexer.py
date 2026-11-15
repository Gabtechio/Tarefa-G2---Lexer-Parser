from sly import Lexer


class ErroLexico(Exception):
    def __init__(self, mensagem, linha):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha


class DartLexer(Lexer):
        tokens = {
        ID, TYPE, VAR, FINAL, IF, ELSE, FOR, PRINT, TRUE, FALSE,
        INT_LIT, DOUBLE_LIT, STRING_LIT,
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

    ID['var'] = VAR
    ID['final'] = FINAL
    ID['if'] = IF
    ID['else'] = ELSE
    ID['for'] = FOR
    ID['print'] = PRINT
    ID['true'] = TRUE
    ID['false'] = FALSE
    ID['int'] = TYPE
    ID['double'] = TYPE
    ID['num'] = TYPE
    ID['bool'] = TYPE
    ID['String'] = TYPE

    @_(r'\d+\.\d+')
    def DOUBLE_LIT(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INT_LIT(self, t):
        t.value = int(t.value)
        return t

    @_(r'"(?:\\.|[^"\\\n])*"' r"|'(?:\\.|[^'\\\n])*'")
    def STRING_LIT(self, t):
        texto = t.value[1:-1]
        texto = (texto.replace('\\n', '\n').replace('\\t', '\t')
                 .replace('\\"', '"').replace("\\'", "'")
                 .replace('\\\\', '\\'))
        t.value = texto
        return t

    def error(self, t):
        raise ErroLexico(f"caractere inválido {t.value[0]!r}", self.lineno)