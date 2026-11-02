from flask import Flask, render_template, request, jsonify
import rdflib

app = Flask(__name__, template_folder='templates')

graph = rdflib.Graph()
graph.parse("medic4.owl", format="xml")

NS = "http://www.semanticweb.org/user1/ontologies/2025/8/med#"
namespaces = {"ex": NS}
EX = rdflib.Namespace(NS)


def q_to_dicts(q, keys):
    out = []
    for row in graph.query(q, initNs=namespaces):
        out.append({k: (str(row[k]) if row[k] is not None else "") for k in keys})
    return out


def get_all_drugs():
    return q_to_dicts(f"""
        PREFIX ex: <{NS}>
        SELECT ?drugName ?manufacturer ?form ?group ?common
        WHERE {{
            ?drug a ex:Лекарство ;
                  ex:Название_лекарства ?drugName ;
                  ex:Производитель ?manufacturer ;
                  ex:ФормаВыпуска ?form .
            OPTIONAL {{ ?drug ex:ФармакологическаяГруппа ?group }}
            OPTIONAL {{ ?drug ex:Общее_имя ?common }}
        }}
        ORDER BY ASC(?drugName)
    """, ["drugName", "manufacturer", "form", "group", "common"])


def get_clinical_trials():
    return q_to_dicts(f"""
        PREFIX ex: <{NS}>
        SELECT ?nazzab ?nazlek ?eff ?bez ?dan
        WHERE {{
            ?rez ex:Исследовалась ?zab .
            ?zab ex:НазваниеЗаболевания ?nazzab .
            ?rez ex:Исследовалось ?lek .
            ?lek ex:Название_лекарства ?nazlek .
            ?rez ex:ПоказательЭффективности ?eff .
            ?rez ex:ПоказательБезопасности ?bez .
            ?rez ex:ИсточникДанных ?dan .
        }}
        ORDER BY ASC(?nazzab) ASC(?nazlek)
    """, ["nazzab", "nazlek", "eff", "bez", "dan"])


def get_diseases():
    return q_to_dicts(f"""
        PREFIX ex: <{NS}>
        SELECT ?name ?group ?mkb
        WHERE {{
            ?d a ex:Заболевание ;
               ex:НазваниеЗаболевания ?name .
            OPTIONAL {{ ?d ex:ГруппаЗаболевания ?group }}
            OPTIONAL {{ ?d ex:КодМКБ ?mkb }}
        }}
        ORDER BY ASC(?name)
    """, ["name", "group", "mkb"])


def get_patients():
    return q_to_dicts(f"""
        PREFIX ex: <{NS}>
        SELECT ?fio ?allergy
        WHERE {{
            ?p a ex:Пациент ;
               ex:ФИО ?fio .
            OPTIONAL {{ ?p ex:ИнформацияОбАллергиях ?allergy }}
        }}
        ORDER BY ASC(?fio)
    """, ["fio", "allergy"])


def get_recommendations(disease_name, patient_allergy=""):
    q = f"""
        PREFIX ex: <{NS}>
        SELECT ?drug ?manufacturer ?form ?group ?eff ?bez ?notes
        WHERE {{
            ?rez a ex:Результаты_клинических_испытаний ;
                 ex:Исследовалась ?zab ;
                 ex:Исследовалось ?lek .
            ?zab ex:НазваниеЗаболевания ?zname .
            FILTER (LCASE(STR(?zname)) = LCASE("{disease_name}"))

            ?lek ex:Название_лекарства ?drug .
            OPTIONAL {{ ?lek ex:Производитель ?manufacturer }}
            OPTIONAL {{ ?lek ex:ФормаВыпуска ?form }}
            OPTIONAL {{ ?lek ex:ФармакологическаяГруппа ?group }}

            OPTIONAL {{ ?rez ex:ПоказательЭффективности ?eff }}
            OPTIONAL {{ ?rez ex:ПоказательБезопасности ?bez }}
            OPTIONAL {{ ?rez ex:ЗаметкиИспытаний ?notes }}
        }}
    """
    rows = list(graph.query(q, initNs=namespaces))
    if not rows:
        return []

    agg = {}
    for r in rows:
        name = str(r["drug"])
        eff = float(r["eff"]) if r["eff"] is not None else 0.0
        bez = float(r["bez"]) if r["bez"] is not None else 0.0
        if name not in agg:
            agg[name] = {
                "drug": name,
                "manufacturer": str(r["manufacturer"] or ""),
                "form": str(r["form"] or ""),
                "group": str(r["group"] or ""),
                "eff": eff,
                "bez": bez,
                "notes": [str(r["notes"])] if r["notes"] else [],
            }
        else:
            agg[name]["eff"] = max(agg[name]["eff"], eff)
            agg[name]["bez"] = max(agg[name]["bez"], bez)
            if r["notes"]:
                agg[name]["notes"].append(str(r["notes"]))


    allergy_lc = patient_allergy.strip().lower()

    result = []
    for d in agg.values():
        eff = d["eff"]
        bez = d["bez"]
        score = round(0.6 * eff + 0.4 * bez, 3)
        warning = ""
        if allergy_lc and allergy_lc not in ("нет", "none", ""):
            hay = f"{d['drug']} {d['group']} {d['manufacturer']}".lower()
            for word in [w for w in allergy_lc.replace(",", " ").split() if len(w) > 2]:
                if word in hay:
                    warning = f"Возможная аллергия: {patient_allergy}"
                    break
        d["score"] = score
        d["warning"] = warning
        d["notes"] = "; ".join(d["notes"]) if d["notes"] else ""
        result.append(d)

    result.sort(key=lambda x: x["score"], reverse=True)
    return result


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/drugs', methods=['GET', 'POST'])
def display_drugs():
    drugs = get_all_drugs()
    manufacturers = sorted({d["manufacturer"] for d in drugs if d["manufacturer"]})
    forms = sorted({d["form"] for d in drugs if d["form"]})
    groups = sorted({d["group"] for d in drugs if d["group"]})
    return render_template(
        'drugs.html',
        drugs=drugs,
        manufacturers=manufacturers,
        forms=forms,
        groups=groups,
    )


@app.route('/clinical_trials', methods=['GET', 'POST'])
def display_clinical_trials():
    trials = get_clinical_trials()
    diseases = sorted({t["nazzab"] for t in trials if t["nazzab"]})
    drugs = sorted({t["nazlek"] for t in trials if t["nazlek"]})
    return render_template(
        'clinical_trials.html',
        clinical_trials=trials,
        diseases=diseases,
        drugs=drugs,
    )


@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    diseases = get_diseases()
    patients = get_patients()
    selected_disease = ""
    selected_patient = ""
    recs = []
    if request.method == 'POST':
        selected_disease = request.form.get('disease', '').strip()
        selected_patient = request.form.get('patient', '').strip()
        allergy = ""
        if selected_patient:
            for p in patients:
                if p["fio"] == selected_patient:
                    allergy = p["allergy"]
                    break
        if selected_disease:
            recs = get_recommendations(selected_disease, allergy)
    return render_template(
        'recommendations.html',
        diseases=diseases,
        patients=patients,
        selected_disease=selected_disease,
        selected_patient=selected_patient,
        recs=recs,
    )


if __name__ == '__main__':
    app.run(debug=True)