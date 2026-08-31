from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Iterable


@dataclass(frozen=True)
class Capability:
    id: str
    layer: str
    description: str
    keywords: tuple[str, ...]
    body: None = None
    available: bool = True
    enabled: bool = True
    explicit_only: bool = False
    permitted: bool = True


@dataclass(frozen=True)
class Intent:
    outcome: str
    freshness: bool
    risk: str


@dataclass(frozen=True)
class RouteResult:
    intent: Intent
    capabilities: tuple[Capability, ...]
    requires_human_control: bool
    unmet: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    clarification_required: bool = False

    @property
    def selected(self) -> list[str]:
        return [c.id for c in self.capabilities]


class CapabilityRegistry:
    def __init__(self, capabilities: Iterable[Capability]):
        self.capabilities = tuple(capabilities)
        if any(not isinstance(c, Capability) or not isinstance(c.id, str) or not isinstance(c.layer, str) for c in self.capabilities):
            raise ValueError("Capability identity and layer must be strings")
        ids = [c.id for c in self.capabilities]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate capability id")
        for c in self.capabilities:
            if not isinstance(c.id, str) or not c.id or c.layer not in {"process", "domain", "source", "verifier"}:
                raise ValueError("Invalid capability identity/layer")
            if not isinstance(c.description, str) or not isinstance(c.keywords, tuple) or any(not isinstance(k, str) or not k.strip() for k in c.keywords):
                raise ValueError("Invalid capability metadata")
            if any(type(v) is not bool for v in (c.available, c.enabled, c.explicit_only, c.permitted)):
                raise ValueError("Capability flags must be boolean")

    @classmethod
    def from_json(cls, path: str | Path) -> "CapabilityRegistry":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(raw, list) or any(not isinstance(i, dict) for i in raw):
            raise ValueError("Registry must contain objects")
        allowed = {"id", "layer", "description", "keywords", "available", "enabled", "explicit_only", "permitted"}
        for item in raw:
            if not {"id", "layer", "description"} <= item.keys() or set(item) - allowed or not isinstance(item.get("keywords", []), list):
                raise ValueError("Invalid registry schema")
        return cls(
            Capability(
                id=item["id"],
                layer=item["layer"],
                description=item["description"],
                keywords=tuple(item.get("keywords", ())),
                available=item.get("available", True), enabled=item.get("enabled", True),
                explicit_only=item.get("explicit_only", False), permitted=item.get("permitted", True),
            )
            for item in raw
        )


def _norm(text: str) -> str:
    for mark in "’‘ʻʼ`":
        text = text.replace(mark, "'")
    return re.sub(r"\s+", " ", text.lower()).strip()


def _freshness(text: str) -> bool:
    terms = ("bugun", "bugungi", "hozir", "hozirgi", "latest", "current", "eng yangi", "so'nggi", "ertaga", "haftalik")
    return any(t in text for t in terms)


def _risk(text: str) -> str:
    # Advisory only: a lexical classification never grants execution permission.
    if any(t in text for t in ("faqat tushuntir", "faqat tekshir", "do not", "don't", " nima", "explain", "o'chirma")):
        return "read"
    destructive = ("o'chir", "delete", "drop ", "wipe", "remove all", "barcha user", "production baza", "production baz")
    write = ("yubor", "send", "publish", "deploy", "yarat", "create", "update", "tuzat", "fix")
    if any(t in text for t in destructive):
        return "destructive"
    if any(t in text for t in write):
        return "write"
    return "read"


def _contains(text: str, phrase: str) -> bool:
    if re.fullmatch(r"[a-z0-9_-]+", phrase):
        # Uzbek suffixes attach directly (pdfdan, hujjatni, slaydlar).
        # `repo` is kept token-exact so it does not match `report`.
        if phrase == "repo":
            return re.search(rf"(?<![a-z0-9_-]){re.escape(phrase)}(?![a-z0-9_-])", text) is not None
        if phrase == "bug":
            return re.search(r"(?<![a-z0-9_-])bug(?:ini|ni|lar|ning|s)?(?![a-z0-9_-])", text) is not None
        if phrase == "rasm":
            return re.search(r"(?<![a-z0-9_-])rasm(?:ni|dan|ga|lar|ning)?(?![a-z0-9_-])", text) is not None
        return re.search(rf"(?<![a-z0-9_-]){re.escape(phrase)}", text) is not None
    return phrase in text


def _has_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(_contains(text, phrase) for phrase in phrases)


