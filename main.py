import random
from gerenciador_arquivos import GerenciadorArquivo

db_jogos = GerenciadorArquivo("jogos.csv")
db_vendas = GerenciadorArquivo("vendas.csv")


class Jogo:
    # Construtor para criar um novo jogo
    def __init__(self, codigo, nome, genero, preco, estoque):
        self.codigo = str(codigo)
        self.nome = str(nome)
        self.genero = str(genero)
        self.preco = float(preco)
        self.estoque = int(estoque)

    # Método para converter o objeto Jogo em um dicionário para que a classe gerenciador consiga salvar no CSV
    def to_dict(self):
        return {
            "codigo": self.codigo,
            "nome": self.nome,
            "genero": self.genero,
            "preco": self.preco,
            "estoque": self.estoque,
        }

    # Exibir as informações do jogo. Vai ficar mostrando estoque/indicando que está esgotado
    def exibir(self):
        estoque_txt = f"{self.estoque} un." if self.estoque > 0 else "ESGOTADO"
        print(f"  [{self.codigo}] {self.nome:<28} {self.genero:<12} R$ {self.preco:>7.2f}   {estoque_txt}")

# Classe para representar um item no carrinho, que tem um jogo e a quantidade desejada
class ItemCarrinho:
    def __init__(self, jogo, quantidade=1):
        self.jogo = jogo
        self.quantidade = quantidade

    def subtotal(self):
        return self.jogo.preco * self.quantidade

# Classe para representar o carrinho de compras do cliente, que pode adicionar/remover itens, calcular total, etc.
class Carrinho:
    # Construtor para criar um carrinho vazio
    def __init__(self):
        self.itens = []

    # Método para adicionar um jogo ao carrinho. Se o jogo já estiver no carrinho, apenas muda a quantidade
    def adicionar(self, jogo, qtd=1):
        for item in self.itens:
            if item.jogo.codigo == jogo.codigo:
                item.quantidade += qtd
                print(f"  Quantidade de '{jogo.nome}' atualizada para {item.quantidade}.")
                return
        self.itens.append(ItemCarrinho(jogo, qtd))
        print(f"  '{jogo.nome}' adicionado ao carrinho.")

 
    # Método para remover um jogo do carrinho
    def remover(self, codigo):
        for i, item in enumerate(self.itens):
            if item.jogo.codigo == codigo:
                print(f"  '{item.jogo.nome}' removido.")
                self.itens.pop(i)
                return
        print("  Codigo nao encontrado no carrinho.")

    # Método para calcular o total do carrinho somando o subtotal de cada item
    def total(self):
        return sum(item.subtotal() for item in self.itens)

    # Método para limpar o carrinho, removendo todos os itens
    def limpar(self):
        self.itens.clear()

    # Método para exibir o conteúdo do carrinho, mostrando cada item.
    def exibir(self):
        if not self.itens:
            print("  Carrinho vazio.")
            return
        print("\n  ┌─ Seu Carrinho " + "─" * 40)
        for item in self.itens:
            print(f"  │  {item.jogo.nome:<30} x{item.quantidade}  R$ {item.subtotal():.2f}")
        print(f"  │  {'':─<46}")
        print(f"  │  {'TOTAL':>36}  R$ {self.total():.2f}")
        print("  └" + "─" * 47)

# Classe para representar um cliente, que tem um nome e um carrinho de compras
class Cliente:
    # Construtor para criar um cliente com um nome e um carrinho vazio
    def __init__(self, nome):
        self.nome = nome.strip().title()
        self.carrinho = Carrinho()

    # Método para exibir o status do cliente, mostrando o nome, quantidade de itens...
    def status(self):
        print(f"\n  {self.nome}  |  Itens: {len(self.carrinho.itens)}  |  Total: R$ {self.carrinho.total():.2f}")

# Função para carregar os jogos do arquivo CSV usando o gerenciador de arquivos. 
# Converte cada linha em um objeto Jogo.
def carregar_jogos():
    registros = db_jogos.ler_dados()
    jogos = []
    for r in registros:
        try:
            jogos.append(Jogo(r["codigo"], r["nome"], r["genero"], r["preco"], r["estoque"]))
        except (KeyError, ValueError) as e:
            print(f"  Linha ignorada no CSV: {e}")
    return jogos

