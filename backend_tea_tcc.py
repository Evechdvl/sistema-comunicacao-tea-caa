import sqlite3
from datetime import date
from typing import List, Optional
from dotenv import load_dotenv
load_dotenv()

DB_NAME = "sistema_tea.db"


# =====================================================================
# CAMADA DE PERSISTÊNCIA (SQLite3)
# =====================================================================

class DatabaseManager:
    """Gerencia a conexão SQLite, criação de tabelas e carga inicial para o TCC."""

    @staticmethod
    def get_connection() -> sqlite3.Connection:
        return sqlite3.connect(DB_NAME, check_same_thread=False)

    @classmethod
    def inicializar_banco(cls) -> None:
        conn = cls.get_connection()
        cursor = conn.cursor()

        # Criação das tabelas espelhando o Diagrama de Classes
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL,
                data_cadastro TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS informacao_crise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                sinais TEXT NOT NULL,
                orientacoes TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS contato_emergencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                descricao TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS biblioteca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS modulo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                biblioteca_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT NOT NULL,
                FOREIGN KEY (biblioteca_id) REFERENCES biblioteca(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS palavra (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modulo_id INTEGER NOT NULL,
                texto TEXT NOT NULL,
                categoria TEXT NOT NULL,
                FOREIGN KEY (modulo_id) REFERENCES modulo(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS imagem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                caminho TEXT NOT NULL,
                descricao TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS frase (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                modulo_id INTEGER,
                usuario_id INTEGER,
                texto TEXT NOT NULL,
                data_criacao TEXT NOT NULL,
                favorita INTEGER DEFAULT 0
            );
        """)
        conn.commit()

        # Verifica se já existem dados; se não, popula dados iniciais para apresentação do TCC
        cursor.execute("SELECT COUNT(*) FROM usuario")
        if cursor.fetchone()[0] == 0:
            cls._popular_dados_iniciais(cursor)
            conn.commit()

        conn.close()

    @staticmethod
    def _popular_dados_iniciais(cursor: sqlite3.Cursor) -> None:
        hoje = date.today().isoformat()

        # 1. Usuário padrão
        cursor.execute(
            "INSERT INTO usuario (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            ("Lucas Silva", "lucas@email.com", "123456", hoje)
        )
        usuario_id = cursor.lastrowid

        # 2. Informação de Crise e Contato de Emergência iniciais
        cursor.execute(
            "INSERT INTO informacao_crise (usuario_id, descricao, sinais, orientacoes) VALUES (?, ?, ?, ?)",
            (
                usuario_id,
                "Hipersensibilidade auditiva (locais barulhentos)",
                "Mãos nos ouvidos, balançar o corpo, respiração curta",
                "Levar para ambiente silencioso, oferecer abafador e evitar perguntas complexas."
            )
        )
        cursor.execute(
            "INSERT INTO contato_emergencia (usuario_id, nome, telefone, descricao) VALUES (?, ?, ?, ?)",
            (usuario_id, "Mariana Silva (Mãe)", "(11) 99999-1234", "Responsável Principal")
        )

        # 3. Biblioteca e Módulos (Composição 1..*)
        cursor.execute("INSERT INTO biblioteca (nome) VALUES (?)", ("Biblioteca CAA Principal",))
        bib_id = cursor.lastrowid

        modulos_iniciais = [
            (bib_id, "Necessidades Básicas", "Alimentação, sede, banheiro e saúde"),
            (bib_id, "Emoções e Sentimentos", "Como estou me sentindo agora"),
            (bib_id, "Rotina e Escola", "Atividades diárias e interação social")
        ]
        cursor.executemany(
            "INSERT INTO modulo (biblioteca_id, nome, descricao) VALUES (?, ?, ?)",
            modulos_iniciais
        )

        # 4. Palavras divididas por módulo
        palavras_iniciais = [
            (1, "Eu", "Pronome"), (1, "quero", "Verbo"), (1, "preciso de", "Verbo"),
            (1, "água", "Substantivo"), (1, "comida", "Substantivo"), (1, "ir ao banheiro", "Ação"),
            (1, "descansar", "Ação"), (1, "ajuda", "Substantivo"),
            (2, "Eu estou", "Pronome/Verbo"), (2, "feliz", "Emoção"), (2, "triste", "Emoção"),
            (2, "cansado", "Estado"), (2, "com medo", "Emoção"), (2, "incomodado com o barulho", "Sensorial"),
            (3, "Vamos", "Verbo"), (3, "brincar", "Ação"), (3, "estudar", "Ação"),
            (3, "para casa", "Local"), (3, "obrigado", "Social"), (3, "por favor", "Social")
        ]
        cursor.executemany(
            "INSERT INTO palavra (modulo_id, texto, categoria) VALUES (?, ?, ?)",
            palavras_iniciais
        )

        # 5. Frases Prontas Iniciais
        frases_iniciais = [
            (1, usuario_id, "Eu quero beber água, por favor", hoje, 1),
            (1, usuario_id, "Preciso ir ao banheiro", hoje, 1),
            (2, usuario_id, "O barulho está me incomodando muito", hoje, 1),
            (3, usuario_id, "Eu quero ir para casa descansar", hoje, 0)
        ]
        cursor.executemany(
            "INSERT INTO frase (modulo_id, usuario_id, texto, data_criacao, favorita) VALUES (?, ?, ?, ?, ?)",
            frases_iniciais
        )

        # 6. Imagens / Pictogramas CAA
        imagens_iniciais = [
            ("Beber Água", "💧", "Sede / Solicitar copo de água"),
            ("Comer / Fome", "🍎", "Fome / Solicitar refeição ou lanche"),
            ("Banheiro", "🚻", "Necessidade fisiológica imediata"),
            ("Muito Barulho", "🙉", "Sobrecarga sensorial auditiva"),
            ("Preciso de Ajuda", "🆘", "Solicitar auxílio de um adulto ou responsável"),
            ("Estou Feliz", "😊", "Expressar bem-estar e alegria"),
            ("Estou Triste / Dor", "😢", "Expressar desconforto emocional ou físico"),
            ("Ir para Casa", "🏠", "Desejo de retornar ao ambiente seguro")
        ]
        cursor.executemany(
            "INSERT INTO imagem (nome, caminho, descricao) VALUES (?, ?, ?)",
            imagens_iniciais
        )


# =====================================================================
# CLASSES DE DOMÍNIO
# =====================================================================

class Palavra:
    def __init__(self, id_palavra: int, texto: str, categoria: str, modulo_id: int = 1):
        self._id: int = id_palavra
        self._texto: str = texto
        self._categoria: str = categoria
        self._modulo_id: int = modulo_id

    @property
    def id(self) -> int: return self._id
    @property
    def texto(self) -> str: return self._texto
    @property
    def categoria(self) -> str: return self._categoria

    def adicionar(self) -> None:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO palavra (modulo_id, texto, categoria) VALUES (?, ?, ?)",
            (self._modulo_id, self._texto, self._categoria)
        )
        self._id = cursor.lastrowid
        conn.commit()
        conn.close()

    def remover(self) -> None:
        conn = DatabaseManager.get_connection()
        conn.execute("DELETE FROM palavra WHERE id = ?", (self._id,))
        conn.commit()
        conn.close()


class Imagem:
    def __init__(self, id_imagem: int = 0, caminho: str = "", nome: str = "", descricao: str = ""):
        self._id: int = id_imagem
        self._caminho: str = caminho
        self._nome: str = nome
        self._descricao: str = descricao

    @property
    def id(self) -> int:
        return self._id

    @property
    def caminho(self) -> str:
        return self._caminho

    @property
    def nome(self) -> str:
        return self._nome

    @property
    def descricao(self) -> str:
        return self._descricao

    @staticmethod
    def _garantir_tabela(conn):
        """Cria a tabela se não existir e popula apenas se estiver vazia."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS imagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caminho TEXT NOT NULL,
                nome TEXT NOT NULL,
                descricao TEXT
            )
        """)

        # Verifica quantos registros já existem na tabela
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM imagens")
        total = cursor.fetchone()[0]

        # Só insere os padrões se a tabela estiver completamente vazia (primeira execução)
        if total == 0:
            cards_iniciais = [
                ("💧", "Água", "Quero beber água"),
                ("🍎", "Comer", "Estou com fome, quero comer"),
                ("🚽", "Banheiro", "Preciso usar o banheiro"),
                ("😴", "Dormir", "Estou com sono, quero descansar"),
                ("😀", "Feliz", "Estou me sentindo bem e contente"),
                ("😢", "Triste", "Estou me sentindo chateado ou triste"),
                ("🛑", "Parar", "Não quero isso, por favor pare"),
                ("💊", "Dor", "Estou sentindo dor ou incômodo"),
                ("🧸", "Brincar", "Quero meus brinquedos ou jogos"),
                ("👋", "Ajuda", "Preciso de ajuda com alguma coisa"),
            ]
            conn.executemany("""
                INSERT INTO imagens (caminho, nome, descricao)
                VALUES (?, ?, ?)
            """, cards_iniciais)
            conn.commit()

    def adicionar(self) -> None:
        conn = DatabaseManager.get_connection()
        self._garantir_tabela(conn)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO imagens (caminho, nome, descricao) VALUES (?, ?, ?)",
            (self._caminho, self._nome, self._descricao)
        )
        self._id = cursor.lastrowid
        conn.commit()
        conn.close()

    def remover(self) -> None:
        conn = DatabaseManager.get_connection()
        self._garantir_tabela(conn)
        conn.execute("DELETE FROM imagens WHERE id = ?", (self._id,))
        conn.commit()
        conn.close()

    @classmethod
    def listar_todas(cls) -> list["Imagem"]:
        conn = DatabaseManager.get_connection()
        cls._garantir_tabela(conn)
        cursor = conn.cursor()
        cursor.execute("SELECT id, caminho, nome, descricao FROM imagens")
        linhas = cursor.fetchall()
        conn.close()
        return [cls(id_imagem=linha[0], caminho=linha[1], nome=linha[2], descricao=linha[3]) for linha in linhas]


class Frase:
    def __init__(
        self,
        id_frase: int = 0,
        texto: str = "",
        favorita: bool = False,
        data_criacao: Optional[str] = None,
        modulo_id: int = 1,
        usuario_id: int = 1
    ):
        self._id: int = id_frase
        self._texto: str = texto
        self._data_criacao: str = data_criacao or date.today().isoformat()
        self._favorita: bool = favorita
        self._modulo_id: int = modulo_id
        self._usuario_id: int = usuario_id
        self._palavras: List[Palavra] = []

    @property
    def id(self) -> int: return self._id
    @property
    def texto(self) -> str: return self._texto
    @property
    def favorita(self) -> bool: return self._favorita
    @favorita.setter
    def favorita(self, valor: bool) -> None: self._favorita = valor
    @property
    def data_criacao(self) -> str: return self._data_criacao

    def montar(self, palavras: List[Palavra]) -> None:
        self._palavras = palavras
        self._texto = " ".join([p.texto for p in self._palavras])
        self.salvar()

    def salvar(self) -> None:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        fav_int = 1 if self._favorita else 0
        if self._id == 0:
            cursor.execute(
                "INSERT INTO frase (modulo_id, usuario_id, texto, data_criacao, favorita) VALUES (?, ?, ?, ?, ?)",
                (self._modulo_id, self._usuario_id, self._texto, self._data_criacao, fav_int)
            )
            self._id = cursor.lastrowid
        else:
            cursor.execute(
                "UPDATE frase SET texto = ?, favorita = ? WHERE id = ?",
                (self._texto, fav_int, self._id)
            )
        conn.commit()
        conn.close()

    def excluir(self) -> None:
        if self._id != 0:
            conn = DatabaseManager.get_connection()
            conn.execute("DELETE FROM frase WHERE id = ?", (self._id,))
            conn.commit()
            conn.close()


class Modulo:
    def __init__(self, id_modulo: int, nome: str, descricao: str):
        self._id: int = id_modulo
        self._nome: str = nome
        self._descricao: str = descricao
        self._palavras: List[Palavra] = []
        self._frases: List[Frase] = []

    @property
    def id(self) -> int: return self._id
    @property
    def nome(self) -> str: return self._nome
    @property
    def descricao(self) -> str: return self._descricao
    @property
    def palavras(self) -> List[Palavra]:
        self.acessar()
        return self._palavras

    def acessar(self) -> None:
        conn = DatabaseManager.get_connection()
        p_rows = conn.execute(
            "SELECT id, texto, categoria, modulo_id FROM palavra WHERE modulo_id = ?", (self._id,)
        ).fetchall()
        self._palavras = [Palavra(r[0], r[1], r[2], r[3]) for r in p_rows]
        conn.close()


class Biblioteca:
    def __init__(self, id_biblioteca: int = 1, nome: str = "Biblioteca Principal"):
        self._id: int = id_biblioteca
        self._nome: str = nome

    def acessar_modulos(self) -> List[Modulo]:
        conn = DatabaseManager.get_connection()
        rows = conn.execute("SELECT id, nome, descricao FROM modulo WHERE biblioteca_id = ?", (self._id,)).fetchall()
        conn.close()
        return [Modulo(r[0], r[1], r[2]) for r in rows]

    def acessar_frases(self) -> List[Frase]:
        conn = DatabaseManager.get_connection()
        rows = conn.execute(
            "SELECT id, texto, favorita, data_criacao, modulo_id, usuario_id FROM frase ORDER BY favorita DESC, id DESC"
        ).fetchall()
        conn.close()
        return [Frase(r[0], r[1], bool(r[2]), r[3], r[4], r[5]) for r in rows]


class Comunicacao:
    def utilizar_texto(self, frase: Optional[Frase] = None, palavra: Optional[Palavra] = None) -> str:
        conteudo = frase.texto if frase else (palavra.texto if palavra else "")
        return self.comunicar(conteudo)

    def utilizar_imagem(self, imagem: Imagem) -> str:
        return self.comunicar(f"{imagem.nome} - {imagem.descricao}")

    def comunicar(self, texto_para_falar: str = "") -> str:
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.say(texto_para_falar)
            engine.runAndWait()
        except Exception:
            pass
        return texto_para_falar


class InformacaoCrise:
    def __init__(
        self,
        id_info: int = 0,
        descricao: str = "",
        sinais: str = "",
        orientacoes: str = "",
        usuario_id: int = 1,
    ):
        self._id: int = id_info
        self._descricao: str = descricao
        self._sinais: str = sinais
        self._orientacoes: str = orientacoes
        self._usuario_id: int = usuario_id

    @property
    def id(self) -> int: return self._id
    @property
    def descricao(self) -> str: return self._descricao
    @property
    def sinais(self) -> str: return self._sinais
    @property
    def orientacoes(self) -> str: return self._orientacoes
    @property
    def usuario_id(self) -> int: return self._usuario_id

    @descricao.setter
    def descricao(self, v: str): self._descricao = v
    @sinais.setter
    def sinais(self, v: str): self._sinais = v
    @orientacoes.setter
    def orientacoes(self, v: str): self._orientacoes = v

    def salvar(self) -> None:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        if self._id and self._id > 0:
            cursor.execute(
                """
                UPDATE informacao_crise 
                SET descricao = ?, sinais = ?, orientacoes = ?, usuario_id = ? 
                WHERE id = ?
                """,
                (self._descricao, self._sinais, self._orientacoes, self._usuario_id, self._id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO informacao_crise (descricao, sinais, orientacoes, usuario_id) 
                VALUES (?, ?, ?, ?)
                """,
                (self._descricao, self._sinais, self._orientacoes, self._usuario_id),
            )
            self._id = cursor.lastrowid
        conn.commit()
        conn.close()

    def remover(self) -> None:
        conn = DatabaseManager.get_connection()
        conn.execute("DELETE FROM informacao_crise WHERE id = ?", (self._id,))
        conn.commit()
        conn.close()


class ContatoEmergencia:
    def __init__(self, id_contato: int, nome: str, telefone: str, descricao: str, usuario_id: int = 1):
        self._id: int = id_contato
        self._nome: str = nome
        self._telefone: str = telefone
        self._descricao: str = descricao
        self._usuario_id: int = usuario_id

    @property
    def nome(self) -> str: return self._nome
    @property
    def telefone(self) -> str: return self._telefone
    @property
    def descricao(self) -> str: return self._descricao

    def cadastrar(self) -> None:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contato_emergencia (usuario_id, nome, telefone, descricao) VALUES (?, ?, ?, ?)",
            (self._usuario_id, self._nome, self._telefone, self._descricao)
        )
        self._id = cursor.lastrowid
        conn.commit()
        conn.close()

    def acionar(self) -> str:
        return f"🚨 Acionando emergência: {self._nome} ({self._descricao}) no número {self._telefone}!"

    
