import unittest
from unittest.mock import patch
import io
import contextlib

import citizen_assist as ca


def novo(id_, titulo="T", categoria="C"):
    return ca.Servico(id_, titulo, categoria, "desc", "req", "local")


def ids(lista):
    return [s.id for s in lista]


class TestLista(unittest.TestCase):
    def setUp(self):
        self.l = ca.ListaEncadeada()

    # ---- casos normais
    def test_inserir_e_percorrer(self):
        for i in (1, 2, 3):
            self.l.inserir_fim(novo(i))
        self.assertEqual(ids(self.l), [1, 2, 3])
        self.assertEqual(len(self.l), 3)

    def test_buscar_por_id(self):
        self.l.inserir_fim(novo(7, "Vacina"))
        self.assertEqual(self.l.buscar_por_id(7).titulo, "Vacina")

    def test_busca_por_atributo_ignora_acento_e_caixa(self):
        self.l.inserir_fim(novo(1, "Emissão de RG"))
        self.l.inserir_fim(novo(2, "Vacinação"))
        self.assertEqual(ids(self.l.buscar_por_atributo("titulo", "EMISSAO")), [1])

    def test_atualizar(self):
        self.l.inserir_fim(novo(1, "Antigo"))
        self.assertTrue(self.l.atualizar(1, titulo="Novo"))
        self.assertEqual(self.l.buscar_por_id(1).titulo, "Novo")

    def test_remover_cabeca_meio_cauda(self):
        for i in (1, 2, 3, 4):
            self.l.inserir_fim(novo(i))
        self.assertTrue(self.l.remover(1))   # cabeça
        self.assertTrue(self.l.remover(3))   # meio
        self.assertTrue(self.l.remover(4))   # cauda
        self.assertEqual(ids(self.l), [2])
        self.l.inserir_fim(novo(9))          # cauda foi atualizada corretamente
        self.assertEqual(ids(self.l), [2, 9])

    def test_remover_unico_elemento(self):
        self.l.inserir_fim(novo(1))
        self.assertTrue(self.l.remover(1))
        self.assertTrue(self.l.esta_vazia())
        self.l.inserir_fim(novo(2))
        self.assertEqual(ids(self.l), [2])

    def test_ordenar_por_id_titulo_categoria(self):
        self.l.inserir_fim(novo(3, "b", "Z"))
        self.l.inserir_fim(novo(1, "C", "A"))
        self.l.inserir_fim(novo(2, "a", "M"))
        self.l.ordenar("id")
        self.assertEqual(ids(self.l), [1, 2, 3])
        self.l.ordenar("titulo")
        self.assertEqual(ids(self.l), [2, 3, 1])
        self.l.ordenar("categoria")
        self.assertEqual(ids(self.l), [1, 2, 3])

    def test_ordenar_estavel_e_cauda_correta(self):
        for i, cat in [(1, "B"), (2, "A"), (3, "B"), (4, "A")]:
            self.l.inserir_fim(novo(i, categoria=cat))
        self.l.ordenar("categoria")
        self.assertEqual(ids(self.l), [2, 4, 1, 3])  # estável
        self.l.inserir_fim(novo(5))
        self.assertEqual(ids(self.l)[-1], 5)

    def test_contagem_por_categoria(self):
        self.l.inserir_fim(novo(1, categoria="Saúde"))
        self.l.inserir_fim(novo(2, categoria="Saúde"))
        self.l.inserir_fim(novo(3, categoria="Educação"))
        self.assertEqual(self.l.contagem_por_categoria(), {"Saúde": 2, "Educação": 1})

    # ---- registros inexistentes
    def test_inexistentes(self):
        self.l.inserir_fim(novo(1))
        self.assertIsNone(self.l.buscar_por_id(99))
        self.assertEqual(self.l.buscar_por_atributo("titulo", "zzz"), [])
        self.assertFalse(self.l.atualizar(99, titulo="x"))
        self.assertFalse(self.l.remover(99))
        self.assertEqual(ids(self.l), [1])

    # ---- entradas inválidas
    def test_id_duplicado(self):
        self.l.inserir_fim(novo(1))
        with self.assertRaises(ValueError):
            self.l.inserir_fim(novo(1))
        self.assertEqual(len(self.l), 1)

    def test_atributo_e_criterio_invalidos(self):
        with self.assertRaises(ValueError):
            self.l.buscar_por_atributo("descricao", "x")
        with self.assertRaises(ValueError):
            self.l.ordenar("xyz")

    def test_atualizar_campo_invalido_ou_vazio(self):
        self.l.inserir_fim(novo(1))
        with self.assertRaises(ValueError):
            self.l.atualizar(1, id=5)
        with self.assertRaises(ValueError):
            self.l.atualizar(1, titulo="   ")

    # ---- lista vazia
    def test_lista_vazia(self):
        self.assertTrue(self.l.esta_vazia())
        self.assertEqual(list(self.l), [])
        self.assertIsNone(self.l.buscar_por_id(1))
        self.assertFalse(self.l.remover(1))
        self.l.ordenar("titulo")  # não deve quebrar
        self.assertEqual(self.l.contagem_por_categoria(), {})


class TestMenu(unittest.TestCase):
    def executar(self, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), \
                patch("citizen_assist.salvar"), patch("citizen_assist.carregar", return_value=0), \
                contextlib.redirect_stdout(saida):
            ca.main()
        return saida.getvalue()

    def test_opcao_inexistente(self):
        self.assertIn("Opção inexistente", self.executar(["abc", "99", "0"]))

    def test_operacoes_com_lista_vazia(self):
        out = self.executar(["2", "3", "4", "5", "6", "8", "0"])
        self.assertEqual(out.count("A lista está vazia."), 6)

    def test_id_invalido_e_duplicado(self):
        entradas = ["1", "abc", "-3", "0", "1", "T", "C", "D", "R", "L",
                    "1", "1", "0"]  # cadastra id 1; tenta cadastrar id 1 de novo
        out = self.executar(entradas)
        self.assertIn("número inteiro positivo", out)
        self.assertIn("Registro cadastrado com sucesso", out)
        self.assertIn("já existe um registro com o id 1", out)

    def test_campo_vazio_e_pesquisa_sem_resultado(self):
        entradas = ["9", "5", "1", "xyz", "0"]
        self.assertIn("Nenhum registro encontrado.", self.executar(entradas))
        entradas = ["1", "5", "", "T", "C", "D", "R", "L", "0"]
        self.assertIn("não pode ficar vazio", self.executar(entradas))


if __name__ == "__main__":
    unittest.main(verbosity=2)
