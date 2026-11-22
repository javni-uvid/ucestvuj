/* Učestvuj: the first page's filters. The page is whole without this file: the list is there, in order, with
   every day written out. This only hides the rows a reader didn't ask for, says how far the next day is from
   the reader's own today, and keeps the choice in the address so it can be bookmarked or sent. Nothing is
   stored on the device and nothing is sent anywhere. */
(function () {
  "use strict";
  var form = document.getElementById("filter");
  var list = document.getElementById("lista");
  if (!form || !list) return;
  var cards = Array.prototype.slice.call(list.children);
  var words = {};
  Array.prototype.forEach.call(document.querySelectorAll("#reci [data-k]"), function (el) { words[el.getAttribute("data-k")] = el.textContent; });

  function iso(shift) {
    var d = new Date();
    d.setDate(d.getDate() + (shift || 0));
    return d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" + ("0" + d.getDate()).slice(-2);
  }
  function between(a, b) { return Math.round((Date.parse(b + "T12:00:00Z") - Date.parse(a + "T12:00:00Z")) / 864e5); }
  var today = iso(0), week = iso(7), month = iso(-30);

  var CYR = "абвгдђежзијклмнопрстћуфхцчш", LAT = ["a", "b", "v", "g", "d", "dj", "e", "z", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "c", "u", "f", "h", "c", "c", "s"];
  function fold(text) {  // as the rows' own words are folded: Latin, lower case, no marks on the letters
    var out = "";
    text = text.toLowerCase().replace(/љ/g, "lj").replace(/њ/g, "nj").replace(/џ/g, "dz");
    for (var i = 0; i < text.length; i++) { var at = CYR.indexOf(text[i]); out += at < 0 ? text[i] : LAT[at]; }
    return out.replace(/đ/g, "dj").normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  // Each row: the days it names, the nearest still to come and the last, by the reader's today.
  cards.forEach(function (card, at) {
    var days = (card.getAttribute("data-days") || "").split(" ").filter(Boolean);
    var next = days.filter(function (d) { return d >= today; }).sort()[0] || "";
    card.order = at;
    card.next = card.hasAttribute("data-held") ? "" : next;
    var say = card.querySelector(".next");
    if (say && card.next) {
      var n = between(today, card.next);
      say.textContent = words.next + " " + (n === 0 ? words.today : n === 1 ? words.tomorrow : words["in"] + " " + n + " " + (n % 10 === 1 && n % 100 !== 11 ? words.day : words.days));
      say.hidden = false;
    }
  });

  var f = form.elements;
  function apply() {
    var place = f.mesto.value, time = f.kada.value, kind = f.vrsta.value, topic = f.tema ? f.tema.value : "", asked = fold(f.rec.value.trim());
    var shown = cards.filter(function (card) {
      var ok = (!place || card.getAttribute("data-place") === place) &&
        (!kind || card.getAttribute("data-kind") === kind) &&
        (!topic || card.getAttribute("data-topic") === topic) &&
        (!asked || card.getAttribute("data-text").indexOf(asked) >= 0) &&
        (time === "ahead" ? !!card.next : time === "week" ? !!card.next && card.next <= week : card.getAttribute("data-day") >= month);
      card.hidden = !ok;
      return ok;
    });
    shown.sort(function (a, b) {
      if (time === "recent") return a.getAttribute("data-day") < b.getAttribute("data-day") ? 1 : a.getAttribute("data-day") > b.getAttribute("data-day") ? -1 : a.order - b.order;
      return a.next < b.next ? -1 : a.next > b.next ? 1 : a.order - b.order;
    }).forEach(function (card) { list.appendChild(card); });
    document.getElementById("broj").textContent = words.found + " " + shown.length;
    // A chosen place says what is read of it and where all of its announcements are (written into the page).
    document.getElementById("nema").hidden = shown.length > 0;
    Array.prototype.forEach.call(document.querySelectorAll("#mesta > p"), function (note) { note.hidden = note.id !== "m-" + place; });
    var state = [];
    ["mesto", "kada", "vrsta", "tema", "rec"].forEach(function (name) {
      if (f[name] && f[name].value && !(name === "kada" && f[name].value === "ahead")) state.push(name + "=" + encodeURIComponent(f[name].value));
    });
    history.replaceState(null, "", state.length ? "#" + state.join("&") : location.pathname + location.search);
  }

  location.hash.slice(1).split("&").forEach(function (pair) {
    var at = pair.indexOf("="), name = pair.slice(0, at);
    if (at > 0 && f[name]) { f[name].value = decodeURIComponent(pair.slice(at + 1)); if (f[name].tagName === "SELECT" && f[name].selectedIndex < 0) f[name].selectedIndex = 0; }
  });
  // The other choices are folded on a phone, so the list starts on the first screen; open where there is room,
  // and where the address already holds one of them.
  var more = form.querySelector("details");
  more.open = window.matchMedia("(min-width: 720px)").matches || ["kada", "vrsta", "tema", "rec"].some(function (name) { return f[name] && f[name].value && f[name].value !== "ahead"; });
  form.hidden = false;
  form.addEventListener("input", apply);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  form.addEventListener("reset", function () { setTimeout(apply, 0); });
  apply();
})();

/* The letter of the guide to the request for information: the form fills the blanks of a letter that stands in the
   page without it. What is typed is put into the letter in this page and goes nowhere: no request, no storage. The
   blanks are the fields' own placeholders (square brackets), so the letter reads the same in either script. */
(function () {
  "use strict";
  var form = document.getElementById("pismo-forma");
  var letter = document.getElementById("pismo");
  if (!form || !letter) return;
  var template = letter.value;
  var fields = Array.prototype.slice.call(form.querySelectorAll("input, textarea, select"));
  function fill() {
    var text = template;
    fields.forEach(function (field) {
      var token = field.getAttribute("data-token") || field.getAttribute("placeholder");
      var value = field.tagName === "SELECT" ? field.options[field.selectedIndex].text : field.value.trim();
      if (token && value) text = text.split(token).join(value);
    });
    letter.value = text;
  }
  var copy = document.getElementById("pismo-kopija");
  var state = document.getElementById("pismo-stanje");
  if (copy && navigator.clipboard) {
    copy.hidden = false;
    copy.addEventListener("click", function () {
      navigator.clipboard.writeText(letter.value).then(function () { state.textContent = copy.getAttribute("data-done") || "Копирано."; });
    });
  }
  form.hidden = false;
  form.addEventListener("input", fill);
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  fill();
})();
