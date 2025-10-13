# Importação dos módulos
import os
import oracledb
import pandas as pd
import json

# Conexão com o banco
try:
    conexao = oracledb.connect(user='rm566645', password='110605', dsn='oracle.fiap.com.br:1521/ORCL')
    i_cadastro = conexao.cursor()
    i_consulta = conexao.cursor()
    i_atualizar = conexao.cursor()
    i_excluir = conexao.cursor()
except Exception as erro:
    print("Erro ao conectar no banco:", erro)
    conexao = None

margem = ' ' * 4


# -------------------------- FUNÇÕES AUXILIARES --------------------------

def calcular_risco(area_total, area_plantio):
    """Calcula o percentual de preservação e risco com base nos hectares informados."""
    perc_preservacao = ((area_total - area_plantio) / area_total) * 100
    if perc_preservacao >= 90:
        risco = "Baixo"
    elif perc_preservacao >= 70:
        risco = "Médio"
    else:
        risco = "Alto"
    return perc_preservacao, risco


# -------------------------- FUNÇÕES PRINCIPAIS --------------------------

def cadastrar_area():
    nome = input("Nome da área: ")

    try:
        area_total = float(input("Área total (ha): "))
        area_plantio = float(input("Área plantada (ha): "))
    except ValueError:
        print("Digite valores numéricos válidos!")
        input("\nPressione ENTER para continuar...")
        return

    perc_preservacao, risco = calcular_risco(area_total, area_plantio)

    sql = """
        INSERT INTO areas_plantio (nome, area_total, area_plantio, perc_preservacao, risco)
        VALUES (:nome, :area_total, :area_plantio, :perc_preservacao, :risco)
    """

    try:
        i_cadastro.execute(sql, {
            "nome": nome,
            "area_total": area_total,
            "area_plantio": area_plantio,
            "perc_preservacao": perc_preservacao,
            "risco": risco
        })
        conexao.commit()
        print(f"\nÁrea cadastrada com sucesso! Risco: {risco}")
    except Exception as e:
        print("Não foi possível cadastrar:", e)
    input("\nPressione ENTER para continuar...")


def listar_cadastro():
    print("----------- Listar áreas -----------")
    try:
        i_consulta.execute("SELECT * FROM areas_plantio ORDER BY id")
        data = i_consulta.fetchall()

        if not data:
            print("Não há áreas cadastradas.")
            input("\nPressione ENTER para continuar...")
            return

        dados_df = pd.DataFrame.from_records(
            data,
            columns=['ID', 'Nome', 'Área Total', 'Área Plantio', 'Preservação (%)', 'Risco']
        )
        print(dados_df)
        print("\n##### LISTADOS! #####")

        # --- JSON simplificado ---
        lista_dados = []
        for linha in data:
            id_, nome, total, plantio, perc_pres, risco = linha
            lista_dados.append({
                "id": id_,
                "nome": nome,
                "area_total": total,
                "area_plantio": plantio,
                "perc_preservacao": perc_pres,
                "risco": risco
            })

#indent=4 formata o JSON com indentação de 4 espaços (mais legível).
#ensure_ascii=False permite que caracteres não-ASCII (ex.: acentos) sejam gravados corretamente
        with open("relatorio_areas.json", "w", encoding="utf-8") as f: # encoding="utf-8" garante suporte a acentos.
            json.dump(lista_dados, f, indent=4, ensure_ascii=False)

        print("\n✅ Dados exportados para 'relatorio_areas.json'.")
    except Exception as e:
        print("Erro ao listar dados:", e)
    input("\nPressione ENTER para continuar...")


