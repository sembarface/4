import json
import os
import sqlite3
from contextlib import asynccontextmanager, closing
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from rdflib import Graph
from rdflib.namespace import RDF

from scoring import EMPLOYMENT, GROUPS, POINTS, POLICY, SWRL, evaluate, parse_fields, read_profiles, score_graph, signed

ROOT = Path(__file__).resolve().parent


def database(app):
    return closing(sqlite3.connect(app.state.db))


def profiles(app):
    with database(app) as db:
        rows = db.execute('SELECT payload FROM borrowers ORDER BY rowid').fetchall()
    added = [json.loads(payload) for (payload,) in rows]
    return {**app.state.initial, **{profile['id']: profile for profile in added if profile['id'] not in app.state.initial}}


@asynccontextmanager
async def lifespan(app):
    path = Path(os.environ.get('CREDIT_ONTOLOGY_PATH', ROOT.parent / 'credit_ontology.owl'))
    app.state.ontology = Graph().parse(path, format='xml')
    if (None, RDF.type, SWRL.Imp) not in app.state.ontology:
        raise RuntimeError(f'В онтологии {path} нет правил SWRL.')
    app.state.initial = read_profiles(app.state.ontology)
    app.state.db = Path(os.environ.get('CREDIT_DB_PATH', ROOT / 'borrowers.sqlite3'))
    with database(app) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS borrowers (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')
    yield


def money(value):
    return f'{Decimal(value):,.2f}'.replace(',', '\u202f').replace('.', ',') + '\u00a0₽'


def percent(value):
    return 'Не определена' if value is None else f'{value * 100:.2f}'.replace('.', ',') + '\u00a0%'


def show_value(value, kind):
    if value is None or value == []:
        return 'Не указано'
    if kind == 'bool':
        return 'Да' if value else 'Нет'
    if kind == 'money':
        return money(value)
    if kind == 'list':
        return '; '.join(value)
    return EMPLOYMENT.get(value, value)


app = FastAPI(title='Оценка кредитоспособности', lifespan=lifespan)
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
templates = Jinja2Templates(directory=ROOT / 'templates')
templates.env.filters.update(money=money, percent=percent, show_value=show_value, signed=signed)


@app.get('/', response_class=HTMLResponse)
def index(request: Request, profile: str | None = None):
    all_profiles = profiles(request.app)
    selected = all_profiles.get(profile) if profile else next(iter(all_profiles.values()), None)
    result = evaluate(selected['data'], selected['jobs']) if selected else None
    return templates.TemplateResponse(request=request, name='index.html', context={
        'profiles': all_profiles.values(), 'selected': selected, 'result': result, 'groups': GROUPS,
        'points': POINTS, 'policy': POLICY,
    }, status_code=404 if profile and not selected else 200)


@app.get('/borrowers/new', response_class=HTMLResponse)
def new_borrower(request: Request):
    return render_form(request)


def render_form(request, values=None, errors=()):
    return templates.TemplateResponse(request=request, name='new.html', context={
        'groups': GROUPS, 'employment_types': EMPLOYMENT, 'values': values or {}, 'errors': errors,
    }, status_code=422 if errors else 200)


@app.post('/borrowers/new', response_class=HTMLResponse)
async def create_borrower(request: Request):
    async with request.form(max_fields=50, max_files=0) as submitted:
        form = dict(submitted)
    data, errors = parse_fields(form)
    name = str(form.get('name', '')).strip()
    if not 1 <= len(name) <= 100:
        errors.insert(0, 'Укажите имя или обозначение профиля длиной до 100 символов.')
    if errors:
        return render_form(request, form, errors)
    profile = {'id': f'profile_{uuid4().hex}', 'name': name, 'data': data, 'jobs': [{
        'employmentType': data.pop('employmentType'), 'currentWorkExperienceMonths': data.pop('currentWorkExperienceMonths')}]}
    with database(request.app) as db, db:
        db.execute('INSERT INTO borrowers VALUES (?, ?)', (profile['id'], json.dumps(profile, ensure_ascii=False)))
    return RedirectResponse(request.url_for('index').include_query_params(profile=profile['id']), status_code=303)


@app.get('/ontology.owl', name='export_ontology')
def export_ontology(request: Request):
    graph = Graph() + request.app.state.ontology
    score_graph(graph, profiles(request.app), with_results=True)
    return Response(graph.serialize(format='xml', encoding='utf-8'), media_type='application/rdf+xml',
                    headers={'Content-Disposition': 'attachment; filename="credit_ontology_export.owl"'})