# Função para salvar os jogos no arquivo CSV usando o gerenciador de arquivos.
def salvar_jogos(jogos):
    db_jogos.salvar_dados([j.to_dict() for j in jogos])

# Função para registrar uma venda no arquivo CSV de vendas. 
def registrar_venda(cliente, jogos_comprados, total):
    historico = db_vendas.ler_dados()
    for j in jogos_comprados:
        historico.append({
            "cliente": cliente.nome,
            "jogo": j.jogo.nome,
            "qtd": j.quantidade,
            "subtotal": j.subtotal(),
            "total_pedido": total,
        })
    db_vendas.salvar_dados(historico)

# Função para buscar jogos por nome, filtrando a lista de jogos e retornando os que contêm o termo pesquisado.
def buscar_por_nome(jogos, termo):
    termo = termo.lower()
    return [j for j in jogos if termo in j.nome.lower()]

# Função para buscar um jogo por código, percorrendo a lista de jogos e retornando o que tiver o código correspondente.
def jogo_por_codigo(jogos, codigo):
    for j in jogos:
        if j.codigo == codigo:
            return j
    return None

# Função para gerar um relatório com informações sobre os jogos cadastrados.
def relatorio(jogos):
    print("\n  ┌─ RELATORIO " + "─" * 42)
    print(f"  │  Total de jogos    : {len(jogos)}")
    if not jogos:
        print("  └" + "─" * 53)
        return
    precos = [j.preco for j in jogos]
    media = sum(precos) / len(precos)
    mais_caro = max(jogos, key=lambda j: j.preco)
    mais_barato = min(jogos, key=lambda j: j.preco)
    generos = list({j.genero for j in jogos})
    print(f"  │  Preco medio       : R$ {media:.2f}")
    print(f"  │  Mais caro         : {mais_caro.nome} (R$ {mais_caro.preco:.2f})")
    print(f"  │  Mais barato       : {mais_barato.nome} (R$ {mais_barato.preco:.2f})")
    print(f"  │  Generos           : {', '.join(sorted(generos))}")
    vendas = db_vendas.ler_dados()
    if vendas:
        total_vendido = sum(v["subtotal"] for v in vendas)
        print(f"  │  Total em vendas   : R$ {total_vendido:.2f}")
        print(f"  │  Pedidos           : {len(vendas)} linha(s)")
    print("  └" + "─" * 53)


# Função para aplicar um cupom de desconto, verificando se o cupom é válido e calculando o desconto no total.
def aplicar_cupom(total):
    cupom = input("  Cupom de desconto (Enter p/ pular): ").strip().upper()
    cupons_validos = {"IFPE10": 10, "GAMER20": 20, "LAIRSON15": 15}
    if cupom == "":
        return total, 0
    try:
        pct = cupons_validos[cupom]
        desconto = total * (pct / 100)
        print(f"  Cupom '{cupom}' aplicado! -{pct}%  (-R$ {desconto:.2f})")
        return total - desconto, pct
    except KeyError:
        print("  Cupom invalido.")
        return total, 0

# Função para cadastrar um novo jogo, solicitando as informações do jogo e validando os dados de entrada.
def cadastrar_jogo(jogos):
    print("\n  ── Cadastrar Novo Jogo ──────────────────")
    nome = input("  Nome    : ").strip().title()
    genero = input("  Genero  : ").strip().title()
    while True:
        try:
            preco = float(input("  Preco   : ").replace(",", "."))
            if preco <= 0:
                raise ValueError("O preco deve ser positivo.")
            break
        except ValueError as e:
            print(f"  Erro: {e}. Tente novamente.")
    while True:
        try:
            estoque = int(input("  Estoque : "))
            if estoque < 0:
                raise ValueError("Estoque nao pode ser negativo.")
            break
        except ValueError as e:
            print(f"  Erro: {e}. Tente novamente.")
    codigo = f"JG{random.randint(1000, 9999)}"
    novo = Jogo(codigo, nome, genero, preco, estoque)
    jogos.append(novo)
    salvar_jogos(jogos)
    print(f"  '{nome}' cadastrado com codigo {codigo}.")

