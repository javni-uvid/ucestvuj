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


def letter_form() -> str:
    """The letter-writer: a form that the script shows and a letter that is there without it, with its blanks."""
    esc = html.escape
    options = "".join(f"<option>{esc(v)}</option>" for v in FORMS)
    return f"""<div class="writer">
<form id="pismo-forma" class="filter" hidden aria-label="Писац захтева">
<label>Орган власти (назив како га он пише, нпр. општинска управа) <input name="organ" placeholder="{SLOT['organ']}" autocomplete="off"></label>
<label>Шта тражите <select name="form" data-token="{SLOT['form']}">{options}</select></label>
<label>Која информација (што прецизније) <textarea name="what" rows="4" placeholder="{SLOT['what']}"></textarea></label>
<label>Ваше име и презиме <input name="name" placeholder="{SLOT['name']}" autocomplete="off"></label>
<label>Ваша адреса <input name="address" placeholder="{SLOT['address']}" autocomplete="off"></label>
<label>Место и датум <input name="place" placeholder="{SLOT['place']}" autocomplete="off"></label>
<p class="note">Оно што упишете остаје у вашем прегледачу: ништа се не шаље и не чува. Копирајте писмо и пошаљите га сами.</p>
</form>
<label class="letter">Писмо <textarea id="pismo" rows="16" readonly>{esc(LETTER)}</textarea></label>
<p><button type="button" id="pismo-kopija" data-done="Копирано." hidden>Копирај писмо</button> <span id="pismo-stanje" role="status"></span></p>
</div>"""


def page(law: dict) -> tuple[str, str, str]:
    q = lambda *a, **k: quote(law, *a, **k)
    version = law["in_force_from"].split("-")
    day = f"{int(version[2])}. {int(version[1])}. {version[0]}."
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
<p>Жалба се шаље Поверенику: {html.escape(COMMISSIONER['name'])}, {html.escape(COMMISSIONER['address'])} (<a href="{COMMISSIONER['url']}">сајт</a>).</p>
"""
    return ("Захтев за информације од јавног значаја — Учествуј",
            "Како се тражи информација од органа власти: кораци, рокови и чланови закона, и писмо које правите у свом прегледачу.", main)