def _score(cap: Capability, text: str) -> int:
    score = sum(1 for kw in cap.keywords if _contains(text, kw))
    # Source-of-truth boosts prevent vague words from stealing routing.
    if cap.id == "gmail" and _has_any(text, ("gmail", "email", "inbox", "pochta")):
        score += 5
    if cap.id == "calendar" and _has_any(text, ("calendar", "kalendar")):
        score += 5
    if cap.id == "github-repository" and _has_any(text, ("github", "repo", "reposi", "repository", "codebase", "kod baz", "source code")):
        score += 5
    if cap.id == "file-source" and _has_any(text, ("pdf", "excel", "xlsx", "fayl", "file", "workbook")):
        score += 4
    if cap.id == "weather-live" and _has_any(text, ("weather", "ob-havo", "yomg'ir", "forecast", "prognoz")):
        score += 7
    if cap.id == "web-research" and _has_any(text, ("internet", "web", "latest", "current", "bugungi", "yangilik", "research", "tadqiqot", "manbalar", "evidence", "dalillar")):
        score += 3
    return score


def route_request(request: str, registry: CapabilityRegistry, *, explicit_ids: Iterable[str] = ()) -> RouteResult:
    if not isinstance(request, str):
        raise ValueError("Request must be text")
    text = _norm(request)
    intent = Intent(outcome=request.strip(), freshness=_freshness(text), risk=_risk(text))
    explicit = set(explicit_ids)
    if text in {"", "salom", "rahmat", "hello", "thanks"} and not explicit:
        return RouteResult(intent, (), False)
    eligible = {c.id: c for c in registry.capabilities if c.available and c.enabled and c.permitted and (not c.explicit_only or c.id in explicit)}
    by_layer: dict[str, tuple[int, Capability]] = {}
    domains = {}
    for cap in sorted(eligible.values(), key=lambda c: c.id):
        score = _score(cap, text)
        if score <= 0:
            continue
        current = by_layer.get(cap.layer)
        if current is None or score > current[0]:
            by_layer[cap.layer] = (score, cap)
        if cap.layer == "domain":
            domains[cap.id] = cap

    # Domain-specific safeguards for common mixed requests.
    chosen = {c.id: c for _, c in by_layer.values() if c.layer not in {"source", "domain"}}
    chosen.update(domains)
    # Matched domains are requirements even when policy prevents selecting them.
    needs = sorted(c.id for c in registry.capabilities if c.layer == "domain" and _score(c, text) > 0)
    source_needs = []
    for cid, terms in (
        ("gmail", ("gmail", "email", "inbox", "pochta")),
        ("calendar", ("calendar", "kalendar", "meeting", "event", "agenda", "uchrashuv", "bo'sh vaqt")),
        ("weather-live", ("weather", "ob-havo", "yomg'ir", "forecast", "prognoz")),
        ("github-repository", ("github", "repo", "reposi", "repository", "codebase", "kod baz", "source code")),
        ("file-source", ("pdf", "excel", "xlsx", "spreadsheet", "jadval", "fayl", "file", "workbook")),
    ):
        if _has_any(text, terms):
            if cid == "calendar" and _has_any(text, ("event handler", "event loop", "event listener")) and not _has_any(text, ("calendar", "kalendar", "meeting", "uchrashuv")):
                continue
            source_needs.append(cid)
    public_terms = ("research", "tadqiqot", "manbalar", "evidence", "dalillar", "keng qamrovli", "internet", "web", "latest", "current", "bugungi", "yangilik")
    explicit_web = _has_any(text, ("internetdan", "webdan", "web research", "public web"))
    source_hints = ("gmail", "email", "inbox", "pochta", "calendar", "kalendar", "github", "repo", "repository", "file", "fayl", "pdf", "weather", "ob-havo")
    clauses = re.split(r"\b(?:and|with|va|bilan)\b|;", text)
    separate_public = any(
        not _has_any(clause, source_hints) and
        (re.search(r"\bnews\b", clause) is not None or _has_any(clause, ("public", "yangilik", "internet", "web research", "release")))
        for clause in clauses
    )
    if (not source_needs and _has_any(text, public_terms)) or explicit_web or separate_public:
        source_needs.append("web-research")
    if not source_needs and "source" in by_layer:
        source_needs.append(by_layer["source"][1].id)
    needs.extend(source_needs)
    unmet = []
    for cid in dict.fromkeys([*needs, *sorted(explicit)]):
        if cid in eligible:
            chosen[cid] = eligible[cid]
        else:
            unmet.append(cid)
    order = {layer: i for i, layer in enumerate(("process", "domain", "source", "verifier"))}
    caps = tuple(sorted(chosen.values(), key=lambda c: (order[c.layer], c.id)))
    return RouteResult(intent, caps, intent.risk != "read", tuple(unmet),
                       tuple(f"{c.id}: relevant {c.layer} metadata" for c in caps), bool(unmet) or not bool(caps))
