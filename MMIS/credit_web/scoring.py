from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path
import json

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD


C = Namespace('http://www.semanticweb.org/creditworthiness#')
SWRL = Namespace('http://www.w3.org/2003/11/swrl#')
POLICY = json.loads(Path(__file__).with_name('score_policy.json').read_text(encoding='utf-8'))


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    kind: str = 'money'
    options: tuple = ()
    optional: bool = False


EMPLOYMENT = {'SalariedEmployment': 'Работа по найму', 'IndividualEntrepreneurship': 'Индивидуальное предпринимательство', 'SelfEmployment': 'Самозанятость'}
REGULARITY = ('регулярные платежи', 'с просрочками', 'нет предыдущих выплат')
VOLATILITY = ('небольшие колебания', 'существенные колебания')
PERIODICITY = ('ежемесячно', 'нерегулярно в течение месяца')

PROFILE_CHECKS = (
    ('maritalStatus', 'householdBudgetConfirmed', 'Бюджет домохозяйства подтвержден'),
    ('education', 'educationIncomeConfirmed', 'Связь квалификации с заявленным доходом подтверждена'),
    ('residenceRegion', 'localExpensesConfirmed', 'Расходы по месту проживания подтверждены'),
    ('loanPurpose', 'loanPurposeConfirmed', 'Сумма кредита обоснована заявленной целью'),
)

GROUPS = {
    'PersonalData': ('Данные заемщика', (
        Field('ageYears', 'Возраст, лет', 'int', optional=True), Field('maritalStatus', 'Семейное положение', 'text', optional=True),
        Field('householdBudgetConfirmed', PROFILE_CHECKS[0][2], 'bool', optional=True),
        Field('education', 'Образование', 'text', optional=True), Field('educationIncomeConfirmed', PROFILE_CHECKS[1][2], 'bool', optional=True),
        Field('residenceRegion', 'Регион проживания', 'text', optional=True), Field('localExpensesConfirmed', PROFILE_CHECKS[2][2], 'bool', optional=True))),
    'IncomeEmployment': ('Доход', (
        Field('officialMonthlyIncome', 'Официальный доход в месяц'), Field('additionalMonthlyIncome', 'Дополнительный доход в месяц'),
        Field('additionalIncomeSource', 'Источники дополнительного дохода, по одному на строку', 'list', optional=True),
        Field('totalWorkExperienceMonths', 'Общий стаж, мес.', 'int'))),
    'Employment': ('Занятость', (Field('employmentType', 'Вид занятости', 'choice', tuple(EMPLOYMENT)),
        Field('currentWorkExperienceMonths', 'Стаж на текущем месте, мес.', 'int'))),
    'IncomeStability': ('Стабильность дохода', (Field('incomeVolatility', 'Колебания дохода', 'choice', VOLATILITY),
        Field('incomePeriodicity', 'Регулярность поступлений', 'choice', PERIODICITY))),
    'Expenses': ('Расходы', (Field('monthlyUtilities', 'ЖКХ в месяц'), Field('monthlyRent', 'Аренда в месяц'),
        Field('monthlyOtherExpenses', 'Прочие расходы в месяц'), Field('monthlyCommunication', 'Связь и интернет в месяц'),
        Field('monthlyTransport', 'Транспорт в месяц'), Field('monthlyFood', 'Питание в месяц'), Field('dependentCount', 'Иждивенцы', 'int'))),
    'RequestedLoan': ('Запрашиваемый кредит', (Field('requestedAmount', 'Сумма кредита'), Field('termMonths', 'Срок, мес.', 'int'),
        Field('loanPurpose', 'Цель кредита', 'text', optional=True), Field('loanPurposeConfirmed', PROFILE_CHECKS[3][2], 'bool', optional=True))),
    'CreditHistory': ('Кредитная история', (Field('previousLoanCount', 'Предыдущие кредиты', 'int'),)),
    'PaymentHistory': ('История выплат', (Field('overdueCount', 'Количество просрочек', 'int'),
        Field('creditHistoryMonths', 'Длительность кредитной истории, мес.', 'int'), Field('paymentRegularity', 'Регулярность платежей', 'choice', REGULARITY))),
    'CreditRating': ('Рейтинг БКИ', (Field('bureauScore', 'Балл БКИ, шкала модели 0–1000', 'int', optional=True),)),
    'CurrentCreditLoad': ('Текущие долги', (Field('activeLoanCount', 'Активные кредиты', 'int'),
        Field('outstandingDebt', 'Остаток задолженности'), Field('monthlyDebtPayments', 'Долговые платежи в месяц'))),
    'Savings': ('Сбережения и активы', (Field('hasSavingsAvailable', 'Есть сбережения', 'bool'), Field('accountBalance', 'Остатки на счетах'),
        Field('hasAssets', 'Есть активы', 'bool'))),
}

