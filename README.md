# 📱 Sistema de Apoio à Comunicação Alternativa e Aumentativa (CAA) para TEA

Sistema desenvolvido como base prática para Trabalho de Conclusão de Curso (TCC), voltado a fornecer ferramentas de Comunicação Alternativa e Aumentativa (CAA) para pessoas com Transtorno do Espectro Autista (TEA)[cite: 1, 2].

O aplicativo simula a interface de um dispositivo móvel[cite: 2], oferecendo montagem de sentenças guiada por categorias gramaticais[cite: 1, 2], pranchas visuais com pictogramas[cite: 1, 2], gestão de frases salvas[cite: 1, 2], cartões de orientação para momentos de desregulação sensorial/crise e botão de alerta para contatos de emergência[cite: 1, 2].

---

## 📂 Estrutura do Repositório

* **`backend_tea_tcc.py`**:
  * **Persistência de Dados (`DatabaseManager`):** Configura a base de dados relacional SQLite (`sistema_tea.db`) e popula dados iniciais (módulos, palavras, frases, imagens e utilizador de teste) de forma automática na primeira execução.
  * **Modelo de Domínio:** Implementa as classes de negócio mapeadas no diagrama UML: `Usuario`, `InformacaoCrise`, `ContatoEmergencia`, `Biblioteca`, `Modulo`, `Palavra`, `Imagem`, `Frase` e `Comunicacao`[cite: 3].
  * **Síntese de Voz:** Integração de áudio via motor TTS (`pyttsx3`) com mecanismo de contingência para execução silenciosa[cite: 3].
  * **Módulo de Inteligência Artificial (`sugerir_frase_com_ia`):** Função opcional de baixo consumo de tokens que conecta ao modelo `gemini-3.8-flash` para refinar e expandir construções curtas em frases polidas.

* **`frontend_tea_tcc.py`**:
  * Interface gráfica desenvolvida com a framework **Flet**, configurada em dimensões proporcionais a um smartphone (430x840)[cite: 2].
  * **Tela 0 (Autenticação):** Gestão de sessão com login e registo de novos utilizadores com validação em SQLite[cite: 3].
  * **Aba 1 (Prancha de Comunicação):** Montagem dinâmica de sentenças por chips categorizados por cores (Pronomes, Verbos, Emoções, etc.), além de botões para cadastro de palavras e otimização assistida por IA[cite: 1, 2].
  * **Aba 2 (Frases Prontas):** Gestão de histórico com capacidade de favoritar mensagens para fixação no topo e reprodução rápida em áudio[cite: 1, 2, 3].
  * **Aba 3 (Pictogramas Visuais):** Grelha interativa com recursos visuais e semânticos para comunicação rápida por associação direta[cite: 1, 2].
  * **Aba 4 (Crise / SOS):** Painel do perfil, instruções personalizadas de manejo em episódios de hipersensibilidade sensorial e acionamento de emergência[cite: 1, 2, 3].

* **`preview_tcc.html`**:
  * Protótipo estático das interfaces renderizado em HTML/CSS[cite: 1].
  * Apresenta os mockups completos das 5 telas do sistema lado a lado, servindo de recurso visual para documentação monográfica ou diapositivos de apresentação da banca[cite: 1].

* **`.gitignore`**:
  * Filtra o controlo de versões para ignorar binários temporários (`__pycache__/`, `.pyc`), arquivos de ambiente e a base de dados gerada localmente (`sistema_tea.db`).

---

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python (v3.10 ou superior)
* **Interface Gráfica:** [Flet](https://flet.dev/)
* **Base de Dados:** SQLite3 (nativo do Python)[cite: 3]
* **Síntese Vocal (TTS):** [pyttsx3](https://pypi.org/project/pyttsx3/)[cite: 3]
* **API de LLM:** [google-genai](https://pypi.org/project/google-genai/) (Opcional - Gemini 3.8 Flash)

---

## 🚀 Como Iniciar do Zero em um Novo Computador

### 1. Clonar o Repositório
Abra o terminal (Prompt de Comando, PowerShell ou Terminal do VS Code) e execute:
```bash
git clone [https://github.com/Evechdvl/sistema-comunicacao-tea-caa.git](https://github.com/Evechdvl/sistema-comunicacao-tea-caa.git)
cd SEU-REPOSITORIO