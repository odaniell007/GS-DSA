"""
Citizen Assist AI - Global Solution 2026.2 (DSA)
Sistema de gerenciamento e consulta de serviços e orientações ao cidadão.

Estrutura de dados : lista encadeada simples (classes No e ListaEncadeada)
Busca              : busca sequencial (linear) por id e por atributo
Ordenação          : Merge Sort implementado sobre a própria lista encadeada
Execução           : python citizen_assist.py
"""

import json
import os
import unicodedata

ARQUIVO_DADOS = "dados_citizen_assist.json"
CAMPOS_EDITAVEIS = ("titulo", "categoria", "descricao", "requisitos", "local")


# ---------------------------------------------------------------- utilitários
def normalizar(texto):
    """Minúsculas e sem acentos, para busca/ordenação mais amigável."""
    sem_acento = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in sem_acento if unicodedata.category(c) != "Mn").lower().strip()


# ------------------------------------------------------------------- registro
class Servico:
    """Registro de um serviço ou orientação ao cidadão."""

    def __init__(self, id_, titulo, categoria, descricao, requisitos, local):
        self.id = id_
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.requisitos = requisitos
        self.local = local

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "categoria": self.categoria,
            "descricao": self.descricao,
            "requisitos": self.requisitos,
            "local": self.local,
        }

    def __str__(self):
        return (
            f"[{self.id}] {self.titulo} ({self.categoria})\n"
            f"    Descrição : {self.descricao}\n"
            f"    Requisitos: {self.requisitos}\n"
            f"    Local     : {self.local}"
        )


# ------------------------------------------------------------ lista encadeada
class No:
    """Nó da lista: guarda um Servico e a referência ao próximo nó."""

    def __init__(self, dado):
        self.dado = dado
        self.proximo = None


