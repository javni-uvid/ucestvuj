"""The guide to the request for information of public importance (decided 22 Nov 2026: the first guide).

Every rule on the page is a quotation of the law as the register prints it, with the article (and the paragraph where
the paragraphs of the article are numbered as the law itself counts them), and says which version it is from
(principles 2, 6 and 7). What is said in our own words is marked "Својим речима". The letter is made in the reader's
browser (static/site.js); nothing typed is sent anywhere (principle 5).
"""

import html

REGISTER = "https://pravno-informacioni-sistem.rs/"
COMMISSIONER = {"name": "Повереник за информације од јавног значаја и заштиту података о личности",
                "address": "Булевар краља Александра 15, 11000 Београд", "url": "https://www.poverenik.rs/"}
# the Commissioner's address as the catalogue of bodies has it, checked by a test
COMMISSIONER_IN_CATALOGUE = ("Bulevar kralja Aleksandra br. 15", "11000", "Beograd")

# What the letter says. [..] are the places the reader fills in; the form's fields carry the same words as their
# placeholders, and the script puts each field's value in its place.
SLOT = {"organ": "[назив органа власти]", "name": "[ваше име и презиме]", "address": "[ваша адреса]",
        "what": "[опис информације]", "place": "[место и датум]", "form": "[шта тражите]"}
# the forms the law names in article 5 (access: inspection, copy, a copy sent by e-mail, being told whether the body has it)
FORMS = ["увид у документ који садржи следећу информацију",
         "копију документа који садржи следећу информацију",
         "копију документа који садржи следећу информацију, да ми је упутите електронском поштом",
         "обавештење да ли поседујете следећу информацију"]
LETTER = (f"{SLOT['organ']}\n\n"
          "ЗАХТЕВ ЗА ПРИСТУП ИНФОРМАЦИЈАМА ОД ЈАВНОГ ЗНАЧАЈА\n\n"
          "На основу члана 15. Закона о слободном приступу информацијама од јавног значаја тражим од вас: "
          f"{SLOT['form']}:\n\n{SLOT['what']}\n\n"
          "Одговор очекујем у року из члана 16. став 1. овог закона.\n\n"
          f"{SLOT['name']}\n{SLOT['address']}\n{SLOT['place']}\n")


class Missing(Exception):
    """A quoted paragraph is not in the law as read: the law changed, or the reading did; the page must not be built."""


def quote(law: dict, number: str, *which: int, numbered: bool = False) -> str:
    """The paragraphs `which` (0-based) of article `number`, word for word. `numbered`: the article's paragraphs are
    the law's own "ставови" in order, so that the paragraph's place can be said ("став 2")."""
    article = next((a for a in law["articles"] if a["number"] == number), None)
    if article is None:
        raise Missing(f"article {number}")
    try:
        text = [article["paragraphs"][i] for i in which]
    except IndexError:
        raise Missing(f"article {number}, paragraphs {which}") from None
    places = [f"став {i + 1}" for i in which] if numbered else []
    cite = f"Члан {number}." + (" " + ", ".join(places) + "." if places else "")
    body = "".join(f"<p>{html.escape(p)}</p>" for p in text)
    return (f'<blockquote><p class="cite"><a href="{html.escape(law["url"])}">{cite}</a>'
            + (f" {html.escape(article['heading'].split(' · ')[-1])}" if article["heading"] else "") + f"</p>{body}</blockquote>")


def own(text: str) -> str:
    return f'<p class="own"><b>Својим речима:</b> {text}</p>'


# The complaint to the Commissioner (article 22 of the law; what a complaint holds is article 159 of the Law on General
# Administrative Procedure: the decision, the organ, its number and day, the signature). Two grounds, as article 22 gives
# them for the common cases: the request was refused or dismissed, or not answered in time.
CSLOT = {"ground": "[основ жалбе]", "decision": "[број и датум решења]", "request": "[датум захтева]"}
# The organ's name is typed by the reader and cannot be declined by us: it stands in the nominative, after a colon or in brackets.
GROUNDS = [f"против решења органа власти ({SLOT['organ']}; {CSLOT['decision']}) којим је одбијен или одбачен мој захтев за приступ информацијама од јавног значаја",
           f"због тога што орган власти ({SLOT['organ']}) није у прописаном року одговорио на мој захтев за приступ информацијама од јавног значаја (захтев је поднет {CSLOT['request']})"]
COMPLAINT = (f"{COMMISSIONER['name']}\n{COMMISSIONER['address']}\n\n"
             "ЖАЛБА\n\n"
             f"На основу члана 22. Закона о слободном приступу информацијама од јавног значаја изјављујем жалбу {CSLOT['ground']}.\n\n"
             "Предлажем да Повереник наложи органу власти да ми омогући приступ траженој информацији, односно да поступи по мом захтеву.\n\n"
             f"{SLOT['name']}\n{SLOT['address']}\n{SLOT['place']}\n")