# Função para remover um jogo, mostrando a lista de jogos e solicitando o código do jogo a ser removido.
def remover_jogo(jogos):
    for j in jogos:
        j.exibir()
    cod = input("\n  Codigo para remover: ").strip().upper()
    antes = len(jogos)
    jogos[:] = [j for j in jogos if j.codigo != cod]
    if len(jogos) < antes:
        salvar_jogos(jogos)
        print("  Jogo removido.")
    else:
        print("  Codigo nao encontrado.")

# Lista de jogos de demonstração para carregar no início, caso o arquivo CSV esteja vazio.
JOGOS_DEMO = [
    Jogo("JG1001", "The Last of Us Part I", "Aventura", 199.90, 10),
    Jogo("JG1002", "FIFA 25", "Esporte", 159.90, 15),
    Jogo("JG1003", "Minecraft", "Sandbox", 89.90, 50),
    Jogo("JG1004", "God of War Ragnarok", "Acao", 249.90, 8),
    Jogo("JG1005", "Hollow Knight", "Indie", 29.90, 30),
    Jogo("JG1006", "Stardew Valley", "Indie", 37.90, 25),
    Jogo("JG1007", "EA Sports FC 25", "Esporte", 179.90, 12),
    Jogo("JG1008", "Red Dead Redemption 2", "Aventura", 149.90, 6),
]

# Função para exibir o cabeçalho do sistema, mostrando o nome do e-commerce e a instituição.
def cabecalho():
    print("\n" + "═" * 55)
    print("           E-COMMERCE DE JOGOS  ")
    print("        IFPE Afogados da Ingazeira")
    print("═" * 55)

# Função para exibir o menu principal, mostrando as opções disponíveis para o cliente.
def menu_principal():
    print("\n  ┌─ MENU " + "─" * 40)
    print("  │  1. Ver Catalogo")
    print("  │  2. Buscar Jogo")
    print("  │  3. Meu Carrinho")
    print("  │  4. Finalizar Compra")
    print("  │  5. Administracao")
    print("  │  6. Relatorio")
    print("  │  0. Sair")
    print("  └" + "─" * 47)
    return input("  Opcao: ").strip()

# Função para exibir o catálogo de jogos, permitindo que o cliente adicione jogos ao carrinho.
def tela_catalogo(jogos, cliente):
    print("\n  ── CATALOGO " + "─" * 43)
    if not jogos:
        print("  Nenhum jogo cadastrado.")
        return
    for j in jogos:
        j.exibir()
    print()
    cod = input("  Codigo para adicionar ao carrinho (Enter p/ voltar): ").strip().upper()
    if not cod:
        return
    jogo = jogo_por_codigo(jogos, cod)
    if not jogo:
        print("  Codigo invalido.")
        return
    if jogo.estoque == 0:
        print("  Jogo esgotado.")
        return
    while True:
        try:
            qtd = int(input(f"  Quantidade (max {jogo.estoque}): "))
            if qtd <= 0:
                raise ValueError("Quantidade deve ser maior que zero.")
            if qtd > jogo.estoque:
                raise ValueError(f"Estoque insuficiente (max {jogo.estoque}).")
            break
        except ValueError as e:
            print(f"  {e}")
    cliente.carrinho.adicionar(jogo, qtd)