def atualizar_dados():
    print("----- ALTERAR DADOS DA ÁREA -----\n")
    try:
        id_area = input(margem + "Escolha um ID: ")
        while not id_area.isdigit():
            print("O ID deve ser numérico!")
            id_area = input(margem + "Escolha um ID válido: ")

        id_area = int(id_area)

        i_consulta.execute(f"SELECT * FROM areas_plantio WHERE id = {id_area}")
        data = i_consulta.fetchall()

        if not data:
            print(f"Não existe área cadastrada com o ID = {id_area}")
        else:
            at_nome = input(margem + "Nome da área: ")
            try:
                at_area_total = float(input(margem + "Área total (ha): "))
                at_area_plantio = float(input(margem + "Área plantada (ha): "))
            except ValueError:
                print("Digite valores numéricos válidos!")
                input("\nPressione ENTER para continuar...")
                return

            perc_preservacao, risco = calcular_risco(at_area_total, at_area_plantio)

            alterar = """
                UPDATE areas_plantio
                SET nome = :nome,
                    area_total = :area_total,
                    area_plantio = :area_plantio,
                    perc_preservacao = :perc_preservacao,
                    risco = :risco
                WHERE id = :id
            """

            i_atualizar.execute(alterar, {
                "nome": at_nome,
                "area_total": at_area_total,
                "area_plantio": at_area_plantio,
                "perc_preservacao": perc_preservacao,
                "risco": risco,
                "id": id_area
            })
            conexao.commit()
            print("\n##### Dados atualizados com sucesso! #####")
    except Exception as e:
        print("Erro ao atualizar:", e)
    input("\nPressione ENTER para continuar...")


def excluir_um():
    print("----- EXCLUIR UM REGISTRO -----\n")
    id_area = input(margem + "Escolha um ID: ")

    if not id_area.isdigit():
        print("O ID deve ser numérico!")
        input("\nPressione ENTER para continuar...")
        return

    id_area = int(id_area)
    try:
        i_consulta.execute(f"SELECT * FROM areas_plantio WHERE id = {id_area}")
        data = i_consulta.fetchall()

        if not data:
            print(f"Não há área cadastrada com o ID = {id_area}")
        else:
            i_excluir.execute(f"DELETE FROM areas_plantio WHERE id = {id_area}")
            conexao.commit()
            print("\n##### Área apagada com sucesso! #####")
    except Exception as e:
        print("Erro ao excluir:", e)
    input("\nPressione ENTER para continuar...")


def excluir_todos():
    print("\n!!!!! EXCLUI TODOS OS DADOS DA TABELA !!!!!\n")
    confirma = input(margem + "CONFIRMA A EXCLUSÃO DAS ÁREAS? [S/N]: ")

    if confirma.upper() == "S":
        try:
            i_excluir.execute("DELETE FROM areas_plantio")
            conexao.commit()
            print("##### Todos os registros foram excluídos! #####")
        except Exception as e:
            print("Erro ao excluir todos:", e)
    else:
        print(margem + "Operação cancelada pelo usuário!")
    input("\nPressione ENTER para continuar...")


# -------------------------- MENU --------------------------
if conexao:
    while True:
        os.system('cls')
        print("------- Sistema de Plantio Sustentável -------")
        print("""
    1 - Cadastrar nova área de plantio
    2 - Listar todas as áreas cadastradas
    3 - Atualizar dados de uma área cadastrada
    4 - Excluir um registro
    5 - Excluir todos os registros
    6 - SAIR
        """)

        escolha = input(margem + "Escolha -> ")

        while not escolha.isdigit():
            print("Digite uma opção válida!")
            escolha = input("Escolha -> ")

        escolha = int(escolha)

        match escolha:
            case 1:
                cadastrar_area()
            case 2:
                listar_cadastro()
            case 3:
                atualizar_dados()
            case 4:
                excluir_um()
            case 5:
                excluir_todos()
            case 6:
                print("Encerrando...")
                break
            case _:
                input(margem + "Digite um número entre 1 e 6.")

    conexao.close()
    print("Obrigado por utilizar o nosso sistema!!.")
else:
    print("Não foi possível conectar ao banco de dados.")
