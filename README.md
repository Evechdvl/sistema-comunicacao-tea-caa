📱 Sistema de Apoio à Comunicação Alternativa e Aumentativa (CAA) para TEA

Sistema desenvolvido como base prática para Trabalho de Conclusão de Curso (TCC), voltado a fornecer ferramentas de Comunicação Alternativa e Aumentativa (CAA) para pessoas com Transtorno do Espectro Autista (TEA).

O aplicativo simula a interface de um dispositivo móvel, oferecendo montagem de sentenças guiada por categorias gramaticais, pranchas visuais com pictogramas, gestão de frases salvas, cartões de orientação para momentos de desregulação sensorial/crise e botão de alerta para contatos de emergência.

📂 Estrutura do Repositório

backend_tea_tcc.py:

Persistência de Dados (DatabaseManager): Configura a base de dados relacional SQLite (sistema_tea.db) e popula dados iniciais (módulos, palavras, frases, imagens e usuário demo) automaticamente na primeira execução.

Modelo de Domínio: Implementa as classes de negócio mapeadas no diagrama de classes UML: Usuario, InformacaoCrise, ContatoEmergencia, Biblioteca, Modulo, Palavra, Imagem, Frase e Comunicacao.

Síntese de Voz: Integração de áudio via motor TTS (pyttsx3) com mecanismo de contingência para execução silenciosa.

Módulo de Inteligência Artificial (sugerir_frase_com_ia): Integração opcional de baixo consumo de tokens conectada ao modelo gemini-3.8-flash para refinar e expandir construções curtas em sentenças prontas para comunicação.

frontend_tea_tcc.py:

Interface gráfica desenvolvida com a framework Flet, configurada em dimensões proporcionais a um smartphone (430x840).

Tela 0 (Autenticação): Gestão de sessão com login e registro de novos usuários validados diretamente no SQLite.

Aba 1 (Prancha de Comunicação): Montagem dinâmica de sentenças por chips categorizados por cores (Pronomes, Verbos, Emoções, etc.), além de botões para cadastro de novas palavras e otimização assistida por IA.

Aba 2 (Frases Prontas): Histórico de frases salvas com suporte a favoritar mensagens para fixação no topo e reprodução rápida em áudio.

Aba 3 (Pictogramas Visuais): Grade interativa com recursos visuais e semânticos para comunicação rápida por associação direta.

Aba 4 (Crise / SOS): Painel do perfil, instruções personalizadas de manejo em episódios de hipersensibilidade sensorial e acionamento de emergência.

preview_tcc.html:

Protótipo estático das interfaces renderizado em HTML/CSS para documentação monográfica ou slides de apresentação para a banca examinadora.

.gitignore:

Filtra o controle de versões para ignorar binários temporários (__pycache__/, .pyc), arquivos de ambiente e a base de dados gerada localmente (sistema_tea.db).

⚙️ Tecnologias Utilizadas

Linguagem: Python (v3.10 ou superior)

Interface Gráfica: Flet

Banco de Dados: SQLite3 (nativo do Python)

Síntese Vocal (TTS): pyttsx3

API de LLM: google-genai (Opcional - Gemini 3.8 Flash)

🚀 Como Iniciar do Zero em um Novo Computador

1. Clonar o Repositório

Abra o terminal (Prompt de Comando, PowerShell ou Terminal do VS Code) e execute:

git clone https://github.com/Evechdvl/sistema-comunicacao-tea-caa.git
cd sistema-comunicacao-tea-caa


2. Criar o Ambiente Virtual (venv)

O ambiente virtual isola as dependências do projeto para evitar conflitos de versão no sistema operacional:

No Windows (PowerShell ou CMD):

python -m venv venv


No Linux / macOS:

python3 -m venv venv


3. Ativar o Ambiente Virtual

No Windows via PowerShell:

.\venv\Scripts\activate


Nota sobre erro de segurança no PowerShell: Caso surja a mensagem de que a execução de scripts foi desabilitada neste sistema, execute o comando abaixo uma única vez para liberar scripts locais assinados e tente ativar novamente:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate


No Windows via Prompt de Comando (CMD):

.\venv\Scripts\activate.bat


No Linux / macOS:

source venv/bin/activate


Quando ativado com sucesso, o terminal exibirá o prefixo (venv) no início da linha de comando.

4. Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas requeridas pelo projeto:

pip install flet pyttsx3 google-genai


5. (Opcional) Configurar a Chave da API Gemini

Para ativar o polimento assistido de frases com Inteligência Artificial, configure sua chave do Google AI Studio:

Windows (PowerShell):

$env:GEMINI_API_KEY="sua_chave_aqui"


Windows (CMD):

set GEMINI_API_KEY=sua_chave_aqui


Linux / macOS:

export GEMINI_API_KEY="sua_chave_aqui"


Caso não configure a chave, a aplicação funcionará normalmente no modo padrão 100% offline.

6. Executar o Aplicativo

Inicie a aplicação executando o ponto de entrada da interface:

python frontend_tea_tcc.py


🔑 Credenciais para Demonstração (Banca de TCC)

Na primeira execução, o arquivo sistema_tea.db será gerado automaticamente. Para acelerar os testes durante a apresentação, utilize a conta pré-configurada:

E-mail: lucas@email.com

Senha: 123456
