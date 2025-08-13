import flet as ft
import sqlite3
from flet import Colors as colors
import os


def main(page: ft.Page):
    page.title = "Pontal - Indicadores"
    page.theme_mode = "dark"
    page.window_width = 400
    page.window_height = 700
    page.scroll = ft.ScrollMode.ALWAYS


    def menu_button_style(bg="#00ffcc", fg="black"):
        return ft.ButtonStyle(
            bgcolor=bg,
            color=fg,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.padding.symmetric(horizontal=10, vertical=15),
            alignment=ft.alignment.center,
            text_style=ft.TextStyle(size=15, weight="w500"),
        )

    def login_view():
        width = page.width * 0.85 if page.width < 600 else 400

        user_input = ft.TextField(label="Usuário", border_radius=12, bgcolor="#1a1a1a",
                                  border_color="#00ffcc", color="white")
        senha_input = ft.TextField(label="Senha", password=True, can_reveal_password=True,
                                   border_radius=12, bgcolor="#1a1a1a", border_color="#00ffcc", color="white")
        msg = ft.Text("", color="red", size=13)

        def login(e):
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (user_input.value, senha_input.value))
            usuario = cursor.fetchone()
            conn.close()
            if usuario:
                page.client_storage.set("user", usuario[2])
                page.client_storage.set("tipo", usuario[4])
                page.go("/menu")
            else:
                msg.value = "❌ Usuário ou senha inválidos"
                page.update()

        return ft.View("/", controls=[
            ft.Container(
                content=ft.Column([
                    ft.Text("🛍️ PONTAL", size=36, weight="bold", color="#00ffcc", text_align="center"),
                    ft.Text("Indicadores de Desempenho", size=20, italic=True, color="#cccccc", text_align="center"),
                    ft.Container(padding=10),
                    user_input,
                    senha_input,
                    ft.ElevatedButton("Entrar", on_click=login, style=ft.ButtonStyle(
                        bgcolor="#00ffcc", color="black", shape=ft.RoundedRectangleBorder(radius=10))),
                    msg
                ], width=width, alignment="center", horizontal_alignment="center", spacing=18),
                alignment=ft.alignment.center,
                padding=40,
                border_radius=20,
                gradient=ft.LinearGradient(colors=["#0f0f0f", "#1c1c1c", "#222222"]),
                shadow=ft.BoxShadow(blur_radius=30, color="#00ffcc")
            )
        ])

    def menu_view():
        user = page.client_storage.get("user") or "usuário"
        tipo = page.client_storage.get("tipo")

        botoes = [
            ft.ElevatedButton("📈 Vendas", on_click=lambda _: page.go("/vendas"),
                            style=menu_button_style(), width=300),
            ft.ElevatedButton("🚗 Fluxo de Veículos", on_click=lambda _: page.go("/veiculos"),
                            style=menu_button_style(), width=300),
            ft.ElevatedButton("💰 Receita Estacionamento", on_click=lambda _: page.go("/estacionamento"),
                            style=menu_button_style(), width=300),
            ft.ElevatedButton("👥 Fluxo de Pessoas", on_click=lambda _: page.go("/pessoas"),
                            style=menu_button_style(), width=300),
            ft.ElevatedButton("📊 NOI", on_click=lambda _: page.go("/noi"),
                            style=menu_button_style(), width=300),
        ]

        if tipo == "admin":
            botoes.append(
                ft.ElevatedButton("🛠 Administração", on_click=lambda _: page.go("/admin"),
                                style=menu_button_style(), width=300)
            )

        botoes.append(
            ft.ElevatedButton("🚪 Sair", on_click=lambda _: page.go("/"),
                            bgcolor=ft.Colors.RED_400, color=ft.Colors.WHITE, width=300)
        )

        return ft.View(
            "/menu",
            scroll=ft.ScrollMode.ALWAYS,
            appbar=ft.AppBar(
                title=ft.Text(f"🛍️ Menu - Olá, {user}", color=ft.Colors.CYAN_ACCENT),
                bgcolor=ft.Colors.BLACK
            ),
            controls=[
                ft.Container(
                    alignment=ft.alignment.top_center,
                    padding=30,
                    margin=20,
                    bgcolor=ft.Colors.BLACK,
                    border_radius=20,
                    shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.CYAN_ACCENT),
                    content=ft.Column(
                        spacing=25,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=botoes
                    )
                )
            ]
        )

    def vendas_view():
        try:
            # Conecta e busca os dados
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM indicadores WHERE tipo = 'Vendas' AND ano = 2025 ORDER BY mes"
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ft.View(
                    "/vendas",
                    controls=[
                        ft.AppBar(title=ft.Text("📊 Indicador: Vendas"), bgcolor="#1e1e1e"),
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Text(
                                "⚠️ Nenhum dado encontrado para 2025",
                                size=18,
                                color=ft.Colors.ORANGE,
                            ),
                        ),
                        ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu")),
                    ],
                )

            # Helpers
            meses_abrev = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            def nome_mes(m: int) -> str:
                return meses_abrev[m-1] if 1 <= m <= 12 else "Inválido"

            def format_real(v: float) -> str:
                return (
                    f"R$ {v:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

            def pct(a: float, b: float) -> ft.Text:
                try:
                    p = (a - b) / b * 100 if b else 0
                    color = ft.Colors.GREEN if p >= 0 else ft.Colors.RED
                    return ft.Text(f"{p:+.2f}%", color=color)
                except:
                    return ft.Text("0.00%", color=ft.Colors.GREY)

            # Totais gerais
            total_real     = sum(r[6] or 0 for r in rows)
            total_anterior = sum(r[7] or 0 for r in rows)
            total_meta     = sum(r[5] or 0 for r in rows)

            # Último mês
            ultimo         = rows[-1]
            mes_atual      = int(ultimo[3])
            realizado_mes  = ultimo[6] or 0
            anterior_mes   = ultimo[7] or 0
            meta_mes       = ultimo[5] or 0

            # Prepara dados do gráfico
            chart_data = [
                ft.LineChartDataPoint(
                    x=i+1,
                    y=float(r[6] or 0),
                    tooltip=format_real(float(r[6] or 0))
                )
                for i, r in enumerate(rows)
            ]
            max_y = max((p.y for p in chart_data), default=0) * 1.2 or 10

            # Estilo comum dos cards
            card_style = dict(
                bgcolor="#1f1f1f",
                border_radius=10,
                padding=15,
                width=400,
                height=300,
            )

            # Card Acumulado do Ano
            card_acum = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text("📅 Acumulado do Ano", size=20, weight="bold"),
                    ft.Text(f"Realizado: {format_real(total_real)}"),
                    ft.Text(f"Ano Anterior: {format_real(total_anterior)}", color=ft.Colors.GREY),
                    ft.Text(f"Meta: {format_real(total_meta)}", color=ft.Colors.BLUE_300),
                    ft.Row([ft.Text("Variação vs. Ano Ant.: "), pct(total_real, total_anterior)]),
                    ft.Row([ft.Text("Variação vs. Meta:       "), pct(total_real, total_meta)]),
                ], spacing=6)
            )

            # Card Mês Atual
            card_mes = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text("📆 Mês Atual", size=20, weight="bold"),
                    ft.Text(f"{nome_mes(mes_atual)}/2025"),
                    ft.Text(f"Realizado: {format_real(realizado_mes)}"),
                    ft.Text(f"Ano Anterior: {format_real(anterior_mes)}", color=ft.Colors.GREY),
                    ft.Text(f"Meta: {format_real(meta_mes)}", color=ft.Colors.BLUE_300),
                    ft.Row([ft.Text("Variação vs. Mês Ant.: "), pct(realizado_mes, anterior_mes)]),
                    ft.Row([ft.Text("Variação vs. Meta:       "), pct(realizado_mes, meta_mes)]),
                ], spacing=6)
            )

            # Monta linhas da tabela
            tabela_rows = []
            for r in rows:
                mm = int(r[3])
                real = r[6] or 0
                ant  = r[7] or 0
                met  = r[5] or 0
                tabela_rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(nome_mes(mm))),
                    ft.DataCell(ft.Text(format_real(real))),
                    ft.DataCell(ft.Text(format_real(ant))),
                    ft.DataCell(pct(real, ant)),
                    ft.DataCell(ft.Text(format_real(met))),
                    ft.DataCell(pct(real, met)),
                ]))
            # Linha Total
            tabela_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("Total", weight="bold")),
                ft.DataCell(ft.Text(format_real(total_real), weight="bold")),
                ft.DataCell(ft.Text(format_real(total_anterior), weight="bold")),
                ft.DataCell(pct(total_real, total_anterior)),
                ft.DataCell(ft.Text(format_real(total_meta), weight="bold")),
                ft.DataCell(pct(total_real, total_meta)),
            ], selected=True))

            # Monta a View completa
            return ft.View(
                "/vendas",
                controls=[
                    ft.AppBar(title=ft.Text("📊 Indicador: Vendas"), bgcolor="#1e1e1e"),
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            scroll="auto",
                            spacing=20,
                            controls=[
                                ft.Row([card_acum, card_mes], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("📈 Evolução Mensal", size=16, weight="bold"),

                                # Container do gráfico com margem horizontal e padding inferior
                                ft.Container(
                                    margin=ft.margin.symmetric(horizontal=80),  # margem nas laterais
                                    padding=ft.padding.only(bottom=30),         # espaço abaixo
                                    content=ft.Column([
                                        ft.LineChart(
                                            data_series=[
                                                ft.LineChartData(
                                                    data_points=chart_data,
                                                    curved=True,            # linha suavizada
                                                    stroke_width=3,         # espessura
                                                    color=ft.Colors.BLUE,   # cor
                                                )
                                            ],
                                            min_y=0,
                                            max_y=max_y,
                                            tooltip_bgcolor=ft.Colors.BLUE_800,
                                            expand=True,
                                            height=250,
                                        ),
                                        ft.Row(
                                            [ft.Text(nome_mes(int(r[3])), size=12) for r in rows],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                    ])
                                ),

                                ft.Divider(),
                                ft.Text("Detalhamento por Mês", size=16, weight="bold"),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Mês")),
                                        ft.DataColumn(ft.Text("Realizado")),
                                        ft.DataColumn(ft.Text("Ano Anterior")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Meta")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                    ],
                                    rows=tabela_rows,
                                ),
                                ft.Divider(),
                                ft.ElevatedButton(
                                    text="🔗 Ver Relatório Power BI",
                                    icon=ft.Icons.INSIGHTS,
                                    style=ft.ButtonStyle(bgcolor="#2563eb", color="white"),
                                    on_click=lambda _: page.launch_url("https://app.powerbi.com/view?r=eyJrIjoiYmVjMWY0YTctYjNhOC00ZGZlLTk2YzUtNGZkMjNjYWEzMWNmIiwidCI6IjYwNjY0ZmMwLWNiMGMtNGUyOS04MWRhLWNjMDlhYTExOTZhMCJ9"),
                                ),

                                # Botão de voltar ao menu
                                ft.ElevatedButton(
                                    text="↩️ Voltar",
                                    on_click=lambda _: page.go("/menu"),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                                ),
                            ],
                        ),
                    ),
                ],
            )

        except Exception as e:
            return ft.View(
                "/vendas",
                controls=[
                    ft.AppBar(title=ft.Text("Erro ao carregar", color=ft.Colors.RED)),
                    ft.Text(str(e), color=ft.Colors.RED_400),
                ],
            )
        
    def fluxo_view():
        try:
            # 1) Busca dados no banco
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mes, mes_nome, ano, realizado, meta, ano_anterior "
                "FROM indicadores "
                "WHERE tipo = 'Fluxo de Veículos' AND ano = 2025 "
                "ORDER BY mes"
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ft.View(
                    "/veiculos",
                    controls=[
                        ft.AppBar(title=ft.Text("🚗 Indicador: Fluxo de Veículos"), bgcolor="#1e1e1e"),
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Text(
                                "⚠️ Nenhum dado encontrado para 2025",
                                size=18,
                                color=ft.Colors.ORANGE
                            )
                        ),
                        ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu"))
                    ]
                )

            # 2) Helpers
            def format_num(v: float) -> str:
                return f"{v:,.0f}".replace(",", ".")
            def pct(a: float, b: float) -> ft.Text:
                p = (a - b) / b * 100 if b else 0
                c = ft.Colors.GREEN if p >= 0 else ft.Colors.RED
                return ft.Text(f"{p:+.2f}%", color=c)

            # 3) Totais e mês atual
            total_real      = sum(r[3] or 0 for r in rows)
            total_meta      = sum(r[4] or 0 for r in rows if r[4] is not None)
            total_anterior  = sum(r[5] or 0 for r in rows if r[5] is not None)
            ultimo          = rows[-1]
            mes_atual_nome  = ultimo[1]
            real_mes        = ultimo[3] or 0
            meta_mes        = ultimo[4] or 0
            ant_mes         = ultimo[5] or 0

            # 4) Dados do gráfico
            chart_data = [
                ft.LineChartDataPoint(x=i+1, y=float(r[3]), tooltip=format_num(r[3]))
                for i, r in enumerate(rows)
            ]
            max_y = max(p.y for p in chart_data) * 1.2

            # 5) Cards
            card_style = dict(bgcolor="#1f1f1f", border_radius=10, padding=15, width=360, height=220)

            card_acum = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text("📊 Acumulado", size=18, weight="bold"),
                    ft.Text(f"Realizado: {format_num(total_real)}"),
                    ft.Text(f"Meta:       {format_num(total_meta)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   {format_num(total_anterior)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(total_real, total_meta)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(total_real, total_anterior)]),
                ], spacing=4)
            )

            card_mes = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text(f"📆 Mês Atual: {mes_atual_nome}/2025", size=18, weight="bold"),
                    ft.Text(f"Realizado: {format_num(real_mes)}"),
                    ft.Text(f"Meta:       {format_num(meta_mes)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   {format_num(ant_mes)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(real_mes, meta_mes)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(real_mes, ant_mes)]),
                ], spacing=4)
            )

            # 6) Tabela comparativa
            tabela_rows = []
            for r in rows:
                tabela_rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[1])),              # mes_nome
                    ft.DataCell(ft.Text(format_num(r[3]))),  # realizado
                    ft.DataCell(ft.Text(format_num(r[5]))),  # ano_anterior
                    ft.DataCell(pct(r[3], r[5])),            # var vs ant
                    ft.DataCell(ft.Text(format_num(r[4]))),  # meta
                    ft.DataCell(pct(r[3], r[4])),            # var vs meta
                ]))
            # Total
            tabela_rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("Total", weight="bold")),
                ft.DataCell(ft.Text(format_num(total_real), weight="bold")),
                ft.DataCell(ft.Text(format_num(total_anterior), weight="bold")),
                ft.DataCell(pct(total_real, total_anterior)),
                ft.DataCell(ft.Text(format_num(total_meta), weight="bold")),
                ft.DataCell(pct(total_real, total_meta)),
            ], selected=True))

            # 7) Monta a View
            return ft.View(
                "/veiculos",
                controls=[
                    ft.AppBar(title=ft.Text("🚗 Indicador: Fluxo de Veículos"), bgcolor="#1e1e1e"),
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            scroll="auto",
                            spacing=20,
                            controls=[
                                ft.Row([card_acum, card_mes], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("📈 Evolução Mensal", size=16, weight="bold"),
                                ft.Container(
                                    margin=ft.margin.symmetric(horizontal=60),
                                    padding=ft.padding.only(bottom=20),
                                    content=ft.Column([
                                        ft.LineChart(
                                            data_series=[ft.LineChartData(data_points=chart_data, curved=True, stroke_width=3)],
                                            min_y=0, max_y=max_y,
                                            tooltip_bgcolor=ft.Colors.BLUE_800,
                                            expand=True, height=200
                                        ),
                                        ft.Row(
                                            [ft.Text(r[1], size=12) for r in rows],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ])
                                ),
                                ft.Divider(),
                                ft.Text("Detalhamento por Mês", size=16, weight="bold"),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Mês")),
                                        ft.DataColumn(ft.Text("Realizado")),
                                        ft.DataColumn(ft.Text("Ano Ant.")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Meta")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                    ],
                                    rows=tabela_rows,
                                ),
                                ft.Divider(),
                                ft.ElevatedButton(
                                    text="🔗 Ver Relatório Power BI",
                                    icon=ft.Icons.INSIGHTS,
                                    style=ft.ButtonStyle(bgcolor="#2563eb", color="white"),
                                    on_click=lambda _: page.launch_url(
                                        "https://app.powerbi.com/view?r=eyJrIjoiMzI0NDZiNDUtNGQwOS00NDdlLTk1YzItMzk5ZGRiN2YwYTI3IiwidCI6IjYwNjY0ZmMwLWNiMGMtNGUyOS04MWRhLWNjMDlhYTExOTZhMCJ9"
                                    )
                                ),
                                ft.ElevatedButton(
                                    text="↩️ Voltar",
                                    on_click=lambda _: page.go("/menu"),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                                ),
                            ]
                        )
                    )
                ]
            )

        except Exception as e:
            return ft.View(
                "/veiculos",
                controls=[
                    ft.AppBar(title=ft.Text("Erro Fluxo", color=ft.Colors.RED)),
                    ft.Text(str(e), color=ft.Colors.RED_400)
                ]
            )

    def estacionamento_view():
        try:
            # busca
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mes, mes_nome, ano, realizado, meta, ano_anterior "
                "FROM indicadores "
                "WHERE tipo = 'Receita de Estacionamento' AND ano = 2025 "
                "ORDER BY mes"
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ft.View(
                    "/estacionamento",
                    controls=[
                        ft.AppBar(title=ft.Text("💰 Receita de Estacionamento"), bgcolor="#1e1e1e"),
                        ft.Container(expand=True, padding=20,
                            content=ft.Text("⚠️ Nenhum dado encontrado para 2025",
                                            size=18, color=ft.Colors.ORANGE)
                        ),
                        ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu"))
                    ]
                )

            # helpers
            def fmt(v): return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            def pct(a,b):
                p = (a-b)/b*100 if b else 0
                c = ft.Colors.GREEN if p>=0 else ft.Colors.RED
                return ft.Text(f"{p:+.2f}%", color=c)

            # totais / atual
            total_real     = sum(r[3] or 0 for r in rows)
            total_meta     = sum(r[4] or 0 for r in rows if r[4] is not None)
            total_anterior = sum(r[5] or 0 for r in rows if r[5] is not None)
            ultimo         = rows[-1]
            mes_atual      = ultimo[1]
            real_mes       = ultimo[3] or 0
            meta_mes       = ultimo[4] or 0
            ant_mes        = ultimo[5] or 0

            # gráfico
            chart_data = [
                ft.LineChartDataPoint(x=i+1, y=float(r[3]), tooltip=fmt(r[3]))
                for i,r in enumerate(rows)
            ]
            max_y = max(p.y for p in chart_data)*1.2

            # cards
            cs = dict(bgcolor="#1f1f1f", border_radius=10, padding=15, width=360, height=220)
            card_acum = ft.Container(
                **cs,
                content=ft.Column([
                    ft.Text("📊 Acumulado", size=18, weight="bold"),
                    ft.Text(f"Realizado: R$ {fmt(total_real)}"),
                    ft.Text(f"Meta:       R$ {fmt(total_meta)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   R$ {fmt(total_anterior)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(total_real, total_meta)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(total_real, total_anterior)]),
                ], spacing=4)
            )
            card_mes = ft.Container(
                **cs,
                content=ft.Column([
                    ft.Text(f"📆 Mês Atual: {mes_atual}/2025", size=18, weight="bold"),
                    ft.Text(f"Realizado: R$ {fmt(real_mes)}"),
                    ft.Text(f"Meta:       R$ {fmt(meta_mes)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   R$ {fmt(ant_mes)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(real_mes, meta_mes)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(real_mes, ant_mes)]),
                ], spacing=4)
            )

            # tabela comparativa
            tabela = []
            for r in rows:
                tabela.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(f"R$ {fmt(r[3])}")),
                    ft.DataCell(ft.Text(f"R$ {fmt(r[5])}")),
                    ft.DataCell(pct(r[3], r[5])),
                    ft.DataCell(ft.Text(f"R$ {fmt(r[4])}")),
                    ft.DataCell(pct(r[3], r[4])),
                ]))
            # total
            tabela.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("Total", weight="bold")),
                ft.DataCell(ft.Text(f"R$ {fmt(total_real)}", weight="bold")),
                ft.DataCell(ft.Text(f"R$ {fmt(total_anterior)}", weight="bold")),
                ft.DataCell(pct(total_real, total_anterior)),
                ft.DataCell(ft.Text(f"R$ {fmt(total_meta)}", weight="bold")),
                ft.DataCell(pct(total_real, total_meta)),
            ], selected=True))

            # monta view
            return ft.View(
                "/estacionamento",
                controls=[
                    ft.AppBar(title=ft.Text("💰 Receita de Estacionamento"), bgcolor="#1e1e1e"),
                    ft.Container(
                        expand=True, padding=20,
                        content=ft.Column(
                            scroll="auto", spacing=20,
                            controls=[
                                ft.Row([card_acum, card_mes], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("📈 Evolução Mensal", size=16, weight="bold"),
                                ft.Container(
                                    margin=ft.margin.symmetric(horizontal=60),
                                    padding=ft.padding.only(bottom=20),
                                    content=ft.Column([
                                        ft.LineChart(
                                            data_series=[ft.LineChartData(data_points=chart_data, curved=True, stroke_width=3)],
                                            min_y=0, max_y=max_y,
                                            tooltip_bgcolor=ft.Colors.BLUE_800,
                                            expand=True, height=200
                                        ),
                                        ft.Row(
                                            [ft.Text(r[1], size=12) for r in rows],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ])
                                ),
                                ft.Divider(),
                                ft.Text("Detalhamento por Mês", size=16, weight="bold"),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Mês")),
                                        ft.DataColumn(ft.Text("Realizado")),
                                        ft.DataColumn(ft.Text("Ano Ant.")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Meta")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                    ],
                                    rows=tabela
                                ),
                                ft.Divider(),
                                ft.ElevatedButton(
                                    text="🔗 Ver Relatório Power BI",
                                    icon=ft.Icons.INSIGHTS,
                                    style=ft.ButtonStyle(bgcolor="#2563eb", color="white"),
                                    on_click=lambda _: page.launch_url("https://app.powerbi.com/view?r=eyJrIjoiNjVlMDRkMjQtNzg2ZC00OTVhLWFhMDMtNDg3NDFjMjgzOTE0IiwidCI6IjYwNjY0ZmMwLWNiMGMtNGUyOS04MWRhLWNjMDlhYTExOTZhMCJ9")
                                ),
                                ft.ElevatedButton(
                                    text="↩️ Voltar",
                                    on_click=lambda _: page.go("/menu"),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                                ),
                            ]
                        )
                    )
                ]
            )

        except Exception as e:
            return ft.View(
                "/estacionamento",
                controls=[
                    ft.AppBar(title=ft.Text("Erro Estacionamento", color=ft.Colors.RED)),
                    ft.Text(str(e), color=ft.Colors.RED_400),
                ]
            )

    def pessoas_view():
        try:
            # 1) busca
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT mes, mes_nome, ano, realizado, meta, ano_anterior "
                "FROM indicadores "
                "WHERE tipo = 'Fluxo de Pessoas' AND ano = 2025 "
                "ORDER BY mes"
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ft.View(
                    "/pessoas",
                    controls=[
                        ft.AppBar(title=ft.Text("👥 Fluxo de Pessoas"), bgcolor="#1e1e1e"),
                        ft.Container(expand=True, padding=20,
                            content=ft.Text("⚠️ Nenhum dado encontrado para 2025",
                                            size=18, color=ft.Colors.ORANGE)
                        ),
                        ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu"))
                    ]
                )

            # 2) formatadores
            def fmt(v): return f"{v:,.0f}".replace(",", ".")
            def pct(a,b):
                p = (a-b)/b*100 if b else 0
                c = ft.Colors.GREEN if p>=0 else ft.Colors.RED
                return ft.Text(f"{p:+.2f}%", color=c)

            # 3) totais e mês atual
            total_real     = sum(r[3] or 0 for r in rows)
            total_meta     = sum(r[4] or 0 for r in rows if r[4] is not None)
            total_ant      = sum(r[5] or 0 for r in rows if r[5] is not None)
            ultimo         = rows[-1]
            mes_atual      = ultimo[1]
            real_mes       = ultimo[3] or 0
            meta_mes       = ultimo[4] or 0
            ant_mes        = ultimo[5] or 0

            # 4) gráfico
            chart_data = [
                ft.LineChartDataPoint(x=i+1, y=float(r[3]), tooltip=fmt(r[3]))
                for i,r in enumerate(rows)
            ]
            max_y = max(p.y for p in chart_data) * 1.2

            # 5) cards
            cs = dict(bgcolor="#1f1f1f", border_radius=10, padding=15, width=360, height=220)
            card_acum = ft.Container(
                **cs,
                content=ft.Column([
                    ft.Text("📊 Acumulado", size=18, weight="bold"),
                    ft.Text(f"Realizado: {fmt(total_real)}"),
                    ft.Text(f"Meta:       {fmt(total_meta)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   {fmt(total_ant)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(total_real, total_meta)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(total_real, total_ant)]),
                ], spacing=4)
            )
            card_mes = ft.Container(
                **cs,
                content=ft.Column([
                    ft.Text(f"📆 Mês Atual: {mes_atual}/2025", size=18, weight="bold"),
                    ft.Text(f"Realizado: {fmt(real_mes)}"),
                    ft.Text(f"Meta:       {fmt(meta_mes)}", color=ft.Colors.BLUE_300),
                    ft.Text(f"Ano Ant.:   {fmt(ant_mes)}", color=ft.Colors.GREY),
                    ft.Row([ft.Text("Vs. Meta:"), pct(real_mes, meta_mes)]),
                    ft.Row([ft.Text("Vs. Ano Ant.:"), pct(real_mes, ant_mes)]),
                ], spacing=4)
            )

            # 6) tabela
            tabela = []
            for r in rows:
                tabela.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(r[1])),
                    ft.DataCell(ft.Text(fmt(r[3]))),
                    ft.DataCell(pct(r[3], r[5])),
                    ft.DataCell(ft.Text(fmt(r[5]))),
                    ft.DataCell(pct(r[3], r[4])),
                    ft.DataCell(ft.Text(fmt(r[4]))),
                ]))
            tabela.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text("Total", weight="bold")),
                ft.DataCell(ft.Text(fmt(total_real), weight="bold")),
                ft.DataCell(pct(total_real, total_ant)),
                ft.DataCell(ft.Text(fmt(total_ant), weight="bold")),
                ft.DataCell(pct(total_real, total_meta)),
                ft.DataCell(ft.Text(fmt(total_meta), weight="bold")),
            ], selected=True))

            # 7) monta view
            return ft.View(
                "/pessoas",
                controls=[
                    ft.AppBar(title=ft.Text("👥 Fluxo de Pessoas"), bgcolor="#1e1e1e"),
                    ft.Container(
                        expand=True, padding=20,
                        content=ft.Column(
                            scroll="auto", spacing=20,
                            controls=[
                                ft.Row([card_acum, card_mes], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("📈 Evolução Mensal", size=16, weight="bold"),
                                ft.Container(
                                    margin=ft.margin.symmetric(horizontal=60),
                                    padding=ft.padding.only(bottom=20),
                                    content=ft.Column([
                                        ft.LineChart(
                                            data_series=[ft.LineChartData(data_points=chart_data, curved=True, stroke_width=3)],
                                            min_y=0, max_y=max_y,
                                            tooltip_bgcolor=ft.Colors.BLUE_800,
                                            expand=True, height=200
                                        ),
                                        ft.Row(
                                            [ft.Text(r[1], size=12) for r in rows],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                        )
                                    ])
                                ),
                                ft.Divider(),
                                ft.Text("Detalhamento por Mês", size=16, weight="bold"),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Mês")),
                                        ft.DataColumn(ft.Text("Realizado")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Ano Ant.")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Meta")),
                                    ],
                                    rows=tabela
                                ),
                                ft.Divider(),
                                ft.ElevatedButton(
                                    text="🔗 Ver Relatório Power BI",
                                    icon=ft.Icons.INSIGHTS,
                                    style=ft.ButtonStyle(bgcolor="#2563eb", color="white"),
                                    on_click=lambda _: page.launch_url("https://app.powerbi.com/view?r=eyJrIjoiYWE5NDhhMWItMGZjNi00Yzk3LTgzNjUtMWQyNTk2YmYzNDA2IiwidCI6IjYwNjY0ZmMwLWNiMGMtNGUyOS04MWRhLWNjMDlhYTExOTZhMCJ9")
                                ),
                                ft.ElevatedButton(
                                    text="↩️ Voltar",
                                    on_click=lambda _: page.go("/menu"),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                                ),
                            ]
                        )
                    )
                ]
            )

        except Exception as e:
            return ft.View(
                "/pessoas",
                controls=[
                    ft.AppBar(title=ft.Text("Erro Pessoas", color=ft.Colors.RED)),
                    ft.Text(str(e), color=ft.Colors.RED_400)
                ]
            )
        
    def noi_view(page: ft.Page):
        try:
            conn = sqlite3.connect("indicadores.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM indicadores WHERE tipo = 'NOI' AND ano = 2025 ORDER BY mes"
            )
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return ft.View(
                    "/noi",
                    controls=[
                        ft.AppBar(title=ft.Text("📊 Indicador: NOI"), bgcolor="#1e1e1e"),
                        ft.Container(
                            expand=True,
                            padding=20,
                            content=ft.Text(
                                "⚠️ Nenhum dado encontrado para 2025",
                                size=18,
                                color=ft.Colors.ORANGE,
                            ),
                        ),
                        ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu")),
                    ],
                )

            # — Helpers de formatação —
            meses_abrev = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
            def nome_mes(m: int) -> str:
                return meses_abrev[m-1] if 1 <= m <= 12 else "Inválido"

            def format_real(v: float) -> str:
                return (
                    f"R$ {v:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

            def pct(a: float, b: float) -> ft.Text:
                try:
                    p = (a - b) / abs(b) * 100 if b else 0
                    color = ft.Colors.GREEN if p >= 0 else ft.Colors.RED
                    return ft.Text(f"{p:+.2f}%", color=color)
                except:
                    return ft.Text("0.00%", color=ft.Colors.GREY)

            # — Totais gerais e mês atual —
            total_real     = sum(r[6] or 0 for r in rows)
            total_anterior = sum(r[7] or 0 for r in rows)
            total_meta     = sum(r[5] or 0 for r in rows)

            ultimo         = rows[-1]
            mes_atual      = int(ultimo[3])
            realizado_mes  = ultimo[6] or 0
            anterior_mes   = ultimo[7] or 0
            meta_mes       = ultimo[5] or 0

            # — Prepara dados do gráfico —
            chart_data = [
                ft.LineChartDataPoint(
                    x=i+1,
                    y=float(r[6] or 0),
                    tooltip=format_real(float(r[6] or 0))
                )
                for i, r in enumerate(rows)
            ]
            ys = [p.y for p in chart_data]
            min_y = min(ys) * 1.2
            max_y = max(ys) * 1.2

            # — Estilo comum dos cards —
            card_style = dict(
                bgcolor="#1f1f1f",
                border_radius=10,
                padding=15,
                width=400,
                height=300,
            )

            # Card Acumulado do Ano
            card_acum = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text("📅 Acumulado do Ano", size=20, weight="bold"),
                    ft.Text(f"Realizado: {format_real(total_real)}"),
                    ft.Text(f"Ano Anterior: {format_real(total_anterior)}", color=ft.Colors.GREY),
                    ft.Text(f"Meta: {format_real(total_meta)}", color=ft.Colors.BLUE_300),
                    ft.Row([ft.Text("Variação vs. Ano Ant.: "), pct(total_real, total_anterior)]),
                    ft.Row([ft.Text("Variação vs. Meta:       "), pct(total_real, total_meta)]),
                ], spacing=6)
            )

            # Card Mês Atual
            card_mes = ft.Container(
                **card_style,
                content=ft.Column([
                    ft.Text("📆 Mês Atual", size=20, weight="bold"),
                    ft.Text(f"{nome_mes(mes_atual)}/2025"),
                    ft.Text(f"Realizado: {format_real(realizado_mes)}"),
                    ft.Text(f"Ano Anterior: {format_real(anterior_mes)}", color=ft.Colors.GREY),
                    ft.Text(f"Meta: {format_real(meta_mes)}", color=ft.Colors.BLUE_300),
                    ft.Row([ft.Text("Variação vs. Mês Ant.: "), pct(realizado_mes, anterior_mes)]),
                    ft.Row([ft.Text("Variação vs. Meta:       "), pct(realizado_mes, meta_mes)]),
                ], spacing=6)
            )

            # — Monta linhas da tabela comparativa —
            tabela_rows = []
            for r in rows:
                mm   = int(r[3])
                real = r[6] or 0
                ant  = r[7] or 0
                met  = r[5] or 0
                tabela_rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(nome_mes(mm))),
                        ft.DataCell(ft.Text(format_real(real))),
                        ft.DataCell(ft.Text(format_real(ant))),
                        ft.DataCell(pct(real, ant)),
                        ft.DataCell(ft.Text(format_real(met))),
                        ft.DataCell(pct(real, met)),
                    ])
                )
            # Linha Total
            tabela_rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Total", weight="bold")),
                    ft.DataCell(ft.Text(format_real(total_real),     weight="bold")),
                    ft.DataCell(ft.Text(format_real(total_anterior), weight="bold")),
                    ft.DataCell(pct(total_real, total_anterior)),
                    ft.DataCell(ft.Text(format_real(total_meta),     weight="bold")),
                    ft.DataCell(pct(total_real, total_meta)),
                ], selected=True)
            )

            # — Monta e retorna a View completa —
            return ft.View(
                "/noi",
                controls=[
                    ft.AppBar(title=ft.Text("📊 Indicador: NOI"), bgcolor="#1e1e1e"),
                    ft.Container(
                        expand=True,
                        padding=20,
                        content=ft.Column(
                            scroll="auto",
                            spacing=20,
                            controls=[
                                ft.Row([card_acum, card_mes], spacing=20, wrap=True),
                                ft.Divider(),
                                ft.Text("📈 Evolução Mensal", size=16, weight="bold"),

                                # gráfico suavizado com margem extra
                                ft.Container(
                                    margin=ft.margin.symmetric(horizontal=80),
                                    padding=ft.padding.only(bottom=30),
                                    content=ft.Column([
                                        ft.LineChart(
                                            data_series=[
                                                ft.LineChartData(
                                                    data_points=chart_data,
                                                    curved=True,
                                                    stroke_width=3,
                                                    color=ft.Colors.BLUE,
                                                )
                                            ],
                                            min_y=min_y,
                                            max_y=max_y,
                                            tooltip_bgcolor=ft.Colors.BLUE_800,
                                            expand=True,
                                            height=250,
                                        ),
                                        ft.Row(
                                            [ft.Text(nome_mes(int(r[3])), size=12) for r in rows],
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        ),
                                    ])
                                ),

                                ft.Divider(),
                                ft.Text("Detalhamento por Mês", size=16, weight="bold"),
                                ft.DataTable(
                                    columns=[
                                        ft.DataColumn(ft.Text("Mês")),
                                        ft.DataColumn(ft.Text("Realizado")),
                                        ft.DataColumn(ft.Text("Ano Anterior")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                        ft.DataColumn(ft.Text("Meta")),
                                        ft.DataColumn(ft.Text("Var. (%)")),
                                    ],
                                    rows=tabela_rows,
                                ),

                                ft.Divider(),
                                ft.ElevatedButton(
                                    text="🔗 Ver Relatório Power BI",
                                    icon=ft.Icons.INSIGHTS,
                                    style=ft.ButtonStyle(bgcolor="#2563eb", color="white"),
                                    on_click=lambda _: page.launch_url("https://app.powerbi.com/view?r=eyJrIjoiZmQ0Mzk1MTktMWFmNC00NTk3LWIwMTctYzllNjg1OTk3MGQ5IiwidCI6IjYwNjY0ZmMwLWNiMGMtNGUyOS04MWRhLWNjMDlhYTExOTZhMCJ9"),
                                ),

                                ft.ElevatedButton(
                                    text="↩️ Voltar",
                                    on_click=lambda _: page.go("/menu"),
                                    style=ft.ButtonStyle(bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE),
                                ),
                            ],
                        ),
                    ),
                ],
            )

        except Exception as e:
            return ft.View(
                "/noi",
                controls=[
                    ft.AppBar(title=ft.Text("Erro ao carregar", color=ft.Colors.RED)),
                    ft.Text(str(e), color=ft.Colors.RED_400),
                    ft.ElevatedButton("↩️ Voltar", on_click=lambda _: page.go("/menu")),
                ],
            )

        
    def admin_view(page: ft.Page):
        tipo = page.client_storage.get("tipo")
        if tipo != "admin":
            return ft.View("/admin", controls=[ft.Text("🚫 Acesso Negado", size=20)])

        # --- Helpers de formatação ---
        meses_abrev = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
        TIPOS = ["Vendas", "Fluxo de Veículos", "Receita de Estacionamento", "Fluxo de Pessoas", "NOI"]

        def nome_mes(m: int) -> str:
            return meses_abrev[m-1] if 1 <= m <= 12 else "Inválido"

        def format_num(v: float) -> str:
            return f"{v:,.0f}".replace(",", ".")

        # --- Estado de edição ---
        id_usuario_edicao = None
        id_indicador_edicao = None

        # --- Campos Usuário ---
        nome = ft.TextField(label="Nome")
        usuario = ft.TextField(label="Usuário")
        email = ft.TextField(label="E-mail")
        senha = ft.TextField(label="Senha", password=True)
        tipo_usuario = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option("admin"), ft.dropdown.Option("user")])
        msg_user = ft.Text()
        lista_usuarios = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in ("Nome","Usuário","Email","Tipo","Ações")],
            rows=[]
        )

        def carregar_usuarios():
            lista_usuarios.rows.clear()
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            c.execute("SELECT id, nome, usuario, email, tipo FROM usuarios")
            for uid, n, u, e_, t in c.fetchall():
                lista_usuarios.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(n)),
                    ft.DataCell(ft.Text(u)),
                    ft.DataCell(ft.Text(e_)),
                    ft.DataCell(ft.Text(t)),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT, tooltip="Editar", on_click=lambda e, i=uid: editar_usuario(i)),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color="red", tooltip="Excluir", on_click=lambda e, i=uid: excluir_usuario(i)),
                    ]))
                ]))
            conn.close()

        def limpar_usuario():
            nonlocal id_usuario_edicao
            nome.value = usuario.value = email.value = senha.value = ""
            tipo_usuario.value = None
            id_usuario_edicao = None
            msg_user.value = ""
            page.update()

        def editar_usuario(uid):
            nonlocal id_usuario_edicao
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            c.execute("SELECT nome, usuario, email, senha, tipo FROM usuarios WHERE id = ?", (uid,))
            row = c.fetchone(); conn.close()
            if row:
                nome.value, usuario.value, email.value, senha.value, tipo_usuario.value = row
                id_usuario_edicao = uid
                msg_user.value = f"✏️ Editando usuário ID {uid}"
                page.update()

        def salvar_usuario(e):
            nonlocal id_usuario_edicao
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            try:
                if id_usuario_edicao:
                    c.execute("UPDATE usuarios SET nome=?, usuario=?, email=?, senha=?, tipo=? WHERE id=?",
                            (nome.value, usuario.value, email.value, senha.value, tipo_usuario.value, id_usuario_edicao))
                    msg_user.value = "✅ Usuário atualizado!"
                else:
                    c.execute("INSERT INTO usuarios (nome, usuario, email, senha, tipo) VALUES (?,?,?,?,?)",
                            (nome.value, usuario.value, email.value, senha.value, tipo_usuario.value))
                    msg_user.value = "✅ Usuário cadastrado!"
                conn.commit()
                limpar_usuario()
                carregar_usuarios()
            except sqlite3.IntegrityError:
                msg_user.value = "❌ Usuário já existe!"
            conn.close()
            page.update()

        def excluir_usuario(uid):
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            c.execute("DELETE FROM usuarios WHERE id = ?", (uid,)); conn.commit(); conn.close()
            msg_user.value = "🗑️ Usuário removido!"
            carregar_usuarios()
            page.update()

        carregar_usuarios()

        # --- Campos Indicador ---
        tipo_ind = ft.Dropdown(label="Tipo", options=[ft.dropdown.Option(o) for o in TIPOS])
        ano = ft.TextField(label="Ano", value="2025")
        mes = ft.TextField(label="Mês (1-12)", value="1")
        data_ref = ft.TextField(label="Data referência (YYYY-MM-DD)")
        meta = ft.TextField(label="Meta")
        realizado = ft.TextField(label="Realizado")
        anterior = ft.TextField(label="Ano Anterior")
        msg_ind = ft.Text()

        lista_indicadores = ft.DataTable(
            columns=[ft.DataColumn(ft.Text(c)) for c in ("Tipo","Ano","Mês","Meta","Realizado","Ano Anterior","Ações")],
            rows=[]
        )

        # --- Filtros ---
        filtro_tipo = ft.Dropdown(label="Filtrar por Tipo", options=[ft.dropdown.Option(o) for o in TIPOS])
        filtro_ano  = ft.TextField(label="Filtrar por Ano", value="")
        def filtrar(_):
            carregar_indicadores()
            page.update()
        btn_filtrar = ft.ElevatedButton("🔍 Filtrar", on_click=filtrar)
        def limpar_filtro(_):
            filtro_tipo.value = None
            filtro_ano.value = ""
            carregar_indicadores()
            page.update()
        btn_limpar = ft.ElevatedButton("❌ Limpar", on_click=limpar_filtro)

        def limpar_indicador():
            nonlocal id_indicador_edicao
            tipo_ind.value = None; ano.value = "2025"; mes.value = "1"
            data_ref.value = meta.value = realizado.value = anterior.value = ""
            id_indicador_edicao = None; msg_ind.value = ""
            page.update()

        def editar_indicador(iid):
            nonlocal id_indicador_edicao
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            c.execute("SELECT tipo, ano, mes, data_referencia, meta, realizado, ano_anterior FROM indicadores WHERE id = ?", (iid,))
            row = c.fetchone(); conn.close()
            if row:
                tipo_ind.value, ano.value, mes.value, data_ref.value, meta.value, realizado.value, anterior.value = (
                    row[0], str(row[1]), str(row[2]), row[3] or "",
                    str(row[4] or ""), str(row[5] or ""), str(row[6] or "")
                )
                id_indicador_edicao = iid
                msg_ind.value = f"✏️ Editando indicador ID {iid}"
                page.update()

        def salvar_indicador(e):
            nonlocal id_indicador_edicao
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            try:
                if id_indicador_edicao:
                    c.execute("""
                        UPDATE indicadores SET tipo=?, ano=?, mes=?, data_referencia=?, meta=?, realizado=?, ano_anterior=? WHERE id=?
                    """, (
                        tipo_ind.value, int(ano.value), int(mes.value),
                        data_ref.value,
                        float(meta.value)     if meta.value     else None,
                        float(realizado.value) if realizado.value else None,
                        float(anterior.value)  if anterior.value  else None,
                        id_indicador_edicao
                    ))
                    msg_ind.value = "✅ Indicador atualizado!"
                else:
                    c.execute("""
                        INSERT INTO indicadores
                        (tipo, ano, mes, data_referencia, meta, realizado, ano_anterior)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tipo_ind.value, int(ano.value), int(mes.value),
                        data_ref.value,
                        float(meta.value)     if meta.value     else None,
                        float(realizado.value) if realizado.value else None,
                        float(anterior.value)  if anterior.value  else None,
                    ))
                    msg_ind.value = "✅ Indicador cadastrado!"
                conn.commit()
                limpar_indicador()
                carregar_indicadores()
            except Exception as ex:
                msg_ind.value = f"❌ Erro: {ex}"
            conn.close()
            page.update()

        def excluir_indicador(iid):
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            c.execute("DELETE FROM indicadores WHERE id = ?", (iid,)); conn.commit(); conn.close()
            msg_ind.value = "🗑️ Indicador removido!"
            carregar_indicadores()
            page.update()

        def carregar_indicadores():
            lista_indicadores.rows.clear()
            conn = sqlite3.connect("indicadores.db"); c = conn.cursor()
            filtros = []
            params  = []
            if filtro_tipo.value:
                filtros.append("tipo = ?");    params.append(filtro_tipo.value)
            if filtro_ano.value.isdigit():
                filtros.append("ano = ?");     params.append(int(filtro_ano.value))
            where = ("WHERE " + " AND ".join(filtros)) if filtros else ""
            c.execute(f"SELECT id, tipo, ano, mes, meta, realizado, ano_anterior FROM indicadores {where} ORDER BY ano, mes", params)
            for iid, t, a, m, me, re_, an in c.fetchall():
                lista_indicadores.rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(t)),
                    ft.DataCell(ft.Text(str(a))),
                    ft.DataCell(ft.Text(nome_mes(m))),
                    ft.DataCell(ft.Text(format_num(me)))  if me is not None else ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text(format_num(re_))),
                    ft.DataCell(ft.Text(format_num(an)))  if an is not None else ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Row([
                        ft.IconButton(icon=ft.Icons.EDIT,    on_click=lambda e, i=iid: editar_indicador(i)),
                        ft.IconButton(icon=ft.Icons.DELETE,  icon_color="red", on_click=lambda e, i=iid: excluir_indicador(i)),
                    ]))
                ]))
            conn.close()

        # Carrega inicialmente
        carregar_indicadores()

        # --- Montagem da View ---
        return ft.View(
            "/admin",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.AppBar(title=ft.Text("⚙️ Painel Administrativo"), bgcolor="#1e1e1e"),
                ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    expand=True,
                    tabs=[
                        ft.Tab(
                            text="👤 Usuários",
                            content=ft.Column([
                                ft.Text("Cadastro de Usuários", size=20, weight="bold"),
                                nome, usuario, email, senha, tipo_usuario,
                                ft.Row([ft.ElevatedButton("💾 Salvar", on_click=salvar_usuario),
                                        ft.ElevatedButton("🧹 Cancelar", on_click=limpar_usuario),
                                        ft.ElevatedButton("↩️ Menu", on_click=lambda e: page.go("/menu"))]),
                                msg_user,
                                ft.Divider(),
                                ft.Text("Lista de Usuários", size=18, weight="bold"),
                                lista_usuarios
                            ], scroll="auto", expand=True, spacing=10),
                        ),
                        ft.Tab(
                            text="📊 Indicadores",
                            content=ft.Column([
                                ft.Text("Cadastro de Indicadores", size=20, weight="bold"),
                                ft.Row([tipo_ind, ano, mes], spacing=10),
                                data_ref, meta, realizado, anterior,
                                ft.Row([ft.ElevatedButton("💾 Salvar", on_click=salvar_indicador),
                                        ft.ElevatedButton("🧹 Cancelar", on_click=limpar_indicador),
                                        ft.ElevatedButton("↩️ Menu", on_click=lambda e: page.go("/menu"))]),
                                msg_ind,
                                ft.Divider(),
                                ft.Text("Filtros", size=18, weight="bold"),
                                ft.Row([filtro_tipo, filtro_ano, btn_filtrar, btn_limpar], spacing=10),
                                ft.Divider(),
                                ft.Text("Lista de Indicadores", size=18, weight="bold"),
                                lista_indicadores
                            ], expand=True, spacing=10),
                        )
                    ]
                )
            ]
        )
    
    def route_change(e):
        page.views.clear()
        # carrega a view certa
        if page.route == "/":
            page.views.append(login_view())
        elif page.route == "/menu":
            page.views.append(menu_view())
        elif page.route == "/vendas":
            page.views.append(vendas_view())
        elif page.route == "/admin":
            page.views.append(admin_view(page))
        elif page.route == "/veiculos":
            page.views.append(fluxo_view())                  # ← aqui!
        elif page.route == "/estacionamento":
            page.views.append(estacionamento_view())
        elif page.route == "/pessoas":
            page.views.append(pessoas_view())
        elif page.route == "/noi":
            page.views.append(noi_view(page))
        page.update()


        # ─── DEBUG ──────────────────────────────────────────
        def log_controls(ctrls, prefix=""):
            for idx, c in enumerate(ctrls):
                if isinstance(c, str):
                    print(f"{prefix}[STR] index={idx}: {repr(c)}")
                else:
                    print(f"{prefix}[{idx}] {type(c)}")
                    if hasattr(c, "controls"):
                        log_controls(c.controls, prefix + "  ")
                    if hasattr(c, "content") and hasattr(c.content, "controls"):
                        log_controls(c.content.controls, prefix + "  ")
        print(f"\n[DEBUG] Rota atual: {page.route}")
        log_controls(page.views[-1].controls)
        # ─────────────────────────────────────────────────

        page.update()

    page.on_route_change = route_change
    page.go("/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    ft.app(main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=port)