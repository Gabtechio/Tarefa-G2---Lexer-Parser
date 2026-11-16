"""Validador de um subconjunto de Dart (Grupo 18) - Sly.

Uso:
    python main.py                      # valida todos os .txt de examples/
    python main.py examples/arq.txt     # valida arquivo(s) específico(s)
"""
import os
import sys

from core.lexer import DartLexer, ErroLexico
from core.parser import DartParser, ErroSintatico

class ErroSemantico(Exception):
    def __init__(self, mensagem, linha):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha


def tipo_de(valor):
    if isinstance(valor, bool):
        return 'bool'
    if isinstance(valor, int):
        return 'int'
    if isinstance(valor, float):
        return 'double'
    if isinstance(valor, str):
        return 'String'
    return 'null'


def formatar(valor):
    if isinstance(valor, bool):
        return 'true' if valor else 'false'
    return str(valor)


def eh_numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


class Interpretador:
    """Executa a AST gerada pelo parser."""

    def __init__(self):
        self.escopos = [{}]
        self.linha = 0

    def erro(self, mensagem):
        raise ErroSemantico(mensagem, self.linha)

    def buscar(self, nome):
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        self.erro(f"variável '{nome}' não foi declarada")

    def conformar(self, tipo, valor, nome):
        if tipo == 'dynamic':
            return valor
        t = tipo_de(valor)
        if tipo == 'double' and t == 'int':
            return float(valor)
        if tipo == 'num' and t in ('int', 'double'):
            return valor
        if t != tipo:
            self.erro(f"não é possível atribuir {t} à variável '{nome}' do tipo {tipo}")
        return valor


    def executar_bloco(self, comandos):
        self.escopos.append({})
        try:
            for c in comandos:
                self.executar(c)
        finally:
            self.escopos.pop()

    def executar(self, no):
        getattr(self, 'exec_' + no[0])(no)

        def exec_decl(self, no):
        _, tipo, nome, expr, final, linha = no
        self.linha = linha
        if nome in self.escopos[-1]:
            self.erro(f"variável '{nome}' já foi declarada neste escopo")
        valor = None
        if expr is not None:
            valor = self.avaliar(expr)
            if tipo == 'var':
                tipo = tipo_de(valor)
            else:
                valor = self.conformar(tipo, valor, nome)
        elif tipo == 'var':
            tipo = 'dynamic'
        self.escopos[-1][nome] = {'tipo': tipo, 'valor': valor, 'final': final}

    def exec_assign(self, no):
        _, nome, op, expr, linha = no
        self.linha = linha
        var = self.buscar(nome)
        if var['final']:
            self.erro(f"variável final '{nome}' não pode receber novo valor")
        valor = self.avaliar(expr)
        if op != '=':
            if var['valor'] is None:
                self.erro(f"variável '{nome}' usada antes de receber valor")
            valor = self.operar(op[0], var['valor'], valor)
        var['valor'] = self.conformar(var['tipo'], valor, nome)



    def exec_print(self, no):
        _, expr, linha = no
        self.linha = linha
        print(formatar(self.avaliar(expr)))


    def avaliar(self, no):
        tipo = no[0]
        if tipo in ('int', 'double', 'string', 'bool'):
            return no[1]
        if tipo == 'var':
            var = self.buscar(no[1])
            if var['valor'] is None:
                self.erro(f"variável '{no[1]}' usada antes de receber valor")
            return var['valor']
        if tipo == 'neg':
            v = self.avaliar(no[1])
            if not eh_numero(v):
                self.erro(f"operador '-' não se aplica a {tipo_de(v)}")
            return -v
        if tipo == 'binop':
            return self.operar(no[1], self.avaliar(no[2]), self.avaliar(no[3]))
        self.erro(f"expressão desconhecida: {tipo}")

    def operar(self, op, a, b):
        if op == '+' and isinstance(a, str) and isinstance(b, str):
            return a + b
        if not (eh_numero(a) and eh_numero(b)):
            self.erro(f"operador '{op}' não se aplica a {tipo_de(a)} e {tipo_de(b)}")
        if op == '+':
            return a + b
        if op == '-':
            return a - b
        if op == '*':
            return a * b
        if b == 0:
            self.erro("divisão por zero")
        if op == '/':
            return a / b
        return a % b


def validar_arquivo(caminho):
    """Retorna True se o arquivo passou pelas análises."""
    print(f"=== {caminho} ===")
    with open(caminho, encoding='utf-8') as f:
        texto = f.read()
    total_linhas = texto.count('\n') + 1

    try:
        arvore = DartParser().parse(DartLexer().tokenize(texto))
        Interpretador().executar_bloco(arvore[1])
    except ErroLexico as e:
        print(f"[ERRO LÉXICO] linha {e.linha}: {e.mensagem}\n")
        return False
    except ErroSintatico as e:
        linha = e.linha if e.linha is not None else total_linhas
        print(f"[ERRO SINTÁTICO] linha {linha}: {e.mensagem}\n")
        return False
    except ErroSemantico as e:
        print(f"[ERRO SEMÂNTICO] linha {e.linha}: {e.mensagem}\n")
        return False



    print("[OK] arquivo válido\n")
    return True


def main():
    if len(sys.argv) > 1:
        arquivos = sys.argv[1:]
    else:
        pasta = 'examples'
        arquivos = sorted(os.path.join(pasta, f) for f in os.listdir(pasta) if f.endswith('.txt'))

    resultados = [(a, validar_arquivo(a)) for a in arquivos]
    ok = sum(1 for _, r in resultados if r)
    print(f"Resumo: {ok} válido(s), {len(resultados) - ok} inválido(s), {len(resultados)} arquivo(s).")


if __name__ == '__main__':
    main()
