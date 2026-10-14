import re

PROMO = re.compile(
    r"ladies|night|half.?price|happy|spar|student|promo|early.?bird|special|"
    r"aktion|réduit|reduced|discount|rabatt|off.?peak|block|abo|subscription|"
    r"following session|additional session|next session|session suivante|partie suivante|second session|2nd session|folgefahrt|weitere fahrt|kolejny przejazd|następny przejazd|další jízda|každá další|"
    r"monday|tuesday|wednesday|thursday|friday|montag|dienstag|mittwoch|"
    r"donnerstag|freitag|lundi|mardi|mercredi|jeudi|vendredi|"
    r"mandag|tirsdag|onsdag|torsdag|fredag|"
    r"from \d+ (rides|sessions|runs)|ab \d+ |\d+er.?(karte|block)|"
    r"\d+\s*(tickets|sessions|rides|heats)|\b(mon|tue|wed|thu|fri|mo|di|mi|do|fr|lun|mar|mer|jeu|ven)\b\s*[-–]"
, re.I)
PERFORMANCE = re.compile(r"\b(2\s*t|2\s*temps|2.?stroke|race\s*kart|rennkart|rotax|125\s*cc)\b", re.I)
CHILD = re.compile(r"baby|kid|kinder|enfant|junior|jugend|bambin|mini|child|barn|børn|dzieci|dziec|dětsk|dětí", re.I)
# track time with the driver's own kart or exclusive track hire: not a rental-kart price
OWN_KART = re.compile(r"own (kart|equipment|vehicle)|track (hire|rental)|private kart|eigene[nmrs]? kart|bahnmiete|"
                      r"location (de )?(la )?piste|noleggio (della )?pista|kart (di )?propriet|własn|vlastní|banleje|banhyra", re.I)


KNOWN_CLASSES = (None, "adult", "kids", "twin", "race", "other", "electric")
KNOWN_TYPES = ("session", "per_minute", "laps", "package")
C_TWIN = re.compile(r"tandem|two.?seat|twin|duo|biposto|doppel|dvoum|dvojm|2.?seat|2drive", re.I)
C_RACE = re.compile(r"race|rennkart|rotax|\b125\b|\bkz\b|36 ?hp|390", re.I)
C_ADULT = re.compile(r"senior|adult|single|pojedyncz|dosp[eě]l|erwachs|standard|\d+\s*(hp|km|cv|ps|ccm|cc)\b|sodi|rimo|\bsr\d|\brt\d|\bgt\d|270|200", re.I)
T_SESSION = re.compile(r"rental|ride|single|jazda|j[ií]zda|przejazd|session|run", re.I)
WEEKDAYS = r"mon|tue|wed|thu|fri|sat|sun|mo|di|mi|do|fr|sa|so|lun|mar|mer|jeu|ven|sam|dim|pon|wt|śr|czw|pt|sob|niedz|nd|po|út|st|čt|pá|ne"
DAY_RANGE = re.compile(rf"\(?\b({WEEKDAYS})\.?\s*[-–]\s*({WEEKDAYS})\b\.?\)?", re.I)
WEEKEND = re.compile(r"\b(sat|sun|sa|so|sam|dim|sob|niedz|nd|ne|weekend|holiday)", re.I)


def normalize_offer(offer: dict) -> dict:
    """Map free-text research classes/types/day ranges onto the categories the comparison understands."""
    q = dict(offer)
    cls = q.get("class")
    if cls not in KNOWN_CLASSES:
        s = str(cls)
        q["class"] = ("twin" if C_TWIN.search(s) else "kids" if CHILD.search(s) or re.search(r"child|kid", s, re.I)
                      else "race" if C_RACE.search(s) else "adult" if C_ADULT.search(s) else "other")
    typ = q.get("type")
    if typ not in KNOWN_TYPES and typ is not None:
        q["type"] = "session" if T_SESSION.search(str(typ)) else "package"
    # day given as free text ("Mon-Tue", "Fri-Sun and holidays") -> weekday/weekend
    day = q.get("day")
    if day not in (None, "weekday", "weekend", "peak") and (DAY_RANGE.search(str(day)) or WEEKEND.search(str(day)) or re.search(WEEKDAYS, str(day), re.I)):
        q["day"] = "weekend" if WEEKEND.search(str(day)) else "weekday"
    label = str(q.get("label") or "")
    m = DAY_RANGE.search(label)
    if m:
        if not q.get("day"):
            q["day"] = "weekend" if WEEKEND.search(m.group(0)) else "weekday"
        q["label"] = (label[:m.start()] + label[m.end():]).strip(" ,()") or label
    if q.get("note"):  # "valid Mon-Fri" in a note describes when the price applies, not a special offer
        q["note"] = DAY_RANGE.sub("", str(q["note"]))
    return q


def comparison_eligible(offer: dict) -> bool:
    """Compare plain adult rental sessions, never performance or group offers."""
    label = str(offer.get("label") or "")
    if (
        offer.get("class") not in (None, "adult", "other", "electric")
        or offer.get("extras")
        or offer.get("type", "session") not in ("session", "per_minute", "laps")
        or CHILD.search(label)
        or PERFORMANCE.search(label)
        or OWN_KART.search(label)
        or (offer.get("minutes") or 0) > 60  # multi-hour blocks/flat rates are time windows, not one driving session
    ):
        return False
    explicit = offer.get("comparison_eligible")
    if explicit is not None:
        if not isinstance(explicit, bool):
            raise ValueError("comparison_eligible must be boolean")
        return explicit
    if offer.get("day") not in (None, "weekend", "peak", "weekday") or PROMO.search(label):
        return False
    # Notes may describe separately priced discounts/blocks beside the standard rate.
    for clause in re.split(r";|\n", str(offer.get("note") or "")):
        if PROMO.search(clause) and not re.search(r"\d+(?:[.,]\d+)?\s*(EUR|DKK|SEK|CHF|€)\b", clause, re.I):
            return False
    return True