class ListaEncadeada:
    """Lista encadeada simples com ponteiro para cabeça e cauda."""

    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0

    def __len__(self):
        return self._tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def __iter__(self):
        """Percurso: devolve cada Servico, da cabeça até a cauda. O(n)."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    # ---- inserção --------------------------------------------------------
    def inserir_fim(self, servico):
        """Insere no fim. Rejeita id duplicado (percorre a lista: O(n))."""
        if self.buscar_por_id(servico.id) is not None:
            raise ValueError(f"Já existe um registro com o id {servico.id}.")
        novo = No(servico)
        if self.cabeca is None:
            self.cabeca = self.cauda = novo
        else:
            self.cauda.proximo = novo  # cauda guardada: ligação em O(1)
            self.cauda = novo
        self._tamanho += 1

    # ---- busca -----------------------------------------------------------
    def buscar_por_id(self, id_):
        """Busca sequencial por id. Retorna o Servico ou None. O(n)."""
        atual = self.cabeca
        while atual is not None:
            if atual.dado.id == id_:
                return atual.dado
            atual = atual.proximo
        return None

    def buscar_por_atributo(self, campo, termo):
        """
        Busca sequencial: devolve lista com todos os registros cujo atributo
        CONTÉM o termo (sem diferenciar maiúsculas/acentos). Se nada for
        encontrado, devolve lista vazia. O(n * m), m = tamanho do texto.
        """
        if campo not in ("titulo", "categoria", "local"):
            raise ValueError("Atributo de busca inválido.")
        alvo = normalizar(termo)
        return [s for s in self if alvo in normalizar(getattr(s, campo))]

    # ---- atualização -----------------------------------------------------
    def atualizar(self, id_, **novos):
        """Atualiza campos de um registro existente (o id não muda). O(n)."""
        servico = self.buscar_por_id(id_)
        if servico is None:
            return False
        for campo, valor in novos.items():
            if campo not in CAMPOS_EDITAVEIS:
                raise ValueError(f"Campo não editável: {campo}")
            if not str(valor).strip():
                raise ValueError(f"O campo {campo} não pode ficar vazio.")
            setattr(servico, campo, str(valor).strip())
        return True

    # ---- remoção ---------------------------------------------------------
    def remover(self, id_):
        """Remove o nó com o id dado, religando os vizinhos. O(n)."""
        anterior, atual = None, self.cabeca
        while atual is not None and atual.dado.id != id_:
            anterior, atual = atual, atual.proximo
        if atual is None:
            return False
        if anterior is None:  # remove a cabeça
            self.cabeca = atual.proximo
        else:
            anterior.proximo = atual.proximo
        if atual is self.cauda:  # remove a cauda: atualiza o ponteiro
            self.cauda = anterior
        self._tamanho -= 1
        return True

    # ---- ordenação (Merge Sort próprio sobre a lista) --------------------
    @staticmethod
    def _chave(campo):
        if campo == "id":
            return lambda s: s.id
        if campo in ("titulo", "categoria"):
            return lambda s: normalizar(getattr(s, campo))
        raise ValueError("Critério de ordenação inválido.")

    def ordenar(self, campo="titulo"):
        """Ordena a lista in-place religando nós. O(n log n), estável."""
        chave = self._chave(campo)
        self.cabeca = self._merge_sort(self.cabeca, chave)
        self.cauda = None
        atual = self.cabeca
        while atual is not None:  # recalcula a cauda
            self.cauda = atual
            atual = atual.proximo

    def _merge_sort(self, cabeca, chave):
        if cabeca is None or cabeca.proximo is None:
            return cabeca
        meio = self._dividir(cabeca)
        esquerda = self._merge_sort(cabeca, chave)
        direita = self._merge_sort(meio, chave)
        return self._mesclar(esquerda, direita, chave)

    @staticmethod
    def _dividir(cabeca):
        """Divide ao meio (lento/rápido) e devolve o início da 2ª metade."""
        lento, rapido = cabeca, cabeca.proximo
        while rapido is not None and rapido.proximo is not None:
            lento = lento.proximo
            rapido = rapido.proximo.proximo
        meio = lento.proximo
        lento.proximo = None
        return meio

    @staticmethod
    def _mesclar(a, b, chave):
        falso = No(None)
        atual = falso
        while a is not None and b is not None:
            if chave(a.dado) <= chave(b.dado):  # <= mantém a estabilidade
                atual.proximo, a = a, a.proximo
            else:
                atual.proximo, b = b, b.proximo
            atual = atual.proximo
        atual.proximo = a if a is not None else b
        return falso.proximo

    # ---- processamento ---------------------------------------------------
    def contagem_por_categoria(self):
        """Dicionário {categoria: quantidade}. O(n)."""
        contagem = {}
        for s in self:
            contagem[s.categoria] = contagem.get(s.categoria, 0) + 1
        return contagem


# ----------------------------------------------------------------- persistência
def salvar(lista, arquivo=ARQUIVO_DADOS):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump([s.to_dict() for s in lista], f, ensure_ascii=False, indent=2)


def carregar(lista, arquivo=ARQUIVO_DADOS):
    """Carrega registros do JSON. Retorna quantos foram carregados."""
    if not os.path.exists(arquivo):
        return 0
    try:
        with open(arquivo, encoding="utf-8") as f:
            dados = json.load(f)
        total = 0
        for d in dados:
            lista.inserir_fim(Servico(**d))
            total += 1
        return total
    except (json.JSONDecodeError, TypeError, ValueError, OSError):
        print("Aviso: arquivo de dados inválido; iniciando com lista vazia.")
        return 0


def dados_exemplo():
    return [
        Servico(1, "Vacinação na UBS", "Saúde", "Vacinas do calendário nacional.",
                "Cartão de vacina e documento com foto", "UBS mais próxima"),
        Servico(2, "Emissão de RG", "Documentação", "Primeira e segunda via do RG.",
                "Certidão de nascimento ou casamento", "Poupatempo"),
        Servico(3, "Cadastro Único (CadÚnico)", "Assistência Social",
                "Inscrição para programas sociais.", "CPF e comprovante de residência", "CRAS"),
        Servico(4, "Curso de Informática Básica", "Educação",
                "Curso gratuito de qualificação.", "Maiores de 16 anos", "Centro de Capacitação"),
        Servico(5, "Reparo de iluminação pública", "Serviços Urbanos",
                "Solicitação de troca de lâmpada de poste.", "Endereço do poste", "Canal 156"),
        Servico(6, "Consulta médica clínica geral", "Saúde", "Atendimento ambulatorial.",
                "Cartão SUS e documento com foto", "UBS mais próxima"),
    ]


# ------------------------------------------------------------------ entrada
def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("  Entrada inválida: o campo não pode ficar vazio.")


def ler_id(mensagem):
    while True:
        bruto = input(mensagem).strip()
        if bruto.isdigit() and int(bruto) > 0:
            return int(bruto)
        print("  Entrada inválida: informe um número inteiro positivo.")


# --------------------------------------------------------------------- menu
def opcao_cadastrar(lista):
    id_ = ler_id("Id (número inteiro positivo): ")
    if lista.buscar_por_id(id_) is not None:
        print(f"  Erro: já existe um registro com o id {id_}.")
        return
    servico = Servico(
        id_,
        ler_texto("Título: "),
        ler_texto("Categoria: "),
        ler_texto("Descrição: "),
        ler_texto("Requisitos: "),
        ler_texto("Local de atendimento: "),
    )
    lista.inserir_fim(servico)
    print("  Registro cadastrado com sucesso.")


def opcao_consultar(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    servico = lista.buscar_por_id(ler_id("Id a consultar: "))
    print(servico if servico else "  Nenhum registro encontrado com esse id.")


def opcao_atualizar(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    id_ = ler_id("Id a atualizar: ")
    servico = lista.buscar_por_id(id_)
    if servico is None:
        print("  Nenhum registro encontrado com esse id.")
        return
    print(servico)
    print("Deixe em branco para manter o valor atual.")
    novos = {}
    for campo in CAMPOS_EDITAVEIS:
        valor = input(f"Novo {campo}: ").strip()
        if valor:
            novos[campo] = valor
    lista.atualizar(id_, **novos)
    print("  Registro atualizado.")


def opcao_excluir(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    id_ = ler_id("Id a excluir: ")
    print("  Registro excluído." if lista.remover(id_) else "  Nenhum registro encontrado com esse id.")


def opcao_pesquisar(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    escolha = input("Pesquisar por (1) título, (2) categoria, (3) local: ").strip()
    campos = {"1": "titulo", "2": "categoria", "3": "local"}
    if escolha not in campos:
        print("  Opção inválida.")
        return
    resultados = lista.buscar_por_atributo(campos[escolha], ler_texto("Termo: "))
    if not resultados:
        print("  Nenhum registro encontrado.")
        return
    print(f"  {len(resultados)} registro(s) encontrado(s):")
    for s in resultados:
        print(s)


def listar(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    for s in lista:
        print(s)


def opcao_ordenar(lista):
    if lista.esta_vazia():
        print("  A lista está vazia.")
        return
    escolha = input("Ordenar por (1) id, (2) título, (3) categoria: ").strip()
    campos = {"1": "id", "2": "titulo", "3": "categoria"}
    if escolha not in campos:
        print("  Opção inválida.")
        return
    lista.ordenar(campos[escolha])
    print(f"  Lista ordenada por {campos[escolha]} (Merge Sort):")
    listar(lista)


def opcao_analise(lista):
    total = len(lista)
    print(f"  Total de registros: {total}")
    if total == 0:
        return
    contagem = lista.contagem_por_categoria()
    print("  Quantidade por categoria:")
    for categoria, qtd in sorted(contagem.items(), key=lambda p: (-p[1], p[0])):
        print(f"    {categoria}: {qtd} ({qtd / total:.0%})")
    mais = max(contagem, key=contagem.get)
    print(f"  Categoria com mais registros: {mais} ({contagem[mais]})")


MENU = """
===== Citizen Assist AI =====
1 - Cadastrar
2 - Consultar por id
3 - Atualizar
4 - Excluir
5 - Pesquisar (título/categoria/local)
6 - Ordenar
7 - Análise
8 - Listar todos
9 - Carregar dados de exemplo
0 - Encerrar
"""


def main():
    lista = ListaEncadeada()
    carregados = carregar(lista)
    if carregados:
        print(f"{carregados} registro(s) carregado(s) de {ARQUIVO_DADOS}.")
    acoes = {
        "1": opcao_cadastrar, "2": opcao_consultar, "3": opcao_atualizar,
        "4": opcao_excluir, "5": opcao_pesquisar, "6": opcao_ordenar,
        "7": opcao_analise, "8": listar,
    }
    while True:
        print(MENU)
        try:
            opcao = input("Escolha: ").strip()
        except EOFError:
            opcao = "0"
        if opcao == "0":
            salvar(lista)
            print("Dados salvos. Até logo!")
            break
        if opcao == "9":
            for s in dados_exemplo():
                try:
                    lista.inserir_fim(s)
                except ValueError:
                    pass  # já carregado
            print("  Dados de exemplo carregados.")
        elif opcao in acoes:
            acoes[opcao](lista)
        else:
            print("  Opção inexistente. Escolha um número do menu.")


if __name__ == "__main__":
    main()