def writer(key: str, label: str, fields: str, letter: str) -> str:
    """A letter-writer: a form that the script shows and a letter that is there without it, with its blanks."""
    return f"""<div class="writer" data-letter="{key}">
<form class="filter" hidden aria-label="{label}">
{fields}
<p class="note">Оно што упишете остаје у вашем прегледачу: ништа се не шаље и не чува. Копирајте писмо и пошаљите га сами.</p>
</form>
<label class="letter">Писмо <textarea rows="16" readonly>{html.escape(letter)}</textarea></label>
<p><button type="button" data-done="Копирано." hidden>Копирај писмо</button> <span role="status"></span></p>
</div>"""


def field(label: str, name: str, slot: str, tag: str = "input") -> str:
    if tag == "textarea":
        return f'<label>{label} <textarea name="{name}" rows="4" placeholder="{slot}"></textarea></label>'
    return f'<label>{label} <input name="{name}" placeholder="{slot}" autocomplete="off"></label>'


def choice(label: str, name: str, slot: str, options: list[str]) -> str:
    return f'<label>{label} <select name="{name}" data-token="{slot}">' + "".join(f"<option>{html.escape(o)}</option>" for o in options) + "</select></label>"


def letter_form() -> str:
    return writer("pismo", "Писац захтева", "\n".join([
        field("Орган власти (назив како га он пише, нпр. општинска управа)", "organ", SLOT["organ"]),
        choice("Шта тражите", "form", SLOT["form"], FORMS),
        field("Која информација (што прецизније)", "what", SLOT["what"], "textarea"),
        field("Ваше име и презиме", "name", SLOT["name"]),
        field("Ваша адреса", "address", SLOT["address"]),
        field("Место и датум", "place", SLOT["place"])]), LETTER)


def complaint_form() -> str:
    return writer("zalba", "Писац жалбе", "\n".join([
        choice("Због чега се жалите", "ground", CSLOT["ground"], GROUNDS),
        field("Орган власти (назив како га он пише)", "organ", SLOT["organ"]),
        field("Број и датум решења (ако је орган одлучио)", "decision", CSLOT["decision"]),
        field("Датум вашег захтева (ако орган није одговорио)", "request", CSLOT["request"]),
        field("Ваше име и презиме", "name", SLOT["name"]),
        field("Ваша адреса", "address", SLOT["address"]),
        field("Место и датум", "place", SLOT["place"])]), COMPLAINT)


