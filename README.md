# 📱 Sistema CAA TEA - Apoio à Comunicação Alternativa e Aumentativa

Projeto de TCC voltado ao desenvolvimento de um aplicativo acessível de **Comunicação Alternativa e Aumentativa (CAA)** para pessoas com Transtorno do Espectro Autista (TEA), construído com **Python**, **Flet** e integrado à **API do Google Gemini**.

---

## 🚀 Funcionalidades Principais

### 1. 🧩 Prancha de Comunicação Dinâmica
- Seleção visual de palavras categorizadas (Pronomes, Verbos, Substantivos, Emoções, Social).
- Visor de montagem de sentença em tempo real.
- Suporte à inclusão de novas palavras personalizadas por módulo.

### 2. ✨ Polimento Inteligente de Frases via IA (Google Gemini)
- Otimização automática de termos soltos ou abreviados em sentenças coesas, educadas e em primeira pessoa do singular.
- **Execução em Segundo Plano (Multi-threading):** O processamento da IA não trava a interface gráfica.
- **Indicadores de Estado em Tempo Real:** Barra de carregamento horizontal (`ProgressBar`) e botão com animação de progresso (`ProgressRing`) informando claramente quando o modelo está trabalhando.
- **Arquitetura de Alta Disponibilidade:** Fallback automático entre modelos de resposta rápida (`models/gemini-3.5-flash`, `models/gemini-3.1-flash-lite`, `models/gemini-3.8-flash`) com `thinking_budget` desativado para garantir latência mínima e evitar cortes de texto.
- **Contingência Offline:** Preserva o texto original sem quebra da aplicação em caso de instabilidade de conexão.

### 3. 🔊 Síntese de Voz (TTS - Text-to-Speech)
- Leitura em áudio de alta clareza via biblioteca `pyttsx3`.
- **Sincronização com a IA:** A voz reproduz fielmente a frase final refinada exibida no visor, salvando o histórico completo no banco de dados.

### 4. ⭐ Biblioteca e Frases Prontas
- Armazenamento local de sentenças criadas pelo usuário.
- Mecanismo de favoritos com priorização no topo da lista.
- Reprodução direta e exclusão de sentenças.

### 5. 🖼️ Pictogramas Visuais
- Grade de comunicação rápida por cartões visuais e simbologia CAA.

### 6. 🚨 Gestão de Crise e SOS
- Registro de gatilhos, sinais comportamentais e instruções de acolhimento.
- Acionamento imediato de contatos de emergência cadastrados.

### 7. 🔐 Autenticação e Perfis
- Sistema completo de login, cadastro e persistência de dados isolada por usuário.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.10+
- **Interface Gráfica:** [Flet](https://flet.dev/) (Flutter para Python)
- **Inteligência Artificial:** [Google GenAI SDK](https://github.com/google-gemini/deprecations) (`google-genai`)
- **Banco de Dados:** SQLite3
- **Síntese de Voz:** `pyttsx3`
- **Gestão de Ambiente:** `python-dotenv`

---

## 📋 Pré-requisitos e Instalação

### 1. Clonar o Repositório
```bash
git clone [https://github.com/Evechdvl/sistema-comunicacao-tea-caa.git](https://github.com/Evechdvl/sistema-comunicacao-tea-caa.git)
cd sistema-comunicacao-tea-caa
```

### 2. Criar e Ativar o Ambiente Virtual (`.venv`)
- **Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar as Dependências
Com o ambiente virtual ativado:
```bash
pip install flet pyttsx3 google-genai python-dotenv
```

---

## 🔑 Configuração da Chave de API (Gemini)

1. Obtenha uma chave de API gratuita no [Google AI Studio](https://aistudio.google.com/).
2. Na raiz do projeto, crie um arquivo chamado `.env`:
   ```env
   GEMINI_API_KEY=sua_chave_aqui
   ```
3. Garanta que o arquivo `.env` esteja presente no seu `.gitignore` para proteção das suas credenciais.

---

## ▶️ Como Executar a Aplicação

Certifique-se de que o ambiente virtual está ativo e execute:
```bash
python frontend_tea_tcc.py
```

### Credenciais para Teste Rápido (Demo):
- **E-mail:** `lucas@email.com`
- **Senha:** `123456`

---

## 📂 Estrutura do Projeto

```text
├── backend_tea_tcc.py      # Camada de dados SQLite, regras de negócio e integração com Gemini
├── frontend_tea_tcc.py     # Interface gráfica em Flet, navegação, threads e layout acessível
├── .env                    # Variáveis de ambiente (Chave de API do Gemini - não versionado)
├── .gitignore              # Configuração de arquivos ignorados pelo Git
└── README.md               # Documentação completa do projeto
```
