import csv
import os


class GerenciadorArquivo:
    """
    Responsável por transformar listas de dados em arquivos CSV
    e vice-versa, com conversão automática de tipos (int / float).
    """

    def __init__(self, nome_arquivo):
        self.nome_arquivo = nome_arquivo

    # ── Conversão automática de tipo ────────────────────────
    def _converter_valor(self, valor):
        """Tenta converter string para int ou float automaticamente."""
        try:
            return int(valor)
        except ValueError:
            pass
        try:
            return float(valor)
        except ValueError:
            pass
        return valor   # permanece string se não for número

    # ── Leitura ─────────────────────────────────────────────
    def ler_dados(self):
        """
        Lê o CSV e retorna uma lista de dicionários.
        Converte valores numéricos automaticamente.
        """
        dados = []
        if not os.path.exists(self.nome_arquivo):
            return dados
        try:
            with open(self.nome_arquivo, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for linha in reader:
                    linha_convertida = {
                        chave: self._converter_valor(valor)
                        for chave, valor in linha.items()
                    }
                    dados.append(linha_convertida)
        except Exception as e:
            print(f"[GerenciadorArquivo] Erro ao ler '{self.nome_arquivo}': {e}")
        return dados

    # ── Escrita ─────────────────────────────────────────────
    def salvar_dados(self, dados):
        """
        Recebe uma lista de dicionários e salva no CSV.
        Cria o arquivo e o cabeçalho automaticamente.
        """
        if not dados:
            return
        try:
            with open(self.nome_arquivo, "w", encoding="utf-8", newline="") as f:
                campos = list(dados[0].keys())
                writer = csv.DictWriter(f, fieldnames=campos)
                writer.writeheader()
                writer.writerows(dados)
        except Exception as e:
            print(f"[GerenciadorArquivo] Erro ao salvar '{self.nome_arquivo}': {e}")