def page(law: dict, procedure: dict) -> tuple[str, str, str]:
    q = lambda *a, **k: quote(law, *a, **k)
    qp = lambda *a, **k: quote(procedure, *a, **k)
    version = law["in_force_from"].split("-")
    day = f"{int(version[2])}. {int(version[1])}. {version[0]}."
    pv = procedure["in_force_from"].split("-")
    proc_day = f"{int(pv[2])}. {int(pv[1])}. {pv[0]}."
    main = f"""
<h1>Захтев за информације од јавног значаја</h1>
<p class="lead">Свако може да затражи од органа власти информацију којом он располаже, а орган мора да одговори у року који закон одређује. Овде су кораци, и уз сваки члан закона на коме почива.</p>
<p class="note">Ово није правни савет. Одломци су преписани речју по реч из <a href="{html.escape(law['url'])}">регистра Службеног гласника</a> ({html.escape(law['title'])}, {html.escape(law['gazette'])}), пречишћен текст на снази од {day} Оно што је написано „Својим речима“ је наше објашњење, не закон. Како органи у пракси поштују рокове, не знамо и не нагађамо.</p>

<h2>1. Од кога се тражи</h2>
{own("од органа власти: државних органа, органа покрајине, града и општине, јавних предузећа и установа и других које закон набраја. Набрајање је дуже од одломка испод, па га прочитајте цело у регистру.")}
{q("3", 0, 1, 2, 3)}
<p>Адресе органа има Повереников каталог органа власти, на порталу <a href="https://data.gov.rs/">data.gov.rs</a>.</p>

<h2>2. Ко може и да ли треба разлог</h2>
{own("свако, под једнаким условима, и не мора да наведе зашто му треба информација.")}
{q("5", 0, 1)}
{q("6", 0)}
{q("15", 3, numbered=True)}

<h2>3. Шта пише у захтеву</h2>
{own("захтев је писмен и садржи назив органа, ваше име и адресу и што прецизнији опис информације. Ако нешто недостаје, орган вас мора поучити како да допуните, и то без накнаде. Образац може постојати, али се мора размотрити и захтев писан слободно.")}
{q("15", 0, 1, 2, 4, 7, numbered=True)}
<h3>Писмо</h3>
<p>Попуните поља и копирајте писмо. Без скрипте је предложени текст испод, са празнинама у угластим заградама.</p>
{letter_form()}

<h2>4. Рок за одговор</h2>
{own("највише 15 дана од пријема захтева; 48 сати ако се информација тиче живота или слободе неког лица, или угрожавања здравља становништва или животне средине. Орган може, са разлогом, да одреди накнадни рок, најдуже 40 дана.")}
{q("16", 0, 1, 3, numbered=True)}

<h2>5. Колико кошта</h2>
{own("увид је бесплатан; за копију плаћате само нужне трошкове израде (и слања). Од плаћања копије су, под условима које члан наводи, ослобођени новинари, удружења за заштиту људских права и сва лица кад се информација односи на здравље становништва и животну средину.")}
{q("17", 0, 1, 3, numbered=True)}

<h2>6. Ако одбију или ћуте</h2>
{own("ако орган одбије захтев, мора то да учини решењем са образложењем и поуком о правним средствима. Ако одбије, одбаци или не одговори у року, можете изјавити жалбу Поверенику. Повереник одлучује у року од 60 дана, а 30 дана ако се ради о информацији из члана 16. став 2. Колико у пракси траје и како се поступа, не знамо.")}
{q("16", 11, numbered=True)}
{q("22", 0, 1, 2, 3)}
{q("24", 0, 1, numbered=True)}
<p>Шта жалба садржи и када може да се поднесе одређује Закон о општем управном поступку, на који упућује члан 23. Закона о слободном приступу ({html.escape(procedure['gazette'])}, пречишћен текст на снази од {proc_day}):</p>
{qp("159", 0)}
{qp("153", 0, 1)}
{own("довољно је навести решење које побијате и у ком сте погледу незадовољни; ако орган уопште није одговорио, жалба се може поднети и после рока, најкасније годину дана од његовог истека. Писмо испод прави такву жалбу.")}
{complaint_form()}
<p>Жалба се шаље Поверенику: {html.escape(COMMISSIONER['name'])}, {html.escape(COMMISSIONER['address'])} (<a href="{COMMISSIONER['url']}">сајт</a>).</p>
"""
    return ("Захтев за информације од јавног значаја — Учествуј",
            "Како се тражи информација од органа власти: кораци, рокови и чланови закона, и писмо које правите у свом прегледачу.", main)


def _day(law: dict) -> str:
    y, m, d = law["in_force_from"].split("-")
    return f"{int(d)}. {int(m)}. {y}."


def initiative_page(law: dict, statutes: list[dict]) -> tuple[str, str, str]:
    """The citizens' initiative and the citizens' assembly, as the Law on Local Self-Government gives them. What the
    statute of a municipality decides is said to be the statute's; no statute is read yet (docs/decisions/data.md)."""
    q = lambda *a, **k: quote(law, *a, **k)
    main = f"""
<h1>Грађанска иницијатива и збор грађана</h1>
<p class="lead">Грађани могу да предложе скупштини општине или града да донесе акт, и да на збору грађана расправљају о питањима из надлежности локалне самоуправе. Закон одређује основно, а многе појединости оставља статуту општине.</p>
<p class="note">Ово није правни савет. Одломци су преписани речју по реч из <a href="{html.escape(law['url'])}">регистра Службеног гласника</a> ({html.escape(law['title'])}, {html.escape(law['gazette'])}), пречишћен текст на снази од {_day(law)} Оно што је написано „Својим речима“ је наше објашњење, не закон. <b>Статуте општина читамо тек за неколико општина</b> (табела испод); шта је у вашем, пише у њему, а он је у службеном листу ваше општине (сајтове општина налазите на страници <a href="{{home}}opstine.html">Општине</a>). Како се то у пракси одвија, не знамо.</p>

<h2>1. Облици непосредног учешћа</h2>
{own("закон зна три облика: грађанску иницијативу, збор грађана и референдум, и упућује на статут за оно што сам не уређује.")}
{q("67", 0, 1, numbered=True)}

<h2>2. Грађанска иницијатива</h2>
{own("грађани предлажу скупштини да донесе акт, измени статут или распише референдум. Скупштина мора да одржи расправу и да им у року од 60 дана да образложен одговор. Закон одређује и број потписа.")}
{q("68", 0, 1, 2, numbered=True)}
{own("за сам предлог да се спроведе јавна расправа довољно је 100 грађана са бирачким правом; о њему одлучује надлежни одбор скупштине.")}
{q("68", 4, 5, 6, numbered=True)}
<p>Како се потписи прикупљају и проверавају у вашој општини, у закону није написано: упућује се на „прописе који уређују грађанску иницијативу“, а ми те прописе још нисмо прочитали.</p>

<h2>3. Збор грађана</h2>
{own("збор се сазива за део територије општине који одреди статут. Закон не каже ко га сазива ни колико људи је потребно: то је у статуту и у одлуци скупштине општине. Органи и службе општине имају 60 дана да размотре предлоге збора и обавесте грађане.")}
{q("69", 0, 1, 2, 3, 4, numbered=True)}

<h2>4. Референдум на предлог грађана</h2>
{own("скупштина мора да распише референдум о питању из своје надлежности ако то предложи најмање 10% бирача, на начин који одређују закон и статут.")}
{q("70", 1, numbered=True)}

<h2>5. Притужба на рад органа и служби</h2>
{own("свако може да поднесе притужбу на рад органа и служби општине; они одговарају у року од 30 дана ако подносилац одговор захтева.")}
{q("71", 2, 3, numbered=True)}

<h2>6. Шта пише у статутима које смо прочитали</h2>
{own("статути исте државе нису исти: у једној општини збор могу да сазову грађани, у другој не; у једној је за збор потребно 5% бирача, у другој 10%. Зато за своју општину прочитајте њен статут. Испод су они које смо до сада прочитали.")}
<p class="note"><b>Проба, и није проверено:</b> ове вредности је из текста статута прочитао модел, а човек их још није проверио; уз сваку је члан и реченица статута како је написана. Статут је онај који је општина ставила на свој сајт (дан стављања је у колони); измене од тада могу постојати, а важећи текст је у службеном листу општине. Други пут су вредности читане са слика страна статута, и слажу се. Три статута нисмо прочитали јер су скенови без текста.</p>
{statutes_table(statutes)}
"""
    return ("Грађанска иницијатива и збор грађана — Учествуј",
            "Шта закон даје грађанима у општини: иницијатива, збор грађана, референдум и притужба, са члановима закона.", main)


