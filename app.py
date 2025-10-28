from flask import Flask, render_template, redirect, url_for, session, request, flash
from functools import wraps
from models import db, Usuario, Crianca, Categoria, Card

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "kayla1234csb2025"
# >>> Banco v2 <<<
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///csb_dev_v2.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapper


# categorias padrão da tela “Cards”
DEFAULT_CATEGORIAS = [
    {"nome": "Como está o dia",        "cor": "#B7E0F2"},
    {"nome": "Rotina",                 "cor": "#BEE3F8"},
    {"nome": "O que estou fazendo",    "cor": "#BFE6F2"},
    {"nome": "Como estou me sentindo", "cor": "#FAD4D8"},
    {"nome": "Quero / Preciso",        "cor": "#E6F3C5"},
]

EMOJI_BY_NOME = {
    "Como está o dia": "☀️",
    "Rotina": "🕒",
    "O que estou fazendo": "🧩",
    "Como estou me sentindo": "❤️",
    "Quero / Preciso": "🙋",
}

# -----------------------------------------------------------------------------
# Auth
# -----------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        if not nome or not email:
            flash("Preencha nome e email.")
            return redirect(url_for("login"))

        user = Usuario.query.filter_by(email=email).first()
        if not user:
            user = Usuario(nome=nome, email=email)
            db.session.add(user)
            db.session.commit()

        session["usuario_id"] = user.id
        session["usuario_nome"] = user.nome
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -----------------------------------------------------------------------------
# Views principais
# -----------------------------------------------------------------------------
@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    uid = session["usuario_id"]

    q_criancas = Crianca.query.filter_by(usuario_id=uid).count()
    q_categorias = Categoria.query.filter_by(usuario_id=uid).count()
    q_cards = (
        db.session.query(Card)
        .join(Categoria)
        .filter(Categoria.usuario_id == uid)
        .count()
    )

    return render_template(
        "dashboard.html",
        nome=session.get("usuario_nome"),
        n_criancas=q_criancas,
        n_categorias=q_categorias,
        n_cards=q_cards,
    )

# -----------------------------------------------------------------------------
# Crianças
# -----------------------------------------------------------------------------
@app.route("/criancas", methods=["GET", "POST"], endpoint="criancas_view")
@login_required
def criancas_view():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        idade = request.form.get("idade", "").strip()
        genero = request.form.get("genero", "").strip()
        observacao = request.form.get("observacao", "").strip()

        if not nome:
            flash("Preencha o nome da criança.")
            return redirect(url_for("criancas_view"))

        nova = Crianca(
            usuario_id=session["usuario_id"],
            nome=nome,
            idade=idade,
            genero=genero,
            observacao=observacao,
        )
        db.session.add(nova)
        db.session.commit()
        flash("Criança cadastrada com sucesso!")
        return redirect(url_for("criancas_view"))

    lista = (
        Crianca.query.filter_by(usuario_id=session["usuario_id"])
        .order_by(Crianca.nome)
        .all()
    )
    return render_template("criancas.html", lista=lista)

# -----------------------------------------------------------------------------
# Categorias
# -----------------------------------------------------------------------------
@app.route("/categorias", methods=["GET", "POST"])
@login_required
def categorias():
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        cor = request.form.get("cor", "").strip() or None
        if not nome:
            flash("Informe o nome da categoria.")
            return redirect(url_for("categorias"))

        nova = Categoria(usuario_id=session["usuario_id"], nome=nome, cor=cor)
        db.session.add(nova)
        db.session.commit()
        flash("Categoria criada com sucesso!")
        return redirect(url_for("categorias"))

    lista = (
        Categoria.query.filter_by(usuario_id=session["usuario_id"])
        .order_by(Categoria.ordem, Categoria.nome)
        .all()
    )
    return render_template("categorias.html", lista=lista)


@app.post("/categorias/<int:cat_id>/delete")
@login_required
def categorias_delete(cat_id):
    cat = Categoria.query.filter_by(
        id=cat_id, usuario_id=session["usuario_id"]
    ).first()
    if not cat:
        flash("Categoria não encontrada.")
        return redirect(url_for("categorias"))
    db.session.delete(cat)
    db.session.commit()
    flash("Categoria removida.")
    return redirect(url_for("categorias"))


