(() => {
  const translations = {
    "Explore all": ["Se alle", "Alle entdecken"],
    "Go karting": ["Kør gokart", "Kart fahren"],
    "Family outing": ["Familietur", "Familienausflug"],
    "Bring my kart": ["Medbring egen kart", "Eigenes Kart mitbringen"],
    "Race-kart rental": ["Lej en racekart", "Rennkart mieten"],
    "Group event": ["Gruppearrangement", "Gruppenveranstaltung"],
    "What would you like to do?": ["Hvad vil du gerne gøre?", "Was möchtest du machen?"],
    "Search and filters": ["Søgning og filtre", "Suche und Filter"],
    "List": ["Liste", "Liste"],
    "Map": ["Kort", "Karte"],
    "Find nearby": ["Find i nærheden", "In der Nähe suchen"],
    "Use my location": ["Brug min placering", "Meinen Standort verwenden"],
    "Clear location / area": ["Ryd placering / område", "Standort / Gebiet löschen"],
    "Reset filters": ["Nulstil filtre", "Filter zurücksetzen"],
    "More filters: countries, track types and karts": ["Flere filtre: lande, banetyper og karts", "Weitere Filter: Länder, Streckentypen und Karts"],
    "Driving": ["Kørsel", "Fahren"],
    "Chassis": ["Chassis", "Chassis"],
    "Engine": ["Motor", "Motor"],
    "Any": ["Alle", "Alle"],
    "Any chassis": ["Alle chassis", "Alle Chassis"],
    "Any engine": ["Alle motorer", "Alle Motoren"],
    "Rental karts": ["Udlejningskarts", "Leihkarts"],
    "Own karts allowed": ["Egne karts tilladt", "Eigene Karts erlaubt"],
    "Own karts": ["Egne karts", "Eigene Karts"],
    "Race karts for rent": ["Racekarts til leje", "Rennkarts zur Miete"],
    "Sort": ["Sortér", "Sortieren"],
    "Country": ["Land", "Land"],
    "Longest": ["Længste", "Längste"],
    "Cheapest €/min": ["Billigste €/min", "Günstigste €/min"],
    "Cheapest €/lap": ["Billigste €/omgang", "Günstigste €/Runde"],
    "Nearest": ["Nærmeste", "Nächste"],
    "Copy search link": ["Kopiér søgelink", "Suchlink kopieren"],
    "Save venue": ["Gem banen", "Strecke speichern"],
    "Unsave venue": ["Fjern gemt bane", "Gespeicherte Strecke entfernen"],
    "Add to comparison": ["Føj til sammenligning", "Zum Vergleich hinzufügen"],
    "Remove from comparison": ["Fjern fra sammenligning", "Aus Vergleich entfernen"],
    "Copy venue link": ["Kopiér banelink", "Streckenlink kopieren"],
    "Venue page": ["Baneside", "Streckenseite"],
    "Shared shortlist": ["Delt liste", "Geteilte Merkliste"],
    "Saved venues": ["Gemte baner", "Gespeicherte Strecken"],
    "Compare venues": ["Sammenlign baner", "Strecken vergleichen"],
    "Copy shortlist link": ["Kopiér listelink", "Merklistenlink kopieren"],
    "Copy comparison link": ["Kopiér sammenligningslink", "Vergleichslink kopieren"],
    "Clear comparison": ["Ryd sammenligning", "Vergleich leeren"],
    "Save all to this browser": ["Gem alle i denne browser", "Alle in diesem Browser speichern"],
    "Open details": ["Åbn detaljer", "Details öffnen"],
    "Close": ["Luk", "Schließen"],
    "✕ Close": ["✕ Luk", "✕ Schließen"],
    "Overview": ["Overblik", "Übersicht"],
    "Track": ["Bane", "Strecke"],
    "Karts": ["Karts", "Karts"],
    "Prices": ["Priser", "Preise"],
    "Town": ["By", "Ort"],
    "Region": ["Region", "Region"],
    "Address": ["Adresse", "Adresse"],
    "Phone": ["Telefon", "Telefon"],
    "Email": ["E-mail", "E-Mail"],
    "Hours": ["Åbningstider", "Öffnungszeiten"],
    "From": ["Fra", "Ab"],
    "Website": ["Hjemmeside", "Webseite"],
    "Venue": ["Bane", "Strecke"],
    "Club": ["Klub", "Verein"],
    "Rental": ["Udlejning", "Vermietung"],
    "Price source": ["Priskilde", "Preisquelle"],
    "Family/group source": ["Familie-/gruppekilde", "Familien-/Gruppenquelle"],
    "venue website": ["banens hjemmeside", "Betreiberwebseite"],
    "Layout": ["Banelayout", "Streckenlayout"],
    "Length": ["Længde", "Länge"],
    "Width": ["Bredde", "Breite"],
    "Use": ["Brug", "Nutzung"],
    "Track layouts": ["Banelayouts", "Streckenlayouts"],
    "Rental fleet": ["Udlejningsflåde", "Leihkart-Flotte"],
    "Kart": ["Kart", "Kart"],
    "Class": ["Klasse", "Klasse"],
    "What you get": ["Hvad du får", "Leistungsumfang"],
    "Price": ["Pris", "Preis"],
    "Age / height": ["Alder / højde", "Alter / Größe"],
    "mandatory": ["obligatorisk", "verpflichtend"],
    "optional": ["valgfri", "optional"],
    "members": ["medlemmer", "Mitglieder"],
    "not compared": ["ikke sammenlignet", "nicht verglichen"],
    "Extra fees on top of the driving price": ["Ekstra gebyrer ud over kørselsprisen", "Zusatzgebühren zum Fahrpreis"],
    "Club membership": ["Klubmedlemskab", "Vereinsmitgliedschaft"],
    "for member prices": ["for medlemspriser", "für Mitgliederpreise"],
    "Include member prices": ["Medtag medlemspriser", "Mitgliederpreise einschließen"],
    "Only with layout": ["Kun med banelayout", "Nur mit Streckenlayout"],
    "Show closed": ["Vis lukkede", "Geschlossene anzeigen"],
    "Reported closed": ["Rapporteret lukket", "Als geschlossen gemeldet"],
    "Outdoor circuit": ["Udendørsbane", "Außenstrecke"],
    "Indoor / hall": ["Indendørs / hal", "Indoor / Halle"],
    "Kids & other": ["Børn og andet", "Kinder und Sonstiges"],
    "shown": ["vist", "angezeigt"],
    "outdoor": ["udendørs", "außen"],
    "indoor": ["indendørs", "innen"],
    "Search this area": ["Søg i dette område", "In diesem Gebiet suchen"],
    "Session behind the lowest €/min:": ["Sessionen bag laveste €/min:", "Session hinter dem niedrigsten €/min:"],
    "Session behind that €/min": ["Sessionen bag denne €/min", "Session hinter diesem €/min"],
    "Family and group visits": ["Familie- og gruppebesøg", "Familien- und Gruppenbesuche"],
    "Rental availability": ["Udlejning tilgængelig", "Leihkart-Verfügbarkeit"],
    "Lowest standard session": ["Billigste standardsession", "Günstigste Standardsession"],
    "Lowest standard €/min": ["Laveste standard-€/min", "Niedrigster Standard-€/min"],
    "Fees and membership": ["Gebyrer og medlemskab", "Gebühren und Mitgliedschaft"],
    "Performance / race sessions": ["Performance- / racesessioner", "Performance- / Rennsessions"],
    "Family options": ["Familiemuligheder", "Familienangebote"],
    "Track length": ["Banelængde", "Streckenlänge"],
    "Price freshness": ["Prisernes aktualitet", "Aktualität der Preise"],
    "Sources": ["Kilder", "Quellen"],
    "Not verified": ["Ikke verificeret", "Nicht bestätigt"],
    "Family options not verified.": ["Familiemuligheder ikke verificeret.", "Familienangebote nicht bestätigt."],
    "Confirmed rental": ["Verificeret udlejning", "Leihkarts bestätigt"],
    "Reported no rental": ["Rapporteret uden udlejning", "Keine Vermietung gemeldet"],
    "No eligible standard adult session verified": ["Ingen egnet voksen-standardsession verificeret", "Keine geeignete Standard-Erwachsenensession bestätigt"],
    "No verified race-kart session price": ["Ingen verificeret racekartpris", "Kein bestätigter Rennkart-Sessionpreis"],
    "No fee information verified": ["Ingen gebyroplysninger verificeret", "Keine Gebühreninformationen bestätigt"],
    "Not a guaranteed complete first-visit total.": ["Ikke en garanteret samlet pris for første besøg.", "Kein garantiert vollständiger Gesamtpreis für den ersten Besuch."],
    "No tracks match these filters. Use Reset filters to start over.": ["Ingen baner matcher filtrene. Brug Nulstil filtre til at starte forfra.", "Keine Strecken passen zu diesen Filtern. Mit Filter zurücksetzen neu beginnen."],
    "No venues selected yet. Open a venue and choose Save venue or Add to comparison.": ["Ingen baner valgt. Åbn en bane og vælg Gem banen eller Føj til sammenligning.", "Noch keine Strecken ausgewählt. Eine Strecke öffnen und speichern oder zum Vergleich hinzufügen."],
    "Add a second venue to compare side by side.": ["Tilføj en anden bane for at sammenligne.", "Eine zweite Strecke für den Vergleich hinzufügen."],
    "Choose two to four venues. Remove or add venues through their details or your saved list.": ["Vælg to til fire baner. Tilføj eller fjern via banedetaljer eller din gemte liste.", "Zwei bis vier Strecken wählen. Über Details oder Merkliste hinzufügen oder entfernen."],
    "Compare up to four venues. Remove one from the comparison before adding another.": ["Sammenlign op til fire baner. Fjern en før du tilføjer en ny.", "Bis zu vier Strecken vergleichen. Vor einer weiteren Auswahl eine Strecke entfernen."],
    "Choose a town from the suggestions. Only towns already in the atlas are searchable.": ["Vælg en by fra forslagene. Kun byer i atlasset kan søges.", "Einen Ort aus den Vorschlägen auswählen. Nur Orte im Atlas sind durchsuchbar."],
    "Saved venues are stored only in this browser, without an account.": ["Gemte baner lagres kun i denne browser, uden konto.", "Gespeicherte Strecken bleiben nur in diesem Browser, ohne Konto."],
    "Saved venues stay in this browser. Sharing sends only venue IDs; no device location is included.": ["Gemte baner forbliver i browseren. Deling sender kun bane-ID'er, ikke enhedens placering.", "Gespeicherte Strecken bleiben im Browser. Geteilt werden nur Strecken-IDs, kein Gerätestandort."],
    "Link copied. Device location is excluded.": ["Link kopieret. Enhedens placering er udeladt.", "Link kopiert. Der Gerätestandort ist ausgeschlossen."],
    "Venue link copied.": ["Banelink kopieret.", "Streckenlink kopiert."],
    "Link copied. It contains venue IDs only, plus the membership option for comparisons.": ["Link kopieret. Kun bane-ID'er og medlemsvalg for sammenligninger er med.", "Link kopiert. Enthält nur Strecken-IDs und die Mitgliederoption bei Vergleichen."],
    "Shortlist saved to this browser.": ["Liste gemt i denne browser.", "Merkliste in diesem Browser gespeichert."],
    "Town centres are estimated from mapped venues. Device location is never put in share links.": ["Bymidter anslås fra kortlagte baner. Enhedens placering deles aldrig i links.", "Ortszentren werden aus kartierten Strecken geschätzt. Der Gerätestandort erscheint nie in geteilten Links."],
    "Town centres are estimated from mapped venues. Your device location is never put in share links.": ["Bymidter anslås fra kortlagte baner. Enhedens placering deles aldrig i links.", "Ortszentren werden aus kartierten Strecken geschätzt. Der Gerätestandort erscheint nie in geteilten Links."],
    "Session cost and lowest €/min may refer to different sessions. Fees shown are known fees, not a guaranteed complete first-visit total.": ["Sessionsprisen og laveste €/min kan gælde forskellige sessioner. Kendte gebyrer er ikke en garanteret samlet pris for første besøg.", "Sessionpreis und niedrigster €/min können verschiedene Sessions betreffen. Bekannte Gebühren ergeben keinen garantiert vollständigen Erstbesuchspreis."],
    "Data and attribution · © OpenStreetMap": ["Data og kildeangivelse · © OpenStreetMap", "Daten und Quellenangabe · © OpenStreetMap"],
    "Language": ["Sprog", "Sprache"],
    "Interface language": ["Grænsefladesprog", "Sprache der Oberfläche"],
    "Venue names, tariff wording and research notes retain their source language.": ["Banenavne, tariftekster og researchnoter beholder deres kildesprog.", "Streckennamen, Tariftexte und Recherchehinweise bleiben in ihrer Quellsprache."],
    "Find around an atlas town": ["Find omkring en by i atlasset", "In der Nähe eines Atlas-Orts suchen"],
    "Search name, town, region or kart…": ["Søg navn, by, region eller kart…", "Name, Ort, Region oder Kart suchen…"],
    "Search tracks": ["Søg baner", "Strecken suchen"],
    "Atlas town": ["By i atlasset", "Ort im Atlas"],
    "Search radius": ["Søgeradius", "Suchradius"],
    "Close track details": ["Luk banedetaljer", "Streckendetails schließen"],
    "Venue information": ["Baneinformation", "Streckeninformationen"],
    "Display mode": ["Visning", "Ansicht"],
    "Trip planning": ["Turplanlægning", "Ausflugsplanung"],
    "Zoom in": ["Zoom ind", "Vergrößern"],
    "Zoom out": ["Zoom ud", "Verkleinern"],
    "Reset view": ["Nulstil visning", "Ansicht zurücksetzen"],
    "Map of go-kart tracks": ["Kort over gokartbaner", "Karte der Kartstrecken"]
  };
  const params = new URLSearchParams(location.hash.slice(1));
  let saved = "en";
  try { saved = localStorage.getItem("kartatlas.language") || "en"; }
  catch (error) { document.getElementById("share-status").textContent = `Could not read language preference: ${error.message}. Using link/default language.`; }
  let language = params.get("lang") || saved;
  if (!["en", "da", "de"].includes(language)) language = "en";
  if (language !== "en" && !params.has("lang")) {
    params.set("lang", language);
    history.replaceState(null, "", "#" + params.toString());
  }
  const original = new WeakMap();
  function translate(text) {
    if (language === "en") return text;
    const index = language === "da" ? 0 : 1, trimmed = text.trim();
    if (translations[trimmed]) return text.replace(trimmed, translations[trimmed][index]);
    const patterns = [
      [/^Saved venues \((\d+)\)$/, index ? "Gespeicherte Strecken ($1)" : "Gemte baner ($1)"],
      [/^Compare \((\d+)\/4\)$/, index ? "Vergleich ($1/4)" : "Sammenlign ($1/4)"],
      [/^Compare selected \((\d+)\/4\)$/, index ? "Auswahl vergleichen ($1/4)" : "Sammenlign valgte ($1/4)"],
      [/^(\d+) of 4 comparison places selected\. Use Compare to view them side by side\.$/, index ? "$1 von 4 Vergleichsplätzen ausgewählt. Zum Vergleichen Vergleich öffnen." : "$1 af 4 sammenligningspladser valgt. Åbn Sammenlign for at se dem."],
      [/^Published prices checked on ([\d-]+)\. Confirm current prices with the venue before travelling\.$/, index ? "Veröffentlichte Preise am $1 geprüft. Aktuelle Preise vor der Anreise beim Betreiber bestätigen." : "Offentliggjorte priser kontrolleret $1. Bekræft aktuelle priser med banen før afrejse."],
      [/^Published prices found; the source-check date was not recorded\. Confirm current prices with the venue\.$/, index ? "Veröffentlichte Preise gefunden; Prüfdatum nicht erfasst. Aktuelle Preise beim Betreiber bestätigen." : "Offentliggjorte priser fundet; kontroldato ikke registreret. Bekræft priser med banen."],
      [/^No verified published prices in the atlas\. This does not mean rental is unavailable\.(.*)$/, index ? "Keine bestätigten veröffentlichten Preise im Atlas. Das bedeutet nicht, dass keine Vermietung möglich ist.$1" : "Ingen verificerede offentliggjorte priser i atlasset. Det betyder ikke, at udlejning er utilgængelig.$1"],
      [/^From €([\d.]+) for ([\d.]+) min/, index ? "Ab €$1 für $2 Min." : "Fra €$1 for $2 min"]
    ];
    for (const [pattern, replacement] of patterns) if (pattern.test(trimmed)) return text.replace(trimmed, trimmed.replace(pattern, replacement));
    return text;
  }
  function apply() {
    observer.disconnect();
    document.documentElement.lang = language;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) {
      if (node.parentElement.closest("script, style, #detail-title, .item .nm, .saved-item h3, #tip, .clabel, #places, .language-note, .facts dd, .fleet tbody, .fees li b, .fees li .note, [data-source-text]")) continue;
      const previous = original.get(node);
      const source = previous && node.nodeValue === previous.translated ? previous.source : node.nodeValue;
      const translated = translate(source);
      original.set(node, { source, translated });
      if (node.nodeValue !== translated) node.nodeValue = translated;
    }
    document.querySelectorAll("[aria-label], [placeholder]").forEach(el => {
      for (const attr of ["aria-label", "placeholder"]) {
        if (!el.hasAttribute(attr)) continue;
        const key = "data-original-" + attr;
        if (!el.hasAttribute(key)) el.setAttribute(key, el.getAttribute(attr));
        el.setAttribute(attr, translate(el.getAttribute(key)));
      }
    });
    document.getElementById("language").value = language;
    document.getElementById("language-note").textContent = translate("Venue names, tariff wording and research notes retain their source language.");
    observer.observe(document.body, { childList: true, characterData: true, subtree: true });
  }
  const observer = new MutationObserver(apply);
  window.kartLanguage = () => language;
  document.getElementById("language").onchange = e => {
    language = e.target.value;
    try { localStorage.setItem("kartatlas.language", language); }
    catch (error) { document.getElementById("share-status").textContent = `Could not persist language preference: ${error.message}. Language remains in this link.`; }
    const params = new URLSearchParams(location.hash.slice(1));
    if (language === "en") params.delete("lang"); else params.set("lang", language);
    history.replaceState(null, "", "#" + params.toString());
    apply();
  };
  window.addEventListener("hashchange", () => {
    const next = new URLSearchParams(location.hash.slice(1)).get("lang") || "en";
    if (["en", "da", "de"].includes(next)) language = next;
    apply();
  });
  apply();
})();