LINKS = {
    'PersonalData': ('Assessment', 'hasPersonalData'), 'IncomeEmployment': ('Assessment', 'hasIncomeEmployment'),
    'Employment': ('IncomeEmployment', 'hasEmployment'), 'Expenses': ('Assessment', 'hasExpenses'),
    'RequestedLoan': ('Assessment', 'hasRequestedLoan'), 'CreditHistory': ('Assessment', 'hasCreditHistory'),
    'PaymentHistory': ('CreditHistory', 'hasPaymentHistory'), 'CreditRating': ('CreditHistory', 'hasCreditRating'),
    'CurrentCreditLoad': ('CreditHistory', 'hasCurrentCreditLoad'), 'FinancialIndicators': ('Assessment', 'hasFinancialIndicators'),
    'IncomeStability': ('FinancialIndicators', 'hasIncomeStability'), 'Savings': ('FinancialIndicators', 'hasSavings'),
}

POINTS = {
    'profilePoints': 'Данные заемщика и цель кредита', 'affordabilityPoints': 'Платежеспособность',
    'incomePoints': 'Доход и занятость', 'historyPoints': 'Кредитная история',
    'savingsPoints': 'Сбережения и активы', 'debtPoints': 'Текущие долги',
}

DECISIONS = {'GrantCredit': 'Выдать кредит', 'DoNotGrantCredit': 'Не выдавать кредит'}
FIELDS = tuple(field for _, fields in GROUPS.values() for field in fields)


def parse_fields(form):
    data, errors = {}, []
    for f in FIELDS:
        raw = str(form.get(f.key, '')).strip()
        if not raw:
            data[f.key] = [] if f.kind == 'list' else None
            if not f.optional:
                errors.append(f'Заполните поле «{f.label}».')
            continue
        try:
            if f.kind in ('money', 'int'):
                value = Decimal(raw.replace(',', '.'))
                if not value.is_finite() or not 0 <= value <= 10**12:
                    raise ValueError
                if f.kind == 'int':
                    if value != value.to_integral_value():
                        raise ValueError
                    value = int(value)
                else:
                    if value != value.quantize(Decimal('.01')):
                        raise ValueError
                    value = str(value.quantize(Decimal('.01')))
            elif f.kind == 'bool':
                value = {'yes': True, 'no': False}[raw]
            elif f.kind == 'choice':
                if raw not in f.options:
                    raise ValueError
                value = raw
            else:
                if len(raw) > (1000 if f.kind == 'list' else 160):
                    raise ValueError
                value = list(dict.fromkeys(line.strip() for line in raw.splitlines() if line.strip())) if f.kind == 'list' else raw
            data[f.key] = value
        except (InvalidOperation, ValueError, KeyError):
            errors.append(f'Проверьте значение в поле «{f.label}».')
    if not errors:
        if not 1 <= data['termMonths'] <= 360 or Decimal(data['requestedAmount']) <= 0:
            errors.append('Укажите положительную сумму кредита и срок от 1 до 360 месяцев.')
        if data['ageYears'] is not None and not 0 < data['ageYears'] <= 120:
            errors.append('Возраст должен быть от 1 до 120 лет.')
        if data['bureauScore'] is not None and data['bureauScore'] > 1000:
            errors.append('В этой модели балл БКИ должен быть от 0 до 1000.')
        if data['currentWorkExperienceMonths'] > data['totalWorkExperienceMonths']:
            errors.append('Стаж на текущем месте не может превышать общий стаж.')
        if data['activeLoanCount'] == 0 and (Decimal(data['outstandingDebt']) or Decimal(data['monthlyDebtPayments'])):
            errors.append('При нуле активных кредитов укажите нулевые остаток долга и платежи.')
        if not data['hasSavingsAvailable'] and Decimal(data['accountBalance']) > 0:
            errors.append('Положительный остаток на счетах должен сопровождаться отметкой о наличии сбережений.')
        for source, confirmation, label in PROFILE_CHECKS:
            if data[confirmation] is not None and data[source] is None:
                errors.append(f'Для проверки «{label}» сначала укажите исходные сведения.')
    return data, errors


