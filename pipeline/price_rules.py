import re

PROMO = re.compile(
    r"ladies|night|half.?price|happy|spar|student|promo|early.?bird|special|"
    r"aktion|réduit|reduced|discount|rabatt|off.?peak|block|abo|subscription|"
    r"monday|tuesday|wednesday|thursday|friday|montag|dienstag|mittwoch|"
    r"donnerstag|freitag|lundi|mardi|mercredi|jeudi|vendredi|"
    r"mandag|tirsdag|onsdag|torsdag|fredag|"
    r"from \d+ (rides|sessions|runs)|ab \d+ |\d+er.?(karte|block)|"
    r"\d+\s*(tickets|sessions|rides|heats)|\b(mon|tue|wed|thu|fri|mo|di|mi|do|fr|lun|mar|mer|jeu|ven)\b\s*[-–]"
, re.I)
PERFORMANCE = re.compile(r"\b(2\s*t|2\s*temps|2.?stroke|race\s*kart|rotax|125\s*cc)\b", re.I)
CHILD = re.compile(r"baby|kid|kinder|enfant|junior|jugend|bambin|mini|child|barn|børn", re.I)


def comparison_eligible(offer: dict) -> bool:
    """Compare plain adult rental sessions, never performance or group offers."""
    label = str(offer.get("label") or "")
    if (
        offer.get("class") not in (None, "adult", "other", "electric")
        or offer.get("extras")
        or offer.get("type", "session") not in ("session", "per_minute", "laps")
        or CHILD.search(label)
        or PERFORMANCE.search(label)
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