class Usuario:
    def __init__(self, id_usuario: int, nome: str, email: str, senha: str, data_cadastro: str = ""):
        self._id: int = id_usuario
        self._nome: str = nome
        self._email: str = email
        self._senha: str = senha
        self._data_cadastro: str = data_cadastro or date.today().isoformat()

    @property
    def id(self) -> int: return self._id
    @property
    def nome(self) -> str: return self._nome
    @property
    def email(self) -> str: return self._email

    @classmethod
    def autenticar(cls, email: str, senha: str) -> Optional["Usuario"]:
        conn = DatabaseManager.get_connection()
        row = conn.execute(
            "SELECT id, nome, email, senha, data_cadastro FROM usuario WHERE email = ? AND senha = ?",
            (email.strip(), senha.strip())
        ).fetchone()
        conn.close()
        if row:
            return cls(row[0], row[1], row[2], row[3], row[4])
        return None

    @classmethod
    def carregar_usuario_padrao(cls) -> "Usuario":
        conn = DatabaseManager.get_connection()
        row = conn.execute("SELECT id, nome, email, senha, data_cadastro FROM usuario LIMIT 1").fetchone()
        conn.close()
        return cls(row[0], row[1], row[2], row[3], row[4])

    def cadastrar(self) -> None:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuario (nome, email, senha, data_cadastro) VALUES (?, ?, ?, ?)",
            (self._nome, self._email, self._senha, self._data_cadastro)
        )
        self._id = cursor.lastrowid
        conn.commit()
        conn.close()

    def cadastrar_informacoes_crise(self, info: InformacaoCrise) -> None:
        info.cadastrar()

    def listar_informacoes_crise(self) -> list[InformacaoCrise]:
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, descricao, sinais, orientacoes, usuario_id 
            FROM informacao_crise 
            WHERE usuario_id = ?
            """,
            (self._id,),
        )
        linhas = cursor.fetchall()
        conn.close()
        return [
            InformacaoCrise(
                id_info=linha[0],
                descricao=linha[1],
                sinais=linha[2],
                orientacoes=linha[3],
                usuario_id=linha[4],
            )
            for linha in linhas
        ]

    def listar_contatos_emergencia(self) -> List[ContatoEmergencia]:
        conn = DatabaseManager.get_connection()
        rows = conn.execute(
            "SELECT id, nome, telefone, descricao, usuario_id FROM contato_emergencia WHERE usuario_id = ?",
            (self._id,)
        ).fetchall()
        conn.close()
        return [ContatoEmergencia(r[0], r[1], r[2], r[3], r[4]) for r in rows]


# =====================================================================
# INTEGRAÇÃO COM A API DO GEMINI (Baixo Consumo e Alta Latência)
# =====================================================================

def sugerir_frase_com_ia(texto_bruto: str) -> str:
    """
    Refina termos soltos em uma sentença estruturada de CAA para TEA.
    Desativa thinking_budget para evitar cortes de texto e utiliza
    fallback automático entre modelos estáveis da conta.
    """
    if not texto_bruto or not texto_bruto.strip():
        return ""

    try:
        import os
        from google import genai
        from google.genai import types

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            return texto_bruto

        client = genai.Client(api_key=api_key)

        config = types.GenerateContentConfig(
            system_instruction=(
                "Você é um motor de CAA (Comunicação Alternativa e Aumentativa) para pessoas autistas. "
                "Sua função é transformar palavras soltas em uma frase clara, educada, correta e em primeira pessoa do singular, "
                "em Português do Brasil. "
                "Regras estritas: Devolva APENAS a frase pronta final. Não use aspas, não dê explicações e não cumprimente."
            ),
            temperature=0.2,
            max_output_tokens=300,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        # Ordem de prioridade: 3.5-flash (confirmado), seguido por 3.1-lite e 3.8
        modelos = [
            "models/gemini-3.5-flash",
            "models/gemini-3.1-flash-lite",
            "models/gemini-3.8-flash",
        ]

        conteudo_prompt = f"Transforme em frase: {texto_bruto.strip()}"

        for modelo in modelos:
            try:
                response = client.models.generate_content(
                    model=modelo,
                    contents=conteudo_prompt,
                    config=config,
                )

                texto_saida = ""
                if hasattr(response, "text") and response.text:
                    texto_saida = response.text
                elif response.candidates and response.candidates[0].content.parts:
                    texto_saida = "".join(
                        [p.text for p in response.candidates[0].content.parts if hasattr(p, "text") and p.text]
                    )

                texto_limpo = texto_saida.strip().replace('"', '').replace("'", "")

                # Garante que não devolveu string vazia antes de entregar
                if len(texto_limpo) >= 3:
                    return texto_limpo

            except Exception as erro_modelo:
                print(f"[IA CAA Tentativa] {modelo} falhou: {erro_modelo}")
                continue

        return texto_bruto

    except Exception as erro_geral:
        print(f"[IA CAA Erro Geral]: {erro_geral}")
        return texto_bruto