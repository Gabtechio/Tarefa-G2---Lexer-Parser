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
        INCREMENT, DECREMENT, PLUSEQ, MINUSEQ,
        EQ, NE, LE, GE, LT, GT, ASSIGN,
        PLUS, MINUS, TIMES, DIVIDE, MOD,
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

    INCREMENT = r'\+\+'
    DECREMENT = r'--'
    PLUSEQ = r'\+='
    MINUSEQ = r'-='
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='

    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    MOD = r'%'
    ASSIGN = r'='
    LT = r'<'
    GT = r'>'

    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    SEMI = r';'

    def error(self, t):
        caractere = t.value[0]
        if caractere in ('"', "'"):
            raise ErroLexico("string não foi fechada", self.lineno)
        raise ErroLexico(f"caractere inválido {caractere!r}", self.lineno)