# Função para exibir a tela de busca, permitindo que o cliente pesquise jogos por nome e adicione ao carrinho.
def tela_busca(jogos, cliente):
    print("\n  ── BUSCAR ─────────────────────────────────")
    termo = input("  Pesquisar por nome: ").strip()
    resultado = buscar_por_nome(jogos, termo)
    if not resultado:
        print("  Nenhum resultado encontrado.")
        return
    print(f"\n  {len(resultado)} resultado(s):\n")
    for j in resultado:
        j.exibir()
    cod = input("\n  Adicionar ao carrinho? (codigo ou Enter p/ voltar): ").strip().upper()
    if not cod:
        return
    jogo = jogo_por_codigo(resultado, cod)
    if not jogo:
        print("  Codigo invalido.")
        return
    if jogo.estoque == 0:
        print("  Jogo esgotado.")
        return
    while True:
        try:
            qtd = int(input(f"  Quantidade (max {jogo.estoque}): "))
            if qtd <= 0 or qtd > jogo.estoque:
                raise ValueError("Quantidade invalida.")
            break
        except ValueError as e:
            print(f"  {e}")
    cliente.carrinho.adicionar(jogo, qtd)

# Função para exibir o carrinho do cliente, mostrando os itens adicionados e permitindo que o cliente remova itens do carrinho.
def tela_carrinho(cliente):
    print("\n  ── CARRINHO ───────────────────────────────")
    cliente.carrinho.exibir()
    if not cliente.carrinho.itens:
        return
    cod = input("  Codigo para remover (Enter p/ voltar): ").strip().upper()
    if cod:
        cliente.carrinho.remover(cod)

# Função para finalizar a compra, mostrando o resumo do pedido, aplicando cupom de desconto e registrando a venda.
def tela_finalizar(cliente, jogos):
    print("\n  ── FINALIZAR COMPRA ───────────────────────")
    cliente.carrinho.exibir()
    if not cliente.carrinho.itens:
        return
    total_bruto = cliente.carrinho.total()
    total_final, _ = aplicar_cupom(total_bruto)
    print(f"\n  Subtotal  : R$ {total_bruto:.2f}")
    print(f"  A pagar   : R$ {total_final:.2f}")
    confirma = input("\n  Confirmar pedido? (S/N): ").strip().upper()
    if confirma != "S":
        print("  Pedido cancelado.")
        return
    for item in cliente.carrinho.itens:
        for j in jogos:
            if j.codigo == item.jogo.codigo:
                j.estoque -= item.quantidade
                break
    registrar_venda(cliente, cliente.carrinho.itens, total_final)
    salvar_jogos(jogos)
    print(f"\n  Pedido confirmado! Obrigado, {cliente.nome}! 🎮")
    print(f"  Total pago: R$ {total_final:.2f}")
    cliente.carrinho.limpar()

# Função para exibir a tela de administração, permitindo que o administrador cadastre ou remova jogos do catálogo.
def tela_admin(jogos):
    print("\n  ── ADMINISTRACAO ──────────────────────────")
    print("  1. Cadastrar novo jogo")
    print("  2. Remover jogo")
    print("  0. Voltar")
    op = input("  Opcao: ").strip()
    if op == "1":
        cadastrar_jogo(jogos)
    elif op == "2":
        remover_jogo(jogos)

# Função principal do programa, que exibe o cabeçalho, carrega os jogos, solicita o nome do cliente e exibe o menu principal.
def main():
    cabecalho()
    jogos = carregar_jogos()
    if not jogos:
        jogos = JOGOS_DEMO[:]
        salvar_jogos(jogos)
        print("  Catalogo inicial carregado!")
    while True:
        try:
            nome = input("\n  Qual e o seu nome? ").strip()
            if not nome:
                raise ValueError("O nome nao pode ser vazio.")
            break
        except ValueError as e:
            print(f"  {e}")
    cliente = Cliente(nome)
    print(f"\n  Ola, {cliente.nome}!")
    while True:
        cliente.status()
        opcao = menu_principal()
        if opcao == "1":
            tela_catalogo(jogos, cliente)
        elif opcao == "2":
            tela_busca(jogos, cliente)
        elif opcao == "3":
            tela_carrinho(cliente)
        elif opcao == "4":
            tela_finalizar(cliente, jogos)
        elif opcao == "5":
            tela_admin(jogos)
        elif opcao == "6":
            relatorio(jogos)
        elif opcao == "0":
            print(f"\n  Volte sempre, {cliente.nome}!\n")
            break
        else:
            print("  Opcao invalida.")


if __name__ == "__main__":
    main()
