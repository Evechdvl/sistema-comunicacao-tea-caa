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

    btn_polir_ia = OutlinedButtonCls(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                ft.Text("✨ Polir IA", weight=ft.FontWeight.BOLD),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        ),
        height=48,
        tooltip="Melhora a frase com Inteligência Artificial (Baixo consumo)",
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

            btn = ElevatedButtonCls(
                content=ft.Column([
                    ft.Text(p.texto, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    ft.Text(p.categoria, size=10, color=ft.Colors.GREY),
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=cor_chip, height=58,
                on_click=lambda e, pal=p: selecionar_palavra(pal),
            )
            grid_palavras.controls.append(btn)
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

        # 1. Salva no banco de dados a frase real (seja a polida pela IA ou a montagem manual)
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
            emitir_comunicacao_visual("Monte uma frase com palavras antes de polir!", ft.Colors.ORANGE)
            return

        texto_bruto = " ".join([p.texto for p in palavras_montagem])

        # 1. Ativa imediatamente o visual de carregamento na tela
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

        # 2. Executa a requisição do Gemini em segundo plano (background thread)
        def processar_ia_background():
            try:
                texto_otimizado = sugerir_frase_com_ia(texto_bruto)
                visor_frase.value = texto_otimizado
                emitir_comunicacao_visual("✨ Frase otimizada com sucesso!", ft.Colors.GREEN)
            except Exception as err:
                visor_frase.value = texto_bruto
                emitir_comunicacao_visual(f"Não foi possível polir: {err}", ft.Colors.RED)
            finally:
                # 3. Restaura os botões quando a API responder
                barra_progresso_ia.visible = False
                btn_polir_ia.disabled = False
                btn_polir_ia.content = ft.Row(
                    [
                        ft.Icon(ft.Icons.AUTO_AWESOME, size=18),
                        ft.Text("✨ Polir IA", weight=ft.FontWeight.BOLD),
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
        if input_nova_palavra.value and input_nova_palavra.value.strip():
            nova_p = Palavra(0, input_nova_palavra.value.strip(), input_cat_palavra.value, modulo_selecionado.id)
            nova_p.adicionar()
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
                ft.Row([
                    FilledButtonCls("🔊 Comunicar", icon=ft.Icons.RECORD_VOICE_OVER, bgcolor=ft.Colors.GREEN, expand=True, height=48, on_click=acao_montar_e_comunicar),
                    btn_polir_ia,
                    OutlinedButtonCls("Limpar", icon=ft.Icons.BACKSPACE_OUTLINED, height=48, on_click=acao_limpar_visor),
                ]),
                ft.Divider(),
                dropdown_modulos,
                ft.Text("Toque nas palavras para montar:", size=14, color=ft.Colors.GREY),
                grid_palavras,
                ft.Divider(),
                ft.Text("Cadastrar Nova Palavra:", weight=ft.FontWeight.BOLD, size=14),
                ft.Row([input_nova_palavra, input_cat_palavra, ft.IconButton(icon=ft.Icons.ADD_CIRCLE, icon_color=ft.Colors.INDIGO, icon_size=36, on_click=acao_adicionar_palavra)]),
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
    # ABA 3: IMAGENS CAA (Container com on_click direto)
    # =====================================================================
    grid_imagens = ft.GridView(expand=False, max_extent=180, child_aspect_ratio=1.1, spacing=12, run_spacing=12)

    def carregar_pictogramas():
        grid_imagens.controls.clear()
        for img in Imagem.listar_todas():
            card_img = ft.Card(
                elevation=3,
                content=ft.Container(
                    padding=12,
                    on_click=lambda e, im=img: emitir_comunicacao_visual(f'Comunicação: "{comunicador.utilizar_imagem(im)}"'),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(img.caminho, size=44),
                            ft.Text(img.nome, size=15, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ft.Text(img.descricao, size=11, color=ft.Colors.GREY, text_align=ft.TextAlign.CENTER, max_lines=2),
                        ],
                    ),
                ),
            )
            grid_imagens.controls.append(card_img)
        page.update()

    aba_imagens = ft.Container(padding=16, content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
        ft.Text("Pictogramas Visuais (CAA)", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Toque em um cartão visual para comunicação rápida:", size=13, color=ft.Colors.GREY),
        ft.Divider(), grid_imagens
    ]))

    # =====================================================================
    # ABA 4: CRISE / SOS
    # =====================================================================
    coluna_crises = ft.Column(spacing=8)
    coluna_contatos = ft.Column(spacing=8)
    titulo_perfil_nome = ft.Text("", weight=ft.FontWeight.BOLD)
    subtitulo_perfil_email = ft.Text("")

    def carregar_dados_usuario():
        titulo_perfil_nome.value = f"Usuário: {usuario_atual.nome}"
        subtitulo_perfil_email.value = f"E-mail: {usuario_atual.email}"

        coluna_crises.controls.clear()
        for c in usuario_atual.listar_informacoes_crise():
            coluna_crises.controls.append(ft.Container(
                padding=12, bgcolor="#fff8e1",
                border_radius=8,
                content=ft.Column([
                    ft.Text(f"⚠️ Gatilho: {c.descricao}", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Sinais: {c.sinais}", size=13),
                    ft.Text(f"✅ Como agir: {c.orientacoes}", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN),
                ])
            ))

        coluna_contatos.controls.clear()
        for ct in usuario_atual.listar_contatos_emergencia():
            coluna_contatos.controls.append(ft.Card(content=ft.Container(padding=12, content=ft.Row([
                ft.Column([ft.Text(ct.nome, weight=ft.FontWeight.BOLD, size=16), ft.Text(f"{ct.descricao} • Tel: {ct.telefone}", size=13, color=ft.Colors.GREY)], expand=True),
                FilledButtonCls("🚨 Acionar", bgcolor=ft.Colors.RED, on_click=lambda e, contato=ct: emitir_comunicacao_visual(contato.acionar(), ft.Colors.RED)),
            ]))))
        page.update()

    aba_usuario_crise = ft.Container(padding=16, content=ft.Column(scroll=ft.ScrollMode.AUTO, controls=[
        ft.ListTile(leading=ft.CircleAvatar(content=ft.Icon(ft.Icons.PERSON)), title=titulo_perfil_nome, subtitle=subtitulo_perfil_email),
        ft.Divider(),
        ft.Text("🚨 Contatos de Emergência", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
        coluna_contatos,
        ft.Divider(),
        ft.Text("🛡️ Cartão de Informações de Crise (TEA)", size=18, weight=ft.FontWeight.BOLD),
        coluna_crises,
    ]))

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