def signed(value):
    return f'+{value}' if value > 0 else str(value).replace('-', '−')


def personal_contributions(data):
    age = data.get('ageYears')
    tenure = data['totalWorkExperienceMonths']
    if age is None or tenure == 0:
        result = [('Возраст и стаж: данных для сопоставления недостаточно', 0)]
    elif tenure <= max(0, age - 14) * 12:
        result = [('Возраст и стаж: указанный стаж укладывается в период с 14 лет', 2)]
    else:
        result = [('Возраст и стаж: указанный стаж превышает период с 14 лет', -2)]
    for source, confirmation, label in PROFILE_CHECKS:
        value = data.get(confirmation) if data.get(source) else None
        status = {True: 'да', False: 'нет', None: 'не проверено'}[value]
        result.append((f'{label}: {status}', {True: 2, False: -2, None: 0}[value]))
    return result


def evaluate(data, jobs):
    def number(key):
        return Decimal(data[key])

    official, extra = number('officialMonthlyIncome'), number('additionalMonthlyIncome')
    income = official + extra
    existing = number('monthlyDebtPayments')
    expenses = sum((number(f.key) for f in GROUPS['Expenses'][1] if f.kind == 'money'), Decimal(0))
    rate = Decimal(POLICY['annualRate'])
    with localcontext() as ctx:
        ctx.prec = 40
        months = data['termMonths']
        principal = number('requestedAmount')
        monthly_rate = rate / 12
        factor = (1 + monthly_rate) ** months
        payment = (principal * monthly_rate * factor / (factor - 1) if monthly_rate else principal / months).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
    current_dti = existing / income if income else None
    projected = (existing + payment) / income if income else None
    budget = income - expenses - existing - payment
    reserve = budget / income if income else None
    dti_points = -10
    if projected is not None:
        for threshold, contribution in (('.30', 10), ('.40', 6), ('.50', -2), ('.60', -7)):
            if projected <= Decimal(threshold):
                dti_points = contribution
                break
    buffer = Decimal('.02') * min(data['dependentCount'], 3)
    budget_points = -9
    if reserve is not None:
        for threshold, contribution in (('.25', 9), ('.15', 5), ('.10', 1)):
            if reserve >= Decimal(threshold) + buffer:
                budget_points = contribution
                break
        else:
            budget_points = -5 if reserve >= 0 else -9
    tenure = data['totalWorkExperienceMonths']
    current = max((job['currentWorkExperienceMonths'] for job in jobs if job['employmentType'] in EMPLOYMENT), default=0)
    count, history_months = data['previousLoanCount'], data['creditHistoryMonths']
    overdue, bki = data['overdueCount'], data['bureauScore']
    monthly_burden = expenses + existing + payment
    coverage = number('accountBalance') / monthly_burden if monthly_burden else 0
    debt_ratio = number('outstandingDebt') / (income * 12) if income else None
    savings_points = -4
    if data['hasSavingsAvailable']:
        savings_points = 6 if coverage >= 3 else 3 if coverage >= 1 else 1 if coverage >= Decimal('.5') else -1
    debt_points = -2
    if debt_ratio is not None:
        debt_points = 2 if debt_ratio <= Decimal('.25') else 1 if debt_ratio <= Decimal('.50') else 0 if debt_ratio <= 1 else -2
    detail = {
        'profilePoints': personal_contributions(data),
        'affordabilityPoints': [('Долговая нагрузка с новым кредитом', dti_points), ('Остаток бюджета после расходов и платежей', budget_points)],
        'incomePoints': [
            ('Общий стаж', 2 if tenure >= 24 else 0 if tenure >= 6 else -2),
            ('Стаж в указанных видах занятости', 2 if current >= 12 else 0 if current >= 3 else -2),
            ('Колебания дохода', 1 if data['incomeVolatility'] == VOLATILITY[0] else -1),
            ('Регулярность поступлений', 1 if data['incomePeriodicity'] == PERIODICITY[0] else -1),
            ('Описание источников дохода', (1 if data['additionalIncomeSource'] else -1) if extra > 0 else (1 if official > 0 else 0))],
        'historyPoints': [
            ('Просрочки', 6 if overdue == 0 and count > 0 else 2 if overdue == 0 else -1 if overdue == 1 else -4 if overdue == 2 else -6),
            ('Регулярность выплат', {REGULARITY[0]: 1, REGULARITY[1]: -1}.get(data['paymentRegularity'], 0)),
            ('Количество предыдущих кредитов и срок истории', 3 if count >= 2 and history_months >= 24 else 1 if count and history_months else 0),
            ('Балл БКИ', 0 if bki is None else 2 if bki >= 750 else 0 if bki >= 550 else -2)],
        'savingsPoints': [
            ('Запас сбережений в месяцах расходов и платежей', savings_points),
            ('Наличие активов', 1 if data['hasAssets'] else -1)],
        'debtPoints': [
            ('Активные кредиты', 1 if data['activeLoanCount'] <= 1 else 0 if data['activeLoanCount'] == 2 else -1),
            ('Остаток долга относительно годового дохода', debt_points)],
    }
    reasons = []
    if income == 0:
        reasons.append('Нет положительного месячного дохода.')
    if projected is not None and projected > Decimal('.60'):
        reasons.append('Долговая нагрузка с новым кредитом превышает 60% дохода.')
    if budget < 0:
        reasons.append('Расходы и платежи превышают месячный доход.')
    penalty = POLICY['criticalAdjustment'] if reasons else 0
    points = {group: sum(item[1] for item in items) for group, items in detail.items()}
    score = sum(points.values()) + penalty
    decision = 'GrantCredit' if score >= POLICY['approvalThreshold'] else 'DoNotGrantCredit'
    return dict(income=income, rate=rate, payment=payment, current_dti=current_dti, projected_dti=projected,
                existing=existing, expenses=expenses, budget=budget, points=points, detail=detail, reasons=reasons,
                penalty=penalty, score=score, decision=decision, label=DECISIONS[decision])


