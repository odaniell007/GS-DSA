# Citizen Assist AI — GS 2026.2 (DSA)

Protótipo em **Python 3** de um sistema de gerenciamento e consulta de serviços e orientações ao cidadão, usando uma **lista encadeada implementada pela equipe**, busca sequencial própria e **Merge Sort** próprio.

## Como executar

```bash
python citizen_assist.py          # abre o menu interativo
python test_citizen_assist.py     # roda os 18 testes automatizados
```

Requisitos: Python 3.8+ (somente biblioteca padrão). Os dados são salvos em `dados_citizen_assist.json` ao encerrar (opção 0) e carregados na próxima execução. A opção 9 carrega dados de exemplo para demonstração.

## 1. Recorte escolhido

Catálogo de serviços públicos ao cidadão nas categorias: Saúde, Documentação, Assistência Social, Educação e Serviços Urbanos (as categorias são livres: o usuário pode cadastrar outras).

## 2. Modelo dos registros (`Servico`)

| Campo | Tipo | Observação |
|---|---|---|
| id | int > 0 | identificador único, imutável |
| titulo | str | obrigatório |
| categoria | str | obrigatório |
| descricao | str | obrigatório |
| requisitos | str | documentos/condições exigidos |
| local | str | local de atendimento |

## 3. Estrutura da lista encadeada

- `No`: guarda `dado` (um `Servico`) e `proximo` (referência ao próximo nó).
- `ListaEncadeada`: mantém `cabeca`, `cauda` e `_tamanho`.
- Operações: inserção no fim (`inserir_fim`), percurso (`__iter__`), remoção por id (`remover`, tratando cabeça, meio e cauda), busca, atualização, ordenação e contagem por categoria.
- Integridade: id duplicado é rejeitado; a `cauda` é atualizada na remoção e na ordenação; `_tamanho` acompanha inserções/remoções.

## 4. Algoritmos

**Busca por id e por atributo (busca sequencial):** percorre os nós do início ao fim. Por atributo, devolve todos os registros cujo título/categoria/local *contém* o termo (sem diferenciar maiúsculas e acentos). Quando nada é encontrado, retorna `None` (id) ou lista vazia (atributo) e o menu informa "Nenhum registro encontrado". Não se usa busca binária porque a lista encadeada não permite acesso direto ao meio.

**Ordenação (Merge Sort sobre lista encadeada):** divide a lista ao meio com ponteiros lento/rápido, ordena cada metade recursivamente e mescla religando os nós (sem copiar dados). Critérios: id, título ou categoria. É estável. Não usa `sort`/`sorted`.

## 5. Complexidade (n = número de registros)

| Operação | Tempo | Justificativa |
|---|---|---|
| Inserção no fim | O(n) | verifica id duplicado percorrendo a lista; a ligação em si é O(1) graças à `cauda` |
| Busca por id | O(n) pior caso, O(1) melhor | busca sequencial |
| Busca por atributo | O(n·m) | m = tamanho do texto comparado; considerado O(n) |
| Atualização | O(n) | localizar o nó |
| Remoção | O(n) | localizar o nó; religar é O(1) |
| Percurso/listagem | O(n) | visita cada nó uma vez |
| Contagem por categoria | O(n) | um percurso com dicionário |
| Ordenação (Merge Sort) | O(n log n) em todos os casos | log n níveis de divisão, mescla O(n) por nível |

Espaço: O(n) para a lista; o Merge Sort usa O(log n) de pilha de recursão e não aloca nós novos.

## 6. Funcionamento do menu

`1` Cadastrar · `2` Consultar por id · `3` Atualizar · `4` Excluir · `5` Pesquisar · `6` Ordenar · `7` Análise · `8` Listar · `9` Dados de exemplo · `0` Encerrar (salva).

Validações: opção inexistente, id não numérico/negativo/zero, campo vazio, id duplicado, consulta/pesquisa sem resultado e operações com lista vazia.

## 7. Evidências de testes

Saída completa em `evidencias_testes.txt` (18 testes, todos OK).

| Caso | Entrada | Esperado | Observado |
|---|---|---|---|
| Inserir e percorrer | ids 1,2,3 | ordem 1,2,3; tamanho 3 | OK |
| Busca por id | id 7 | retorna o registro | OK |
| Busca por atributo | "EMISSAO" vs "Emissão de RG" | acha o registro 1 | OK |
| Atualizar | id 1, novo título | título alterado | OK |
| Remover cabeça/meio/cauda | ids 1, 3, 4 | resta só o id 2; inserção posterior funciona | OK |
| Remover único elemento | id 1 | lista vazia; nova inserção funciona | OK |
| Ordenar | por id, título, categoria | ordem correta | OK |
| Estabilidade e cauda | categorias repetidas | ordem relativa preservada; cauda correta | OK |
| Contagem por categoria | 2 Saúde, 1 Educação | `{"Saúde": 2, "Educação": 1}` | OK |
| Registro inexistente | id 99 / termo "zzz" | None / [] / False / False | OK |
| Id duplicado | inserir id 1 duas vezes | `ValueError`; tamanho 1 | OK |
| Atributo/critério inválido | "descricao", "xyz" | `ValueError` | OK |
| Campo não editável/vazio | `id=5`, título "   " | `ValueError` | OK |
| Lista vazia | todas as operações | sem erro | OK |
| Menu: opção inexistente | "abc", "99" | mensagem de opção inexistente | OK |
| Menu: operações com lista vazia | 2,3,4,5,6,8 | 6 avisos de lista vazia | OK |
| Menu: id inválido e duplicado | "abc", "-3", "0", id repetido | pede de novo / erro de duplicado | OK |
| Menu: campo vazio e pesquisa sem resultado | "" / "xyz" | reprompt / "Nenhum registro encontrado." | OK |

## 8. Demonstração (roteiro sugerido para o vídeo)

1. Opção 9 (dados de exemplo) e 8 (listar).
2. Cadastrar um novo registro; tentar repetir o id (mostra o erro).
3. Pesquisar por título "saude" e por um termo inexistente.
4. Ordenar por título e por categoria; mostrar o resultado.
5. Atualizar e excluir (cabeça, meio e cauda).
6. Opção 7 (análise) e opção 0 (salvar); reabrir e mostrar que os dados persistem.
7. Mostrar no código `No`, `ListaEncadeada.remover` e `_merge_sort`, e rodar `test_citizen_assist.py`.
