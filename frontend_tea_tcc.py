import flet as ft
import threading
from backend_tea_tcc import (
    DatabaseManager,
    Biblioteca,
    Modulo,
    Palavra,
    Imagem,
    Frase,
    Comunicacao,
    Usuario,
    InformacaoCrise,
    ContatoEmergencia,
    sugerir_frase_com_ia,
)

# =====================================================================
# RESOLUÇÃO DINÂMICA DE COMPONENTES (Compatibilidade Flet)
# =====================================================================
def _obter_botao(nome):
    if hasattr(ft, nome):
        return getattr(ft, nome)
    if hasattr(ft, "Button"):
        return getattr(ft, "Button")
    return getattr(ft, "ElevatedButton", getattr(ft, "FilledButton", None))

ElevatedButtonCls = _obter_botao("ElevatedButton")
FilledButtonCls = _obter_botao("FilledButton")
OutlinedButtonCls = _obter_botao("OutlinedButton")
TextButtonCls = _obter_botao("TextButton")

def criar_opcao(chave: str, texto: str = None):
    rotulo = texto if texto else chave
    if hasattr(ft, "DropdownOption"):
        return ft.DropdownOption(key=str(chave), text=rotulo)
    if hasattr(ft, "dropdown") and hasattr(ft.dropdown, "Option"):
        return ft.dropdown.Option(str(chave), rotulo)
    return ft.dropdown.Option(str(chave))