@app.post("/categorias/<int:cat_id>/update")
@login_required
def categorias_update(cat_id):
    cat = Categoria.query.filter_by(
        id=cat_id, usuario_id=session["usuario_id"]
    ).first_or_404()
    cat.nome = request.form.get("nome", cat.nome).strip() or cat.nome
    cor = request.form.get("cor", "").strip()
    cat.cor = cor or cat.cor
    db.session.commit()
    flash("Categoria atualizada.")
    return redirect(url_for("categorias"))


# -----------------------------------------------------------------------------
# Cards
# -----------------------------------------------------------------------------
@app.route("/cards")
@login_required
def cards_home():
    uid = session["usuario_id"]

    # Garante categorias padrão
    existentes = {c.nome for c in Categoria.query.filter_by(usuario_id=uid).all()}
    novos = [
        Categoria(usuario_id=uid, nome=item["nome"], cor=item["cor"])
        for item in DEFAULT_CATEGORIAS
        if item["nome"] not in existentes
    ]
    if novos:
        db.session.add_all(novos)
        db.session.commit()

    cats = (
        Categoria.query.filter_by(usuario_id=uid)
        .order_by(Categoria.ordem, Categoria.nome)
        .all()
    )
    return render_template("cards.html", categorias=cats, emoji_by_nome=EMOJI_BY_NOME)


@app.route("/cards/<int:cat_id>", methods=["GET", "POST"])
@login_required
def cards_categoria(cat_id):
    cat = Categoria.query.filter_by(
        id=cat_id, usuario_id=session["usuario_id"]
    ).first_or_404()

    if request.method == "POST":
        label = request.form.get("label", "").strip()
        emoji = request.form.get("emoji", "").strip() or "🧩"
        cor = request.form.get("cor", "").strip() or (cat.cor or "#cfeeff")
        fala = request.form.get("fala", "").strip()

        if not label:
            flash("Dê um nome ao card.")
            return redirect(url_for("cards_categoria", cat_id=cat_id))

        novo = Card(
            categoria_id=cat.id, label=label, emoji=emoji, cor=cor, fala=fala
        )
        db.session.add(novo)
        db.session.commit()
        flash("Card criado!")
        return redirect(url_for("cards_categoria", cat_id=cat_id))

    cards = (
        Card.query.filter_by(categoria_id=cat.id)
        .order_by(Card.ordem, Card.label)
        .all()
    )
    return render_template("cards_categoria.html", cat=cat, cards=cards)


@app.post("/cards/<int:cat_id>/<int:card_id>/delete")
@login_required
def cards_delete(cat_id, card_id):
    card = (
        db.session.query(Card)
        .join(Categoria)
        .filter(
            Card.id == card_id,
            Card.categoria_id == cat_id,
            Categoria.usuario_id == session["usuario_id"],
        )
        .first()
    )
    if card:
        db.session.delete(card)
        db.session.commit()
        flash("Card removido.")
    return redirect(url_for("cards_categoria", cat_id=cat_id))

# ----- USUÁRIOS -----
@app.route("/usuarios")
@login_required
def usuarios():
    itens = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios.html", itens=itens)

# ----- CONFIGURAÇÕES DA CONTA -----
@app.route("/conta", methods=["GET", "POST"])
@login_required
def conta():
    user = Usuario.query.get(session["usuario_id"])
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not nome or not email:
            flash("Preencha todos os campos.")
            return redirect(url_for("conta"))

        user.nome = nome
        user.email = email
        db.session.commit()
        session["usuario_nome"] = nome  # atualiza na sessão
        flash("Informações atualizadas com sucesso!")
        return redirect(url_for("dashboard"))

    return render_template("conta.html", user=user)

# ----- CONFIGURAÇÕES GERAIS (preferências + TTS) -----
@app.route("/config", methods=["GET", "POST"])
@login_required
def config_gerais():
    """
    Nesta tela, por enquanto, não vamos gravar no banco.
    Vamos carregar/salvar via localStorage no navegador (feito no template).
    Ainda assim, deixo POST preparado caso depois você queira persistir.
    """
    if request.method == "POST":
        # espaço reservado para futura persistência no banco se desejar
        flash("Configurações salvas.")
        return redirect(url_for("dashboard"))

    return render_template("config_gerais.html")



# -----------------------------------------------------------------------------
# Boot
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
