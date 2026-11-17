

from sly import Parser
from core.lexer import DartLexer


class ErroSintatico(Exception):
    def __init__(self, mensagem, linha):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha


class DartParser(Parser):
    debugfile = 'parser.out'
    tokens = DartLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE, MOD),
        ('right', UMINUS),
    )

    # ------------------------------------------------------------ programa
    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)

    @_('')
    def program(self, p):
        return ('program', [])

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    # ------------------------------------------------------------ comandos
    @_('decl_init SEMI', 'update SEMI', 'if_stmt', 'for_stmt')
    def statement(self, p):
        return p[0]

    @_('VAR ID SEMI')
    def statement(self, p):
        return ('decl', 'var', p.ID, None, False, p.lineno)

    @_('TYPE ID SEMI')
    def statement(self, p):
        return ('decl', p.TYPE, p.ID, None, False, p.lineno)

    @_('PRINT LPAREN expr RPAREN SEMI')
    def statement(self, p):
        return ('print', p.expr, p.lineno)

    # ------------------------------------------------------------ tarefa 1: atribuição
    @_('VAR ID ASSIGN expr')
    def decl_init(self, p):
        return ('decl', 'var', p.ID, p.expr, False, p.lineno)

    @_('TYPE ID ASSIGN expr')
    def decl_init(self, p):
        return ('decl', p.TYPE, p.ID, p.expr, False, p.lineno)

    @_('FINAL ID ASSIGN expr')
    def decl_init(self, p):
        return ('decl', 'var', p.ID, p.expr, True, p.lineno)

    @_('FINAL TYPE ID ASSIGN expr')
    def decl_init(self, p):
        return ('decl', p.TYPE, p.ID, p.expr, True, p.lineno)

    @_('ID ASSIGN expr')
    def update(self, p):
        return ('assign', p.ID, '=', p.expr, p.lineno)

    @_('ID PLUSEQ expr')
    def update(self, p):
        return ('assign', p.ID, '+=', p.expr, p.lineno)

    @_('ID MINUSEQ expr')
    def update(self, p):
        return ('assign', p.ID, '-=', p.expr, p.lineno)

    @_('ID INCREMENT', 'INCREMENT ID')
    def update(self, p):
        return ('assign', p.ID, '+=', ('int', 1), p.lineno)

    @_('ID DECREMENT', 'DECREMENT ID')
    def update(self, p):
        return ('assign', p.ID, '-=', ('int', 1), p.lineno)

    # ------------------------------------------------------------ tarefa 3: IF
    @_('IF LPAREN condition RPAREN block')
    def if_stmt(self, p):
        return ('if', p.condition, p.block, None, p.lineno)

    @_('IF LPAREN condition RPAREN block ELSE block')
    def if_stmt(self, p):
        return ('if', p.condition, p.block0, p.block1, p.lineno)

    @_('IF LPAREN condition RPAREN block ELSE if_stmt')
    def if_stmt(self, p):
        return ('if', p.condition, p.block, [p.if_stmt], p.lineno)

    @_('LBRACE statement_list RBRACE')
    def block(self, p):
        return p.statement_list

    @_('LBRACE RBRACE')
    def block(self, p):
        return []

    @_('expr comp_op expr')
    def condition(self, p):
        return ('cond', p.comp_op, p.expr0, p.expr1)

    @_('EQ', 'NE', 'LT', 'LE', 'GT', 'GE')
    def comp_op(self, p):
        return p[0]

    # ------------------------------------------------------------ tarefa 4: FOR
    @_('FOR LPAREN for_init SEMI condition SEMI update RPAREN block')
    def for_stmt(self, p):
        return ('for', p.for_init, p.condition, p.update, p.block, p.lineno)

    @_('decl_init', 'update')
    def for_init(self, p):
        return p[0]

    # ------------------------------------------------------------ expressões
    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr TIMES expr',
       'expr DIVIDE expr',
       'expr MOD expr')
    def expr(self, p):
        return ('binop', p[1], p.expr0, p.expr1)

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('INT_LIT')
    def expr(self, p):
        return ('int', p.INT_LIT)

    @_('DOUBLE_LIT')
    def expr(self, p):
        return ('double', p.DOUBLE_LIT)

    @_('STRING_LIT')
    def expr(self, p):
        return ('string', p.STRING_LIT)

    @_('TRUE')
    def expr(self, p):
        return ('bool', True)

    @_('FALSE')
    def expr(self, p):
        return ('bool', False)

    @_('ID')
    def expr(self, p):
        return ('var', p.ID, p.lineno)

    # ------------------------------------------------------------ erros
    def error(self, token):
        if token:
            raise ErroSintatico(f"token inesperado {token.value!r}", token.lineno)
        raise ErroSintatico("fim do arquivo inesperado (faltou ';' ou '}' ?)", None)