def main(page: ft.Page):
    DatabaseManager.inicializar_banco()

    page.title = "CAA TEA - Sistema de Apoio à Comunicação"
    page.theme_mode = ft.ThemeMode.LIGHT

    try:
        if hasattr(page, "window") and page.window is not None:
            page.window.width = 430
            page.window.height = 840
        else:
            page.window_width = 430
            page.window_height = 840
    except Exception:
        pass

    page.padding = 0

    biblioteca = Biblioteca()
    comunicador = Comunicacao()
    usuario_atual: Usuario = Usuario.carregar_usuario_padrao()

    palavras_montagem: list[Palavra] = []
    modulos_disponiveis = biblioteca.acessar_modulos()
    modulo_selecionado: Modulo = modulos_disponiveis[0]

    def emitir_comunicacao_visual(texto_falado: str, cor=ft.Colors.INDIGO):
        sb = ft.SnackBar(
            content=ft.Row([
                ft.Icon(ft.Icons.VOLUME_UP, color=ft.Colors.WHITE, size=30),
                ft.Text(f"{texto_falado}", size=15, weight=ft.FontWeight.BOLD, expand=True),
            ]),
            bgcolor=cor,
            duration=3000,
        )
        if hasattr(page, "open"):
            page.open(sb)
        else:
            page.snack_bar = sb
            page.snack_bar.open = True
            page.update()

    # =====================================================================
    # TELA 0: AUTENTICAÇÃO REAL (LOGIN E CADASTRO)
    # =====================================================================
    modo_cadastro = False

    input_login_nome = ft.TextField(label="Nome Completo", prefix_icon=ft.Icons.PERSON_OUTLINE, visible=False, border_radius=12)
    input_login_email = ft.TextField(label="E-mail", value="lucas@email.com", prefix_icon=ft.Icons.EMAIL_OUTLINED, border_radius=12)
    input_login_senha = ft.TextField(label="Senha", value="123456", password=True, prefix_icon=ft.Icons.LOCK_OUTLINE, border_radius=12)
    texto_erro_login = ft.Text("", color=ft.Colors.RED, size=13, weight=ft.FontWeight.BOLD, visible=False)
    titulo_form_auth = ft.Text("Acesso ao Sistema", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO)
    btn_acao_principal_auth = FilledButtonCls("Entrar no Aplicativo", icon=ft.Icons.LOGIN, bgcolor=ft.Colors.INDIGO, width=float("inf"), height=48)
    btn_alternar_modo_auth = TextButtonCls("Não possui conta? Cadastre-se aqui")

    def alternar_modo_autenticacao(e):
        nonlocal modo_cadastro
        modo_cadastro = not modo_cadastro
        texto_erro_login.visible = False
        if modo_cadastro:
            titulo_form_auth.value = "Criar Nova Conta"
            input_login_nome.visible = True
            input_login_nome.value = ""
            input_login_email.value = ""
            input_login_senha.value = ""
            btn_acao_principal_auth.text = "Cadastrar e Entrar"
            btn_acao_principal_auth.icon = ft.Icons.PERSON_ADD
            btn_alternar_modo_auth.text = "Já possui conta? Faça login"
        else:
            titulo_form_auth.value = "Acesso ao Sistema"
            input_login_nome.visible = False
            input_login_email.value = "lucas@email.com"
            input_login_senha.value = "123456"
            btn_acao_principal_auth.text = "Entrar no Aplicativo"
            btn_acao_principal_auth.icon = ft.Icons.LOGIN
            btn_alternar_modo_auth.text = "Não possui conta? Cadastre-se aqui"
        page.update()

    def processar_autenticacao(e):
        nonlocal usuario_atual
        email = (input_login_email.value or "").strip()
        senha = (input_login_senha.value or "").strip()

        if modo_cadastro:
            nome = (input_login_nome.value or "").strip()
            if not nome or not email or not senha:
                texto_erro_login.value = "⚠️ Preencha todos os campos."
                texto_erro_login.visible = True
                page.update()
                return
            novo_u = Usuario(0, nome, email, senha)
            novo_u.cadastrar()
            usuario_atual = novo_u
            entrar_no_sistema()
            emitir_comunicacao_visual(f"Conta criada! Bem-vindo(a), {usuario_atual.nome}!", ft.Colors.GREEN)
        else:
            user_autenticado = Usuario.autenticar(email, senha)
            if user_autenticado:
                usuario_atual = user_autenticado
                texto_erro_login.visible = False
                entrar_no_sistema()
                emitir_comunicacao_visual(f"Bem-vindo(a), {usuario_atual.nome}!", ft.Colors.GREEN)
            else:
                texto_erro_login.value = "❌ E-mail ou senha incorretos."
                texto_erro_login.visible = True
                page.update()

    btn_acao_principal_auth.on_click = processar_autenticacao
    btn_alternar_modo_auth.on_click = alternar_modo_autenticacao

    tela_login = ft.Container(
        expand=True,
        bgcolor="#f5f7fb",
        padding=24,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Card(
                    elevation=6,
                    content=ft.Container(
                        padding=24,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        content=ft.Column(
                            tight=True,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=14,
                            controls=[
                                ft.CircleAvatar(radius=38, bgcolor="#e8eaf6", content=ft.Icon(ft.Icons.RECORD_VOICE_OVER, size=40, color=ft.Colors.INDIGO)),
                                ft.Text("Apoio à Comunicação TEA", size=21, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO, text_align=ft.TextAlign.CENTER),
                                ft.Text("Comunicação Alternativa e Aumentativa (CAA)", size=12, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER),
                                ft.Divider(),
                                titulo_form_auth,
                                input_login_nome,
                                input_login_email,
                                input_login_senha,
                                texto_erro_login,
                                btn_acao_principal_auth,
                                btn_alternar_modo_auth,
                                ft.Container(
                                    padding=8, bgcolor="#e8eaf6", border_radius=8,
                                    content=ft.Text("💡 Demo TCC: lucas@email.com | Senha: 123456", size=11, color=ft.Colors.INDIGO, text_align=ft.TextAlign.CENTER),
                                ),
                            ],
                        ),
                    ),
                )
            ],
        ),
    )

   # =====================================================================
    # ABA 1: MONTAR FRASE & IA
    # =====================================================================
    visor_frase = ft.Text("Toque nas palavras abaixo para montar sua frase...", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO)
    barra_progresso_ia = ft.ProgressBar(visible=False, color=ft.Colors.INDIGO, bgcolor=ft.Colors.INDIGO_50, height=4)
    grid_palavras = ft.Row(wrap=True, spacing=8, run_spacing=8)
    input_nova_palavra = ft.TextField(label="Nova palavra", expand=True, height=48)
    input_cat_palavra = ft.Dropdown(
        label="Categoria", width=145, value="Substantivo",
        options=[
            criar_opcao("Pronome"),
            criar_opcao("Verbo"),
            criar_opcao("Substantivo"),
            criar_opcao("Emoção"),
            criar_opcao("Social"),
        ],
    )

    # Diálogo de confirmação para exclusão de palavra
    modal_remover_palavra = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir Palavra"),
        content=ft.Text(""),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def confirmar_remover_palavra(pal: Palavra):
        def fechar_dialogo(e):
            if hasattr(page, "close"):
                page.close(modal_remover_palavra)
            else:
                modal_remover_palavra.open = False
                page.update()

        def executar_remocao(e):
            try:
                # 1. Remove do banco SQLite
                pal.remover()

                # 2. Atualiza a lista em memória do módulo ativo
                if pal in modulo_selecionado.palavras:
                    modulo_selecionado.palavras.remove(pal)

                # 3. Se a palavra estiver selecionada no visor, remove também
                if pal in palavras_montagem:
                    palavras_montagem[:] = [item for item in palavras_montagem if item.id != pal.id]
                    atualizar_visor()

                # 4. Fecha modal e recarrega a grade
                if hasattr(page, "close"):
                    page.close(modal_remover_palavra)
                else:
                    modal_remover_palavra.open = False

                carregar_palavras_do_modulo()
                emitir_comunicacao_visual(f"Palavra '{pal.texto}' removida com sucesso!", ft.Colors.BLUE)
            except Exception as err:
                if hasattr(page, "close"):
                    page.close(modal_remover_palavra)
                else:
                    modal_remover_palavra.open = False
                emitir_comunicacao_visual(f"Erro ao remover palavra: {err}", ft.Colors.RED)
            page.update()

        modal_remover_palavra.content = ft.Text(f'Tem certeza de que deseja excluir a palavra "{pal.texto}"?')
        modal_remover_palavra.actions = [
            ft.TextButton("Cancelar", on_click=fechar_dialogo),
            ft.FilledButton("Excluir", bgcolor=ft.Colors.RED_600, on_click=executar_remocao),
        ]

        if hasattr(page, "open"):
            page.open(modal_remover_palavra)
        else:
            modal_remover_palavra.open = True
            if modal_remover_palavra not in page.overlay:
                page.overlay.append(modal_remover_palavra)
            page.update()

    # 1. Definição do botão de ajuste com IA
    btn_polir_ia = OutlinedButtonCls(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                ft.Text("✨ Ajustar Frase", weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        width=float("inf"),
        height=48,
        tooltip="Ajusta a frase com Inteligência Artificial (Baixo consumo)",
    )

    def atualizar_visor():
        if palavras_montagem:
            visor_frase.value = " ".join([p.texto for p in palavras_montagem])
        else:
            visor_frase.value = "Toque nas palavras abaixo para montar sua frase..."
        page.update()

    def selecionar_palavra(p: Palavra):
        palavras_montagem.append(p)
        atualizar_visor()

    def carregar_palavras_do_modulo():
        grid_palavras.controls.clear()
        for p in modulo_selecionado.palavras:
            cor_chip = "#bbdefb"
            if p.categoria == "Verbo":
                cor_chip = "#c8e6c9"
            elif p.categoria == "Emoção":
                cor_chip = "#ffecb3"

            # Componente em container com suporte a toque para seleção e botão de exclusão
            item_palavra = ft.Container(
                bgcolor=cor_chip,
                border_radius=12,
                padding=ft.Padding(left=12, top=4, right=4, bottom=4),
                content=ft.Row(
                    tight=True,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        # Área de toque para selecionar a palavra
                        ft.Container(
                            padding=ft.Padding(left=4, top=6, right=4, bottom=6),
                            ink=True,
                            on_click=lambda e, pal=p: selecionar_palavra(pal),
                            content=ft.Column(
                                [
                                    ft.Text(p.texto, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                                    ft.Text(p.categoria, size=10, color=ft.Colors.GREY_800),
                                ],
                                spacing=1,
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                            ),
                        ),
                        # Botão discreto para exclusão com confirmação
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            icon_color=ft.Colors.GREY_700,
                            tooltip=f"Excluir '{p.texto}'",
                            on_click=lambda e, pal=p: confirmar_remover_palavra(pal),
                        ),
                    ],
                ),
            )
            grid_palavras.controls.append(item_palavra)
        page.update()

    def trocar_modulo(e):
        nonlocal modulo_selecionado
        id_mod = int(dropdown_modulos.value)
        for m in modulos_disponiveis:
            if m.id == id_mod:
                modulo_selecionado = m
                break
        carregar_palavras_do_modulo()

    dropdown_modulos = ft.Dropdown(
        label="Módulo da Biblioteca",
        value=str(modulo_selecionado.id),
        options=[criar_opcao(str(m.id), f"{m.nome} - {m.descricao}") for m in modulos_disponiveis],
    )
    if hasattr(dropdown_modulos, "on_select"):
        dropdown_modulos.on_select = trocar_modulo
    else:
        dropdown_modulos.on_change = trocar_modulo

    def acao_montar_e_comunicar(e):
        texto_para_falar = (visor_frase.value or "").strip()

        # Evita falar o texto padrão de placeholder
        if not texto_para_falar or texto_para_falar == "Toque nas palavras abaixo para montar sua frase...":
            emitir_comunicacao_visual("Selecione ao menos uma palavra primeiro!", ft.Colors.ORANGE)
            return

        # 1. Salva no banco de dados a frase real
        nova_frase = Frase(
            modulo_id=modulo_selecionado.id,
            usuario_id=usuario_atual.id,
            texto=texto_para_falar,
        )
        nova_frase.salvar()

        # 2. Emite a voz com o texto atualizado do visor
        saida = comunicador.comunicar(texto_para_falar)
        emitir_comunicacao_visual(f'Comunicação: "{saida}"')
        carregar_lista_frases()

    def acao_polir_com_ia(e):
        if not palavras_montagem:
            emitir_comunicacao_visual("Monte uma frase com palavras antes de ajustar!", ft.Colors.ORANGE)
            return

        texto_bruto = " ".join([p.texto for p in palavras_montagem])

        # Ativa feedback visual de carregamento
        btn_polir_ia.disabled = True
        btn_polir_ia.content = ft.Row(
            [
                ft.ProgressRing(width=16, height=16, stroke_width=2, color=ft.Colors.INDIGO),
                ft.Text("Otimizando...", weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )
        barra_progresso_ia.visible = True
        visor_frase.value = f'⏳ A IA está estruturando a frase: "{texto_bruto}"...'
        page.update()

        def processar_ia_background():
            try:
                texto_otimizado = sugerir_frase_com_ia(texto_bruto)
                visor_frase.value = texto_otimizado
                emitir_comunicacao_visual("✨ Frase ajustada com sucesso!", ft.Colors.GREEN)
            except Exception as err:
                visor_frase.value = texto_bruto
                emitir_comunicacao_visual(f"Não foi possível ajustar: {err}", ft.Colors.RED)
            finally:
                barra_progresso_ia.visible = False
                btn_polir_ia.disabled = False
                btn_polir_ia.content = ft.Row(
                    [
                        ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                        ft.Text("✨ Ajustar Frase", weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                )
                page.update()

        threading.Thread(target=processar_ia_background, daemon=True).start()

    btn_polir_ia.on_click = acao_polir_com_ia

    def acao_limpar_visor(e):
        palavras_montagem.clear()
        atualizar_visor()

    def acao_adicionar_palavra(e):
        texto = (input_nova_palavra.value or "").strip()
        if texto:
            nova_p = Palavra(0, texto, input_cat_palavra.value, modulo_selecionado.id)
            nova_p.adicionar()
            modulo_selecionado.palavras.append(nova_p)
            input_nova_palavra.value = ""
            carregar_palavras_do_modulo()

    aba_montar = ft.Container(
        padding=16,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Prancha de Comunicação (CAA)", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Column([
                        visor_frase,
                        barra_progresso_ia,
                    ], spacing=10),
                    padding=16,
                    bgcolor="#e8eaf6",
                    border_radius=12,
                    width=float("inf"),
                ),
                # Linha 1: Botão principal de Comunicar e botão Limpar
                ft.Row([
                    FilledButtonCls(
                        "Comunicar",
                        icon=ft.Icons.RECORD_VOICE_OVER,
                        bgcolor=ft.Colors.GREEN,
                        expand=True,
                        height=48,
                        on_click=acao_montar_e_comunicar,
                    ),
                    OutlinedButtonCls(
                        "Limpar",
                        icon=ft.Icons.BACKSPACE_OUTLINED,
                        height=48,
                        on_click=acao_limpar_visor,
                    ),
                ]),
                # Linha 2: Botão de Ajustar Frase posicionado logo abaixo
                btn_polir_ia,
                ft.Divider(),
                dropdown_modulos,
                ft.Text("Toque nas palavras para montar:", size=14, color=ft.Colors.GREY),
                grid_palavras,
                ft.Divider(),
                ft.Text("Cadastrar Nova Palavra:", weight=ft.FontWeight.BOLD, size=14),
                ft.Row([
                    input_nova_palavra,
                    input_cat_palavra,
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE,
                        icon_color=ft.Colors.INDIGO,
                        icon_size=36,
                        on_click=acao_adicionar_palavra,
                    ),
                ]),
            ],
        ),
    )

    # =====================================================================
    # ABA 2: FRASES PRONTAS
    # =====================================================================
    lista_frases_view = ft.Column(spacing=8)

    def alternar_favorito(frase_obj: Frase):
        frase_obj.favorita = not frase_obj.favorita
        frase_obj.salvar()
        carregar_lista_frases()

    def deletar_frase(frase_obj: Frase):
        frase_obj.excluir()
        carregar_lista_frases()

    def carregar_lista_frases():
        lista_frases_view.controls.clear()
        for f in biblioteca.acessar_frases():
            icone_fav = ft.Icons.STAR if f.favorita else ft.Icons.STAR_BORDER
            cor_fav = ft.Colors.AMBER if f.favorita else ft.Colors.GREY
            card = ft.Card(content=ft.Container(padding=10, content=ft.Row([
                ft.IconButton(icon=icone_fav, icon_color=cor_fav, on_click=lambda e, fr=f: alternar_favorito(fr)),
                ft.Column([ft.Text(f.texto, size=16, weight=ft.FontWeight.BOLD), ft.Text(f"Criada em: {f.data_criacao}", size=11, color=ft.Colors.GREY)], expand=True),
                ft.IconButton(icon=ft.Icons.VOLUME_UP, icon_color=ft.Colors.GREEN, on_click=lambda e, fr=f: emitir_comunicacao_visual(f'Comunicação: "{comunicador.utilizar_texto(frase=fr)}"')),
                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED, on_click=lambda e, fr=f: deletar_frase(fr)),
            ])))
            lista_frases_view.controls.append(card)
        page.update()

    aba_frases = ft.Container(padding=16, content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
        ft.Row([ft.Text("Frases Prontas e Salvas", size=20, weight=ft.FontWeight.BOLD, expand=True), ft.Icon(ft.Icons.STAR, color=ft.Colors.AMBER), ft.Text("Favoritas no topo", size=12)]),
        ft.Divider(), lista_frases_view
    ]))

    # =====================================================================
    # ABA 3: IMAGENS CAA (Pictogramas com Cadastro Dinâmico e Diagnóstico)
    # =====================================================================
    grid_imagens = ft.GridView(
        expand=False, 
        max_extent=180, 
        child_aspect_ratio=1.1, 
        spacing=12, 
        run_spacing=12
    )

    EMOJIS_PADRAO = [
        "🍎", "💧", "🥪", "🍌", "🥛", "🍪",
        "🚽", "🛁", "🛏️", "👕", "👟", "💊",
        "😀", "😢", "😠", "😨", "😴", "🤒",
        "🏠", "🏫", "🚗", "🚶", "🛑", "⏰",
        "🎨", "🧩", "⚽", "📖", "🎧", "🧸",
        "👋", "👍", "👎", "🙏", "✋", "🤝",
    ]

    estado_emoji = {"atual": "🍎"}
    preview_emoji = ft.Text(estado_emoji["atual"], size=38)

    # Texto fixo de status para garantir feedback visível caso a SnackBar falhe
    status_feedback_cadastro = ft.Text("", size=13, weight=ft.FontWeight.BOLD, visible=False)

    input_nome_imagem = ft.TextField(
        label="Nome do Pictograma",
        hint_text="Ex: Maçã, Banheiro, Dormir",
        expand=True,
        height=48,
    )
    input_desc_imagem = ft.TextField(
        label="Descritor / Contexto",
        hint_text="Ex: Quero comer fruta fresca",
        expand=True,
        height=48,
    )

    def selecionar_emoji_padrao(e, emoji: str):
        print(f"[DEBUG] Emoji selecionado: {emoji}")
        estado_emoji["atual"] = emoji
        preview_emoji.value = emoji
        page.update()

    seletor_emojis = ft.Row(
        scroll=ft.ScrollMode.ADAPTIVE,
        spacing=6,
        controls=[
            ft.Container(
                content=ft.Text(em, size=24),
                tooltip=f"Selecionar {em}",
                padding=6,
                border_radius=8,
                ink=True,
                on_click=lambda e, emoji=em: selecionar_emoji_padrao(e, emoji),
            )
            for em in EMOJIS_PADRAO
        ],
    )
    
    # Diálogo de confirmação para exclusão
    modal_confirmar_exclusao = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir Pictograma"),
        content=ft.Text(""),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def confirmar_remover_pictograma(img: Imagem):
        print(f"\n--- [DEBUG] Botão de lixeira acionado para o card: id={img.id}, nome='{img.nome}' ---")

        def fechar_dialogo(e):
            print("[DEBUG] Exclusão cancelada pelo usuário.")
            # Fecha com suporte a versões novas (page.close) e legadas (modal.open = False)
            if hasattr(page, "close"):
                page.close(modal_confirmar_exclusao)
            else:
                modal_confirmar_exclusao.open = False
                page.update()

        def executar_remocao(e):
            print(f"[DEBUG] Confirmada exclusão do registro id={img.id} ('{img.nome}') no SQLite...")
            try:
                # 1. Executa a remoção no backend
                img.remover()
                print("[DEBUG] Execução de img.remover() concluída com sucesso no banco!")

                # 2. Fecha o modal primeiro
                if hasattr(page, "close"):
                    page.close(modal_confirmar_exclusao)
                else:
                    modal_confirmar_exclusao.open = False

                # 3. Recarrega a grade e atualiza a interface
                carregar_pictogramas()

                msg_sucesso = f"Pictograma '{img.nome}' removido com sucesso!"
                print(f"[SUCESSO] {msg_sucesso}")
                status_feedback_cadastro.value = f"🗑️ {msg_sucesso}"
                status_feedback_cadastro.color = ft.Colors.BLUE_700
                status_feedback_cadastro.visible = True
                emitir_comunicacao_visual(msg_sucesso, ft.Colors.BLUE)

            except Exception as err:
                import traceback
                print("\n[ERRO CRÍTICO AO EXCLUIR IMAGEM]:")
                print(traceback.format_exc())

                if hasattr(page, "close"):
                    page.close(modal_confirmar_exclusao)
                else:
                    modal_confirmar_exclusao.open = False

                msg_erro = f"❌ Erro ao excluir pictograma: {err}"
                status_feedback_cadastro.value = msg_erro
                status_feedback_cadastro.color = ft.Colors.RED_700
                status_feedback_cadastro.visible = True
                emitir_comunicacao_visual(msg_erro, ft.Colors.RED)

            page.update()

        # Configuração do conteúdo do modal
        modal_confirmar_exclusao.content = ft.Text(f'Tem certeza de que deseja excluir o pictograma "{img.nome}"?')
        modal_confirmar_exclusao.actions = [
            ft.TextButton("Cancelar", on_click=fechar_dialogo),
            ft.FilledButton("Excluir", bgcolor=ft.Colors.RED_600, on_click=executar_remocao),
        ]

        # Abertura compatível com todas as versões do Flet:
        if hasattr(page, "open"):
            page.open(modal_confirmar_exclusao)
        else:
            modal_confirmar_exclusao.open = True
            if modal_confirmar_exclusao not in page.overlay:
                page.overlay.append(modal_confirmar_exclusao)
            page.update()

        print("[DEBUG] Modal de confirmação aberto na interface.")

    def carregar_pictogramas():
        grid_imagens.controls.clear()
        for img in Imagem.listar_todas():
            corpo_card = ft.Container(
                padding=12,
                ink=True,
                border_radius=10,
                on_click=lambda e, im=img: emitir_comunicacao_visual(f'Comunicação: "{comunicador.comunicar(im.nome)}"'),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(img.caminho, size=40),
                        ft.Text(img.nome, size=15, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ft.Text(img.descricao, size=11, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER, max_lines=2),
                    ],
                ),
            )

            btn_deletar = ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED_400,
                icon_size=20,
                tooltip=f"Excluir '{img.nome}'",
                on_click=lambda e, im=img: confirmar_remover_pictograma(im),
            )

            card_img = ft.Card(
                elevation=3,
                content=ft.Stack(
                    controls=[
                        corpo_card,
                        ft.Container(
                            content=btn_deletar,
                            alignment=ft.Alignment(1, -1),
                            padding=2,
                        ),
                    ],
                ),
            )
            grid_imagens.controls.append(card_img)
        page.update()

    # Função de diagnóstico e cadastro
    def acao_cadastrar_imagem(e):
        print("\n--- [DEBUG] Botão de cadastrar pictograma clicado! ---")
        
        nome = (input_nome_imagem.value or "").strip()
        descritor = (input_desc_imagem.value or "").strip()

        print(f"[DEBUG] Dados capturados -> Emoji: '{estado_emoji['atual']}', Nome: '{nome}', Descritor: '{descritor}'")

        if not nome:
            msg = "⚠️ Atenção: Preencha o Nome do pictograma antes de salvar!"
            print(f"[AVISO] {msg}")
            status_feedback_cadastro.value = msg
            status_feedback_cadastro.color = ft.Colors.ORANGE_800
            status_feedback_cadastro.visible = True
            emitir_comunicacao_visual(msg, ft.Colors.ORANGE)
            page.update()
            return

        if not descritor:
            msg = "⚠️ Atenção: Preencha o Descritor antes de salvar!"
            print(f"[AVISO] {msg}")
            status_feedback_cadastro.value = msg
            status_feedback_cadastro.color = ft.Colors.ORANGE_800
            status_feedback_cadastro.visible = True
            emitir_comunicacao_visual(msg, ft.Colors.ORANGE)
            page.update()
            return

        try:
            print("[DEBUG] Tentando persistir no banco SQLite...")
            nova_img = Imagem(
                caminho=estado_emoji["atual"],
                nome=nome,
                descricao=descritor,
            )
            nova_img.adicionar()
            print("[DEBUG] Imagem persistida com sucesso!")

            # Limpar campos de texto
            input_nome_imagem.value = ""
            input_desc_imagem.value = ""
            
            # Recarregar lista visual
            carregar_pictogramas()

            sucesso_msg = f"✅ Sucesso: Pictograma '{nome}' cadastrado com sucesso!"
            print(f"[SUCESSO] {sucesso_msg}")
            status_feedback_cadastro.value = sucesso_msg
            status_feedback_cadastro.color = ft.Colors.GREEN_700
            status_feedback_cadastro.visible = True
            emitir_comunicacao_visual(sucesso_msg, ft.Colors.GREEN)

        except Exception as err:
            import traceback
            erro_detalhado = traceback.format_exc()
            msg_erro = f"❌ Erro ao cadastrar pictograma: {err}"
            print("\n[ERRO CRÍTICO NO BANCO/BACKEND]:")
            print(erro_detalhado)

            status_feedback_cadastro.value = f"❌ Erro: {err} (Veja os detalhes no terminal)"
            status_feedback_cadastro.color = ft.Colors.RED_700
            status_feedback_cadastro.visible = True
            emitir_comunicacao_visual(msg_erro, ft.Colors.RED)

        page.update()

    # Botão com estilo de botão preenchido (FilledButton) para garantir área de clique evidente
    btn_cadastrar_imagem = ft.FilledButton(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.ADD_CIRCLE, size=20),
                ft.Text("Cadastrar", weight=ft.FontWeight.BOLD),
            ],
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        bgcolor=ft.Colors.INDIGO,
        height=48,
        on_click=acao_cadastrar_imagem,
    )

    aba_imagens = ft.Container(
        padding=16,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Pictogramas Visuais (CAA)", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("Toque em um cartão visual para comunicação rápida:", size=13, color=ft.Colors.GREY),
                ft.Divider(),
                grid_imagens,
                ft.Divider(),
                ft.Text("Cadastrar Novo Pictograma:", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("1. Escolha um emoji da paleta padrão:", size=12, color=ft.Colors.GREY),
                seletor_emojis,
                ft.Row(
                    [
                        ft.Container(
                            content=preview_emoji,
                            padding=8,
                            bgcolor="#e8eaf6",
                            border_radius=10,
                            alignment=ft.Alignment(0, 0),
                            width=60,
                            height=60,
                        ),
                        ft.Column(
                            [
                                input_nome_imagem,
                                input_desc_imagem,
                            ],
                            expand=True,
                            spacing=8,
                        ),
                        btn_cadastrar_imagem,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                # Linha de diagnóstico direto na tela
                status_feedback_cadastro,
            ],
        ),
    )

    # =====================================================================
    # ABA 4: CRISE / SOS (COM CRUD DE CARTÕES DE CRISE)
    # =====================================================================
    coluna_crises = ft.Column(spacing=10)
    coluna_contatos = ft.Column(spacing=8)
    titulo_perfil_nome = ft.Text("", weight=ft.FontWeight.BOLD)
    subtitulo_perfil_email = ft.Text("")

    # Campos do formulário (Cadastro e Edição)
    input_crise_gatilho = ft.TextField(label="Gatilho / Motivo", hint_text="Ex: Barulhos altos, Multidão", height=48)
    input_crise_sinais = ft.TextField(label="Sinais da Crise", hint_text="Ex: Cobrir os ouvidos, agitação motora", height=48)
    input_crise_orientacoes = ft.TextField(label="Como agir (Instruções)", multiline=True, min_lines=2, max_lines=3)
    info_crise_em_edicao = {"objeto": None}

    def fechar_modal_crise(e=None):
        if hasattr(page, "close"):
            page.close(modal_form_crise)
        else:
            modal_form_crise.open = False
            page.update()

    def salvar_info_crise(e):
        gatilho = (input_crise_gatilho.value or "").strip()
        sinais = (input_crise_sinais.value or "").strip()
        orientacoes = (input_crise_orientacoes.value or "").strip()

        if not gatilho or not orientacoes:
            emitir_comunicacao_visual("Preencha ao menos o Gatilho e as Orientações!", ft.Colors.ORANGE)
            return

        try:
            if info_crise_em_edicao["objeto"]:
                item = info_crise_em_edicao["objeto"]
                item.descricao = gatilho
                item.sinais = sinais
                item.orientacoes = orientacoes
                item.salvar()
                emitir_comunicacao_visual("Cartão de crise atualizado com sucesso!", ft.Colors.GREEN)
            else:
                novo_item = InformacaoCrise(
                    id_info=0,
                    descricao=gatilho,
                    sinais=sinais,
                    orientacoes=orientacoes,
                    usuario_id=usuario_atual.id,
                )
                novo_item.salvar()
                emitir_comunicacao_visual("Novo cartão de crise cadastrado!", ft.Colors.GREEN)

            fechar_modal_crise()
            carregar_dados_usuario()
        except Exception as err:
            emitir_comunicacao_visual(f"Erro ao salvar cartão: {err}", ft.Colors.RED)

    modal_form_crise = ft.AlertDialog(
        modal=True,
        title=ft.Text("Cartão de Informações de Crise"),
        content=ft.Container(
            width=420,
            content=ft.Column(
                tight=True,
                spacing=10,
                controls=[
                    input_crise_gatilho,
                    input_crise_sinais,
                    input_crise_orientacoes,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=fechar_modal_crise),
            ft.FilledButton("Salvar", bgcolor=ft.Colors.INDIGO, on_click=salvar_info_crise),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_modal_novo_crise(e):
        info_crise_em_edicao["objeto"] = None
        modal_form_crise.title.value = "Novo Cartão de Crise"
        input_crise_gatilho.value = ""
        input_crise_sinais.value = ""
        input_crise_orientacoes.value = ""
        if hasattr(page, "open"):
            page.open(modal_form_crise)
        else:
            modal_form_crise.open = True
            if modal_form_crise not in page.overlay:
                page.overlay.append(modal_form_crise)
            page.update()

    def abrir_modal_editar_crise(item: InformacaoCrise):
        info_crise_em_edicao["objeto"] = item
        modal_form_crise.title.value = "Editar Cartão de Crise"
        input_crise_gatilho.value = item.descricao
        input_crise_sinais.value = item.sinais
        input_crise_orientacoes.value = item.orientacoes
        if hasattr(page, "open"):
            page.open(modal_form_crise)
        else:
            modal_form_crise.open = True
            if modal_form_crise not in page.overlay:
                page.overlay.append(modal_form_crise)
            page.update()

    modal_confirmar_deletar_crise = ft.AlertDialog(
        modal=True,
        title=ft.Text("Excluir Cartão de Crise"),
        content=ft.Text(""),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def confirmar_remover_crise(item: InformacaoCrise):
        def fechar_del(e):
            if hasattr(page, "close"):
                page.close(modal_confirmar_deletar_crise)
            else:
                modal_confirmar_deletar_crise.open = False
                page.update()

        def executar_del(e):
            try:
                item.remover()
                fechar_del(None)
                carregar_dados_usuario()
                emitir_comunicacao_visual("Cartão de crise excluído com sucesso!", ft.Colors.BLUE)
            except Exception as err:
                fechar_del(None)
                emitir_comunicacao_visual(f"Erro ao excluir cartão: {err}", ft.Colors.RED)

        modal_confirmar_deletar_crise.content = ft.Text(f'Tem certeza de que deseja excluir o cartão com gatilho "{item.descricao}"?')
        modal_confirmar_deletar_crise.actions = [
            ft.TextButton("Cancelar", on_click=fechar_del),
            ft.FilledButton("Excluir", bgcolor=ft.Colors.RED_600, on_click=executar_del),
        ]
        if hasattr(page, "open"):
            page.open(modal_confirmar_deletar_crise)
        else:
            modal_confirmar_deletar_crise.open = True
            if modal_confirmar_deletar_crise not in page.overlay:
                page.overlay.append(modal_confirmar_deletar_crise)
            page.update()

    def carregar_dados_usuario():
        titulo_perfil_nome.value = f"Usuário: {usuario_atual.nome}"
        subtitulo_perfil_email.value = f"E-mail: {usuario_atual.email}"

        coluna_crises.controls.clear()
        for c in usuario_atual.listar_informacoes_crise():
            card_crise = ft.Container(
                padding=12,
                bgcolor="#fff8e1",
                border_radius=8,
                border=ft.Border.all(1, "#ffe082"),
                content=ft.Column([
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(f"⚠️ Gatilho: {c.descricao}", weight=ft.FontWeight.BOLD, size=15, color=ft.Colors.AMBER_900),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.VOLUME_UP,
                                        icon_size=20,
                                        icon_color=ft.Colors.INDIGO,
                                        tooltip="Ouvir como agir",
                                        on_click=lambda e, item=c: emitir_comunicacao_visual(
                                            f'Comunicação: "{comunicador.comunicar(item.orientacoes)}"'
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT_OUTLINED,
                                        icon_size=20,
                                        icon_color=ft.Colors.GREY_700,
                                        tooltip="Editar cartão",
                                        on_click=lambda e, item=c: abrir_modal_editar_crise(item),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINE,
                                        icon_size=20,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Excluir cartão",
                                        on_click=lambda e, item=c: confirmar_remover_crise(item),
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ft.Text(f"Sinais: {c.sinais or 'Não especificado'}", size=13),
                    ft.Text(f"✅ Como agir: {c.orientacoes}", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_800),
                ], spacing=4),
            )
            coluna_crises.controls.append(card_crise)

        # Carrega a lista de contatos de emergência (inalterada)
        coluna_contatos.controls.clear()
        for ct in usuario_atual.listar_contatos_emergencia():
            coluna_contatos.controls.append(ft.Card(content=ft.Container(padding=12, content=ft.Row([
                ft.Column([
                    ft.Text(ct.nome, weight=ft.FontWeight.BOLD, size=16), 
                    ft.Text(f"{ct.descricao}\nTel: {ct.telefone}", size=13, color=ft.Colors.GREY)
                ], expand=True),
                FilledButtonCls("🚨 Acionar", bgcolor=ft.Colors.RED, on_click=lambda e, contato=ct: emitir_comunicacao_visual(contato.acionar(), ft.Colors.RED)),
            ]))))
        page.update()

    aba_usuario_crise = ft.Container(
        padding=16,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.ListTile(leading=ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON)), title=titulo_perfil_nome, subtitle=subtitulo_perfil_email),
                ft.Divider(),
                ft.Text("🚨 Contatos de Emergência", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                coluna_contatos,
                ft.Divider(),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("🛡️ Cartão de Informações de Crise (TEA)", size=18, weight=ft.FontWeight.BOLD),
                        ft.FilledButton(
                            "Novo Cartão",
                            icon=ft.Icons.ADD_CARD,
                            bgcolor=ft.Colors.INDIGO,
                            on_click=abrir_modal_novo_crise,
                        ),
                    ],
                ),
                coluna_crises,
            ],
        ),
    )

    # =====================================================================
    # NAVEGAÇÃO E SESSÃO
    # =====================================================================
    area_principal = ft.Container(content=tela_login, expand=True)

    def mudar_aba(e):
        idx = e.control.selected_index
        if idx == 0: carregar_palavras_do_modulo(); area_principal.content = aba_montar
        elif idx == 1: carregar_lista_frases(); area_principal.content = aba_frases
        elif idx == 2: carregar_pictogramas(); area_principal.content = aba_imagens
        elif idx == 3: carregar_dados_usuario(); area_principal.content = aba_usuario_crise
        page.update()

    def realizar_logout(e):
        page.appbar.visible = False
        page.navigation_bar.visible = False
        area_principal.content = tela_login
        page.update()

    def entrar_no_sistema():
        page.appbar.visible = True
        page.navigation_bar.visible = True
        page.navigation_bar.selected_index = 0
        carregar_palavras_do_modulo()
        area_principal.content = aba_montar
        page.update()

    page.appbar = ft.AppBar(
        title=ft.Text("Apoio à Comunicação TEA", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=18),
        bgcolor=ft.Colors.INDIGO, center_title=True, visible=False,
        actions=[ft.IconButton(icon=ft.Icons.LOGOUT, icon_color=ft.Colors.WHITE, tooltip="Sair", on_click=realizar_logout)]
    )

    page.navigation_bar = ft.NavigationBar(
        selected_index=0, visible=False, on_change=mudar_aba,
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.CHAT_BUBBLE_OUTLINE, label="Montar Frase"),
            ft.NavigationBarDestination(icon=ft.Icons.BOOKMARK_BORDER, label="Frases Prontas"),
            ft.NavigationBarDestination(icon=ft.Icons.IMAGE_OUTLINED, label="Imagens CAA"),
            ft.NavigationBarDestination(icon=ft.Icons.HEALTH_AND_SAFETY_OUTLINED, label="Crise / SOS"),
        ],
    )

    page.add(area_principal)


if __name__ == "__main__":
    ft.run(main)