def _convened(f: dict) -> str:
    if not f["citizens_may_convene"]:
        return "Не: грађани нису међу сазивачима"
    text = f"Да: најмање {f['number']} грађана" if f.get("number") else "Да: група грађана (број није наведен)"
    return text + ("; сазивач мора да сазове збор на захтев 10% бирача" if f.get("also") else "")


def statutes_table(rows: list[dict]) -> str:
    esc = html.escape
    body = []
    for r in (r for r in rows if not r.get("superseded_suspected")):
        parts = [("Збор: подручје", r["assembly_area"]), ("Збор: ко сазива", r["convened_by_citizens"]),
                 ("Збор: потребно присутних", r["assembly_quorum"]), ("Иницијатива: потписа", r["initiative_signatures"])]
        quotes = "".join(f"<p><b>{esc(label)}</b>, члан {esc(x['article'])}: {esc(x['quote'])}</p>" for label, x in parts)
        s = r["statute"]
        body.append(
            f'<tr><th scope="row">{esc(r["name"])}</th><td>{esc(_convened(r["convened_by_citizens"]))}</td>'
            f'<td class="num">{r["assembly_quorum"]["percent"]}%</td><td class="num">{r["initiative_signatures"]["percent"]}%</td>'
            f'<td><a href="{esc(s["url"])}">{esc(s["title"])}</a>, на сајту од {_day({"in_force_from": s["uploaded"]})}'
            + (f'<br><small>{esc(r["caveat"])}</small>' if r.get("caveat") else "")
            + f'<details><summary>Чланови и реченице статута</summary>{quotes}</details></td></tr>')
    left = [r for r in rows if r.get("superseded_suspected")]
    note = "".join(f'<p class="note"><b>{esc(r["name"])} није у табели:</b> {esc(r["superseded_suspected"])}</p>' for r in left)
    return (note + '<div class="scroll"><table><thead><tr><th scope="col">Општина</th><th scope="col">Збор: ко га сазива</th>'
            '<th scope="col" class="num">Збор: присутних</th><th scope="col" class="num">Иницијатива: потписа</th>'
            '<th scope="col">Статут</th></tr></thead><tbody>' + "".join(body) + "</tbody></table></div>")


def index_page() -> tuple[str, str, str]:
    main = """
<h1>Водичи</h1>
<p class="lead">Како се учествује у одлукама, корак по корак, уз члан закона на коме сваки корак почива.</p>
<ul class="guides">
<li><a href="{home}zahtev.html">Захтев за информације од јавног значаја</a>: како се тражи информација од органа власти, рокови, жалба Поверенику, и писма која правите у свом прегледачу.</li>
<li><a href="{home}inicijativa.html">Грађанска иницијатива и збор грађана</a>: шта закон даје грађанима у општини, и шта пише у статутима неколико општина које смо прочитали.</li>
</ul>
<p class="note">Водичи нису правни савет. Закони су прочитани из регистра Службеног гласника; статути, за сада, само пет, и нису проверени.</p>
"""
    return ("Водичи — Учествуј", "Водичи кроз начине да се учествује у одлукама, са члановима закона.", main)