def read_profiles(graph):
    profiles = {}
    for row in graph.query('''
        PREFIX credit: <http://www.semanticweb.org/creditworthiness#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?assessment ?profile ?name WHERE {
            ?assessment a credit:CreditworthinessAssessment ; credit:hasPersonalData ?profile .
            ?profile rdfs:label ?name . FILTER (LANG(?name) = "ru")
        } ORDER BY ?profile'''):
        nodes = {'Assessment': row.assessment}
        for key, (parent, prop) in LINKS.items():
            objects = list(graph.objects(nodes[parent], C[prop]))
            nodes[key] = objects if key == 'Employment' else objects[0]
        data, jobs = {}, []
        for key, (_, fields) in GROUPS.items():
            if key == 'Employment':
                for job in sorted(nodes[key]):
                    kind = next((str(t).split('#')[-1] for t in graph.objects(job, RDF.type) if str(t).split('#')[-1] in EMPLOYMENT), None)
                    duration = graph.value(job, C.currentWorkExperienceMonths)
                    jobs.append({'employmentType': kind, 'currentWorkExperienceMonths': int(duration)})
                continue
            for f in fields:
                values = sorted(graph.objects(nodes[key], C[f.key]))
                data[f.key] = [str(v) for v in values] if f.kind == 'list' else (
                    (str(values[0]) if f.kind == 'money' else values[0].toPython()) if values else None)
        key = str(row.profile).removeprefix(str(C))
        profiles[key] = dict(id=key, name=str(row.name), data=data, jobs=jobs, assessment=row.assessment)
    return profiles


def add_profile(graph, profile):
    key = profile['id']
    data, jobs = profile['data'], profile['jobs']
    nodes = {'Assessment': C[f'assessment_{key}']}
    graph.add((nodes['Assessment'], RDF.type, OWL.NamedIndividual))
    graph.add((nodes['Assessment'], RDF.type, C.CreditworthinessAssessment))
    for group, (parent, prop) in LINKS.items():
        entries = jobs if group == 'Employment' else [data]
        for idx, values in enumerate(entries):
            node = C[key] if group == 'PersonalData' else C[f'{group}_{key}_{idx}']
            nodes[group] = node
            graph.add((nodes[parent], C[prop], node))
            graph.add((node, RDF.type, OWL.NamedIndividual))
            graph.add((node, RDF.type, C[values['employmentType'] if group == 'Employment' else group]))
            if group == 'PersonalData':
                graph.add((node, RDFS.label, Literal(profile['name'], lang='ru')))
            for f in GROUPS.get(group, ('', ()))[1]:
                val = values.get(f.key)
                if val is None or f.key == 'employmentType':
                    continue
                dt = {'money': XSD.decimal, 'int': XSD.integer, 'bool': XSD.boolean}.get(f.kind, XSD.string)
                if f.kind == 'int':
                    dt = XSD.positiveInteger if f.key == 'termMonths' else XSD.nonNegativeInteger
                for item in val if f.kind == 'list' else [val]:
                    graph.add((node, C[f.key], Literal(item, datatype=dt)))
    graph.add((nodes['FinancialIndicators'], C.hasDtiIncomeBasis, nodes['IncomeEmployment']))
    graph.add((nodes['FinancialIndicators'], C.hasDtiPaymentBasis, nodes['CurrentCreditLoad']))
    result = evaluate(data, jobs)
    graph.add((nodes['IncomeEmployment'], C.monthlyIncome, Literal(result['income'], datatype=XSD.decimal)))
    if result['current_dti'] is not None:
        graph.add((nodes['FinancialIndicators'], C.dtiRatio, Literal(result['current_dti'].quantize(Decimal('.000001'), rounding=ROUND_HALF_UP), datatype=XSD.decimal)))
    return nodes['Assessment']


def score_graph(graph, profiles, *, with_results):
    graph.bind('credit', C)
    assessment = C.CreditworthinessAssessment
    graph.set((assessment, RDFS.comment, Literal('Оценка заемщика и запрашиваемого кредита. Итоговый балл складывается из вкладов, решение определяется сравнением с порогом.', lang='ru')))
    for key, label in DECISIONS.items():
        graph.add((C[key], RDF.type, OWL.NamedIndividual))
        graph.add((C[key], RDF.type, C.CreditDecision))
        graph.add((C[key], RDFS.label, Literal(label, lang='ru')))
    graph.add((C.CreditDecision, RDF.type, OWL.Class))
    graph.add((C.CreditDecision, RDFS.label, Literal('Решение по кредиту', lang='ru')))
    graph.add((C.CreditDecision, RDFS.comment, Literal('Итог сравнения балла с порогом выдачи.', lang='ru')))
    graph.add((C.CreditDecision, OWL.disjointWith, assessment))
    graph.add((C.GrantCredit, OWL.differentFrom, C.DoNotGrantCredit))
    graph.add((C.hasCreditDecision, RDF.type, OWL.ObjectProperty))
    graph.add((C.hasCreditDecision, RDFS.domain, assessment))
    graph.add((C.hasCreditDecision, RDF.type, OWL.FunctionalProperty))
    graph.add((C.hasCreditDecision, RDFS.range, C.CreditDecision))
    graph.add((C.hasCreditDecision, RDFS.label, Literal('решение по кредиту', lang='ru')))
    graph.add((C.hasCreditDecision, RDFS.comment, Literal('Значение выводится по итоговому баллу и порогу выдачи.', lang='ru')))
    properties = {
        **{key: (title, XSD.double) for key, title in POINTS.items()},
        'riskAdjustment': ('Поправка за критические условия', XSD.double),
        'creditScore': ('Итоговый балл', XSD.double), 'approvalThreshold': ('Порог выдачи', XSD.double),
        'proposedMonthlyPayment': ('Новый месячный платеж', XSD.decimal), 'projectedDtiRatio': ('Прогнозная долговая нагрузка', XSD.decimal),
        'budgetAfterLoan': ('Остаток бюджета', XSD.decimal), 'monthlyExpenseTotal': ('Сумма недолговых расходов', XSD.decimal),
        'scenarioAnnualRate': ('Годовая ставка', XSD.decimal), 'policyVersion': ('Версия оценки', XSD.string),
        'hasScoreReason': ('Обоснование оценки', XSD.string),
    }
    for key, (label, dt) in properties.items():
        graph.add((C[key], RDF.type, OWL.DatatypeProperty))
        graph.add((C[key], RDFS.domain, assessment))
        graph.add((C[key], RDFS.range, dt))
        graph.add((C[key], RDFS.label, Literal(label, lang='ru')))
        graph.add((C[key], RDFS.comment, Literal('Показатель модели оценки кредитоспособности.', lang='ru')))
        if key != 'hasScoreReason':
            graph.add((C[key], RDF.type, OWL.FunctionalProperty))
    for source, key, title in PROFILE_CHECKS:
        graph.add((C[key], RDF.type, OWL.DatatypeProperty))
        graph.add((C[key], RDF.type, OWL.FunctionalProperty))
        graph.add((C[key], RDFS.domain, C.RequestedLoan if source == 'loanPurpose' else C.PersonalData))
        graph.add((C[key], RDFS.range, XSD.boolean))
        graph.add((C[key], RDFS.label, Literal(title, lang='ru')))
        graph.add((C[key], RDFS.comment, Literal('Результат проверки. Отсутствие значения означает, что проверка не проводилась.', lang='ru')))
    for profile in profiles.values():
        node = profile['assessment'] if 'assessment' in profile else add_profile(graph, profile)
        for key in properties:
            graph.remove((node, C[key], None))
        graph.remove((node, C.hasCreditDecision, None))
        result = evaluate(profile['data'], profile['jobs'])
        values = {**result['points'], 'riskAdjustment': result['penalty'], 'approvalThreshold': POLICY['approvalThreshold'],
                  'proposedMonthlyPayment': result['payment'], 'budgetAfterLoan': result['budget'], 'monthlyExpenseTotal': result['expenses'],
                  'scenarioAnnualRate': result['rate'], 'policyVersion': POLICY['version']}
        if result['projected_dti'] is not None:
            values['projectedDtiRatio'] = result['projected_dti'].quantize(Decimal('.000001'), rounding=ROUND_HALF_UP)
        for key, value in values.items():
            graph.add((node, C[key], Literal(value, datatype=properties[key][1])))
        for items in result['detail'].values():
            for title, points in items:
                graph.add((node, C.hasScoreReason, Literal(f'{title} · {signed(points)}')))
        for note in result['reasons']:
            graph.add((node, C.hasScoreReason, Literal(note)))
        if with_results:
            graph.add((node, C.creditScore, Literal(result['score'], datatype=XSD.double)))
            graph.add((node, C.hasCreditDecision, C[result['decision']]))
    return graph
