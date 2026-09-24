#!/usr/bin/env python3
"""Valida o pacote SDD em .spec/ e a rastreabilidade com as fontes.

Contrato: .github/instructions/sdd-artifacts.instructions.md.
Somente leitura. Validacao textual nao prova semantica EARS, aprovacao
humana, renderizacao de diagramas nem resultado de testes.

Saida: 0 sem erros; 1 com erros (ou avisos com --strict); 2 quando
nenhum pacote e encontrado (recusa aprovacao vazia).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_DIR = ".spec"
FORBIDDEN_DIRS = ("specs", ".specs")
PACKAGE = re.compile(r"^\d{3}-[a-z0-9-]+$")
SOURCE_ID_DEFAULT = r"\b(?:RF|RNF|RN)-\d+\b"

SECTIONS: dict[str, tuple[tuple[str, ...], ...]] = {
    "spec.md": (
        ("problema e resultado",),
        ("escopo e não objetivos",),
        ("atores e dependências",),
        ("registro de fontes",),
        ("requisitos",),
        ("matriz de rastreabilidade",),
        ("premissas, bloqueios e perguntas em aberto",),
        ("disposições históricas", "disposição dos ids da fonte"),
        ("validação",),
        ("histórico de mudanças",),
    ),
    "frd.md": (
        ("controle do documento",),
        ("problema e resultados",),
        ("escopo",),
        ("atores e permissões",),
        ("modelo de domínio e ciclo de vida",),
        ("requisitos funcionais por domínio",),
        ("interações externas",),
        ("resumo dos requisitos",),
        ("disposição de ids históricos",),
        ("incrementos de entrega",),
        ("perguntas em aberto",),
        ("registro de revisão",),
    ),
    "nfrd.md": (
        ("controle do documento",),
        ("aplicabilidade",),
        ("contextos de implantação e medição",),
        ("requisitos de qualidade",),
        ("decisões de segurança e conformidade",),
        ("restrições tecnológicas",),
        ("resumo dos requisitos",),
        ("bloqueios e perguntas em aberto",),
        ("registro de revisão",),
    ),
    "plan.md": (
        ("metadados da funcionalidade",),
        ("análise",),
        ("visão geral da arquitetura",),
        ("contexto do sistema",),
        ("mapa de componentes",),
        ("visão de implantação",),
        ("modelo de estados",),
        ("sequências críticas",),
        ("fluxo e ciclo de vida dos dados",),
        ("modelo de dados",),
        ("interfaces e contratos",),
        ("modelo de erros",),
        ("invariantes arquiteturais",),
        ("design de segurança",),
        ("modelo de ameaças",),
        ("estratégia de testes",),
        ("design de observabilidade",),
        ("superfície de implementação",),
        ("visão de entrega e rastreabilidade",),
        ("decisões",),
        ("riscos e trade-offs",),
        ("desenvolvimento em fases",),
        ("histórico de mudanças",),
    ),
    "tasks.md": (
        ("metadados da funcionalidade",),
        ("gate pré-implementação",),
        ("regras de execução",),
        ("grafo de dependências",),
        ("mapa de testes",),
        ("verificação",),
        ("desvios",),
        ("checklist",),
        ("análise cruzada",),
        ("gate de conclusão",),
        ("registro de execução",),
        ("histórico de mudanças",),
    ),
}
REQUIRED_FILES = ("spec.md", "frd.md", "nfrd.md")
STAGE_FILES = ("plan.md", "tasks.md")
SPEC_STATUS = (
    "rascunho", "pronto para revisão", "aprovado", "implementado",
    "verificado",
)
EARS_PATTERNS = (
    "ubiquo", "orientado a evento", "evento", "orientado a estado",
    "estado", "opcional", "indesejado", "complexo",
)

H2 = re.compile(r"^##\s+(.+?)\s*$", re.M)
FENCE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
REQ_HEAD = re.compile(r"^###\s+((?:REQ|NFR)-\d{3})\s*:", re.M)
NEXT_HEAD = re.compile(r"^#{2,3}\s", re.M)
REQ_ID = re.compile(r"\b(?:REQ|NFR)-\d{3}\b")
SRC_ID = re.compile(r"\bSRC-\d{3}\b")
SRC_ROW = re.compile(r"^\|\s*(SRC-\d{3})\s*\|", re.M)
ORIGEM = re.compile(r"^origem:\s*(.*)$", re.M)
EARS_LINE = re.compile(r"^>\s.*\bdeve\b", re.M)
ANCHOR = re.compile(
    r"(?P<path>[A-Za-z0-9_.][\w./-]*\.[A-Za-z0-9]+)?"
    r"#L(?P<a>\d+)(?:-L(?P<b>\d+))?"
)
PATH_TOKEN = re.compile(r"([A-Za-z0-9_.][\w./-]*\.md)\b")
TASK = re.compile(
    r"^- \[(?P<mark>[ xX])\] \*\*(?P<id>T\d{3})(?P<meta>[^*]*)\*\*"
    r"(?P<body>.*?)(?=^- \[[ xX]\] \*\*T\d{3}|^#{1,3} |\Z)",
    re.M | re.S,
)
TASK_ID = re.compile(r"\bT\d{3}\b")
DEPENDS = re.compile(r"Depende de:\s*([^\n]+)")
LEDGER = re.compile(
    r"Marcadas como concluídas pela verificação:\s*([^\n]*)")
COUNT = re.compile(r"Tarefas concluídas:\s*\*\*(\d+) de (\d+)\*\*")
MERMAID = re.compile(r"^```mermaid\n(.*?)^```", re.M | re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
THEME = (
    '%%{init: {"theme":"base","themeVariables":{"background":"#FFFFFF",'
    '"primaryColor":"#FFFFFF","primaryTextColor":"#222222",'
    '"primaryBorderColor":"#777777","lineColor":"#555555",'
    '"secondaryColor":"#F2F2F2","tertiaryColor":"#E8E8E8"}}}%%'
)
PALETTE = (
    "classDef default fill:#FFFFFF,stroke:#777777,color:#222222",
    "classDef zone fill:#F2F2F2,stroke:#999999,color:#222222",
    "classDef external fill:#E8E8E8,stroke:#555555,color:#222222",
)
GRAPHLIKE = ("flowchart", "graph", "classDiagram")


@dataclass
class Finding:
    level: str
    code: str
    path: str
    message: str


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.items: list[Finding] = []

    def add(self, level: str, code: str, path: Path, msg: str) -> None:
        try:
            shown = path.relative_to(self.root).as_posix()
        except ValueError:
            shown = path.as_posix()
        self.items.append(Finding(level, code, shown, msg))

    def error(self, code: str, path: Path, msg: str) -> None:
        self.add("ERRO", code, path, msg)

    def warn(self, code: str, path: Path, msg: str) -> None:
        self.add("AVISO", code, path, msg)


def normalize(heading: str) -> str:
    text = unicodedata.normalize("NFC", heading).replace("`", "")
    text = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text)
    text = re.sub(r"\s*\(.*\)\s*$", "", text)
    return text.strip().casefold()


def fold(text: str) -> str:
    raw = unicodedata.normalize("NFD", text.casefold())
    return "".join(c for c in raw if not unicodedata.combining(c))


def without_fences(text: str) -> str:
    return FENCE.sub("", text)


def mask_fences(text: str) -> str:
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def sections(text: str) -> dict[str, str]:
    heads = list(H2.finditer(mask_fences(text)))
    found: dict[str, str] = {}
    for index, match in enumerate(heads):
        end = heads[index + 1].start() if index + 1 < len(heads) \
            else len(text)
        found[normalize(match.group(1))] = text[match.end():end]
    return found


def check_sections(rep: Report, path: Path, text: str) -> None:
    found = sections(text)
    for names in SECTIONS[path.name]:
        body = next((found[n] for n in names if n in found), None)
        label = " ou ".join(f"`## {n}`" for n in names)
        if body is None:
            rep.error("SEC-001", path, f"seção ausente: {label}")
        elif not body.strip():
            rep.error("SEC-002", path,
                      f"seção vazia: {label}; use NÃO APLICÁVEL: <motivo>")
        elif re.fullmatch(r"\s*N[ÃA]O APLIC[ÁA]VEL\.?\s*", body):
            rep.error("SEC-003", path,
                      f"{label}: NÃO APLICÁVEL sem motivo")
    if path.name == "tasks.md" and not any(
            k.startswith("fase") for k in found):
        rep.error("SEC-001", path, "nenhuma seção `## Fase N`")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def resolve(root: Path, base: Path, token: str) -> Path | None:
    for candidate in (root / token, base / token):
        if candidate.is_file():
            return candidate
    return None


def check_anchors(rep: Report, root: Path, path: Path, text: str,
                  primary: Path | None) -> None:
    lengths: dict[Path, int] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        current = primary
        for match in ANCHOR.finditer(line):
            token = match.group("path")
            if token:
                current = resolve(root, path.parent, token)
                if current is None:
                    rep.error("ANC-001", path,
                              f"L{number}: arquivo citado não existe: "
                              f"{token}")
                    continue
            if current is None:
                rep.warn("ANC-002", path,
                         f"L{number}: âncora #L{match.group('a')} sem "
                         "documento de origem identificável")
                continue
            start = int(match.group("a"))
            end = int(match.group("b") or start)
            size = lengths.setdefault(current, line_count(current))
            shown = current.relative_to(root).as_posix() \
                if current.is_relative_to(root) else current.name
            if start < 1 or end < start:
                rep.error("ANC-003", path,
                          f"L{number}: intervalo inválido {shown}"
                          f"#L{start}-L{end}")
            elif end > size:
                rep.error("ANC-004", path,
                          f"L{number}: {shown}#L{end} além do fim do "
                          f"arquivo ({size} linhas)")


def requirement_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for match in REQ_HEAD.finditer(text):
        rest = text[match.end():]
        nxt = NEXT_HEAD.search(rest)
        body = rest[:nxt.start()] if nxt else rest
        blocks.setdefault(match.group(1), body)
    return blocks


def source_documents(root: Path, spec: Path, text: str) -> list[Path]:
    docs: list[Path] = []
    for value in ORIGEM.findall(text):
        for token in PATH_TOKEN.findall(value):
            if token.startswith(".github/"):
                continue
            found = resolve(root, spec.parent, token)
            if found and found not in docs:
                docs.append(found)
    return docs


def field_value(block: str, name: str) -> str | None:
    match = re.search(rf"^- {name}:\s*(.+)$", block, re.M)
    return match.group(1).strip() if match else None


def check_requirement(rep: Report, spec: Path, rid: str, block: str,
                      sources: set[str]) -> None:
    head = "\n".join(block.splitlines()[:21])
    origem = ORIGEM.search(head)
    if origem is None:
        rep.error("REQ-001", spec,
                  f"{rid}: sem linha `origem:` até 20 linhas após o título")
    else:
        value = origem.group(1)
        cited = set(SRC_ID.findall(value))
        greenfield = re.search(r"\[GREENFIELD\]\s*\S", value)
        if not cited and not PATH_TOKEN.search(value) and not greenfield:
            rep.error("REQ-002", spec,
                      f"{rid}: `origem:` sem SRC-###, caminho ou "
                      "[GREENFIELD] justificado")
        for src in sorted(cited - sources):
            rep.error("SRC-001", spec,
                      f"{rid}: {src} não está no registro de fontes")
    pattern = field_value(block, "Padrão")
    if pattern is None:
        rep.error("REQ-003", spec, f"{rid}: sem `- Padrão:`")
    elif not any(fold(pattern).startswith(p) for p in EARS_PATTERNS):
        rep.error("REQ-003", spec,
                  f"{rid}: padrão EARS desconhecido: {pattern}")
    priority = field_value(block, "Prioridade")
    if priority is None or not re.match(r"P[0-3]\b", priority):
        rep.error("REQ-004", spec, f"{rid}: prioridade P0-P3 ausente")
    if field_value(block, "Status") is None:
        rep.error("REQ-005", spec, f"{rid}: sem `- Status:`")
    statements = EARS_LINE.findall(block)
    if not statements:
        rep.error("REQ-006", spec,
                  f"{rid}: sem declaração EARS (`> ... deve ...`)")
    elif len(statements) > 1:
        rep.warn("REQ-006", spec,
                 f"{rid}: mais de uma declaração EARS no bloco")
    if not re.search(rf"\bAC-{rid}-\d{{2}}\b", block):
        if "BLOQUEADO" in block:
            rep.warn("REQ-007", spec,
                     f"{rid}: aceite BLOQUEADO; não entra no handoff")
        else:
            rep.error("REQ-007", spec, f"{rid}: sem AC-{rid}-NN")
    if "**Verificação**" not in block:
        rep.error("REQ-008", spec, f"{rid}: sem bloco **Verificação**")
    if rid.startswith("NFR-") and "nfrd.md" not in block:
        rep.warn("REQ-009", spec,
                 f"{rid}: não aponta o envelope de medição em nfrd.md")


def check_spec(rep: Report, root: Path, spec: Path,
               source_pattern: re.Pattern[str]
               ) -> tuple[set[str], list[Path]]:
    text = spec.read_text(encoding="utf-8")
    check_sections(rep, spec, text)
    header = text.split("\n## ", 1)[0]
    status = re.search(r"^- Status:\s*(.+)$", header, re.M)
    if status is None or not any(
            normalize(status.group(1)).startswith(s)
            for s in SPEC_STATUS):
        rep.error("SPC-001", spec,
                  "cabeçalho sem `- Status:` válido "
                  f"({', '.join(SPEC_STATUS)})")
    if not re.search(r"^- Constituição:", header, re.M):
        rep.warn("SPC-002", spec, "cabeçalho sem `- Constituição:`")
    registry = sections(text).get("registro de fontes", "")
    sources = set(SRC_ROW.findall(registry))
    if not sources:
        rep.error("SRC-002", spec, "registro de fontes sem SRC-###")
    blocks = requirement_blocks(text)
    if not blocks:
        rep.error("REQ-000", spec, "nenhum REQ-NNN/NFR-NNN declarado")
    headings = REQ_HEAD.findall(text)
    for rid in sorted({h for h in headings if headings.count(h) > 1}):
        rep.error("REQ-010", spec, f"{rid}: ID duplicado")
    for rid, block in blocks.items():
        check_requirement(rep, spec, rid, block, sources)
    cited = set(SRC_ID.findall("\n".join(ORIGEM.findall(text))))
    for src in sorted(sources - cited):
        rep.warn("SRC-003", spec, f"{src} não é citado em nenhum origem:")
    docs = source_documents(root, spec, text)
    if not docs:
        rep.warn("FON-001", spec,
                 "nenhum documento de origem fora de .github/ citado")
    for doc in docs:
        doc_text = doc.read_text(encoding="utf-8")
        for sid in sorted(set(source_pattern.findall(doc_text))):
            if not re.search(rf"\b{re.escape(sid)}\b", text):
                rep.error("FON-002", spec,
                          f"{sid} de {doc.relative_to(root).as_posix()} "
                          "sem requisito nem disposição em spec.md")
    return set(blocks), docs


def check_companion(rep: Report, path: Path, active: set[str],
                    prefix: str) -> None:
    text = path.read_text(encoding="utf-8")
    check_sections(rep, path, text)
    wanted = {i for i in active if i.startswith(prefix)}
    present = {i for i in REQ_ID.findall(text) if i.startswith(prefix)}
    for rid in sorted(wanted - present):
        rep.error("XRF-001", path, f"{rid} de spec.md ausente")
    for rid in sorted(present - active):
        rep.error("XRF-002", path, f"{rid} não existe em spec.md")
    for number, line in enumerate(text.splitlines(), start=1):
        if EARS_LINE.match(line):
            rep.error("XRF-003", path,
                      f"L{number}: declaração EARS copiada; referencie "
                      "o ID de spec.md")


def check_plan(rep: Report, path: Path, active: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    check_sections(rep, path, text)
    present = set(REQ_ID.findall(text))
    for rid in sorted(active - present):
        rep.error("XRF-004", path, f"{rid} sem componente no plano")
    for rid in sorted(present - active):
        rep.error("XRF-002", path, f"{rid} não existe em spec.md")


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            if nxt not in state:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if node not in state:
            found = visit(node)
            if found:
                return found
    return None


def check_tasks(rep: Report, path: Path, active: set[str]) -> None:
    text = path.read_text(encoding="utf-8")
    check_sections(rep, path, text)
    tasks = list(TASK.finditer(text))
    if not tasks:
        rep.error("TSK-000", path, "nenhuma tarefa `- [ ] **T001 ...**`")
        return
    ids = [t.group("id") for t in tasks]
    for tid in sorted({i for i in ids if ids.count(i) > 1}):
        rep.error("TSK-001", path, f"{tid}: ID de tarefa duplicado")
    known = set(ids)
    graph: dict[str, set[str]] = {}
    traced: set[str] = set()
    done: set[str] = set()
    for task in tasks:
        tid, meta, body = task.group("id"), task.group("meta"), \
            task.group("body")
        if "[S]" not in meta and "[P]" not in meta:
            rep.error("TSK-002", path, f"{tid}: sem marcador [S] ou [P]")
        refs = set(REQ_ID.findall(meta + body))
        if not refs:
            rep.warn("TSK-003", path, f"{tid}: não rastreia REQ/NFR")
        for rid in sorted(refs - active):
            rep.error("TSK-004", path, f"{tid}: {rid} não existe")
        traced |= refs
        deps: set[str] = set()
        for value in DEPENDS.findall(body):
            deps |= set(TASK_ID.findall(value))
        for dep in sorted(deps - known):
            rep.error("TSK-005", path, f"{tid}: depende de {dep} "
                      "inexistente")
        graph[tid] = deps & known
        if task.group("mark") in "xX":
            done.add(tid)
    for rid in sorted(active - traced):
        rep.error("TSK-006", path, f"{rid} sem tarefa")
    cycle = find_cycle(graph)
    if cycle:
        rep.error("TSK-007", path, f"ciclo: {' -> '.join(cycle)}")
    ledger = LEDGER.search(text)
    marked = set(TASK_ID.findall(ledger.group(1))) if ledger else set()
    for tid in sorted(done - marked):
        rep.error("TSK-008", path,
                  f"{tid} marcada [x] sem entrada no registro datado")
    for tid in sorted(marked - done):
        rep.error("TSK-008", path, f"{tid} no registro, mas desmarcada")
    count = COUNT.search(text)
    if count is None:
        rep.error("TSK-009", path, "sem `Tarefas concluídas: **N de M**`")
    elif (int(count.group(1)), int(count.group(2))) != \
            (len(done), len(known)):
        rep.error("TSK-009", path,
                  f"contagem {count.group(1)} de {count.group(2)} "
                  f"diverge de {len(done)} de {len(known)}")
    graph_text = raw_section(text, "Grafo de dependências")
    for tid in sorted(known - set(TASK_ID.findall(graph_text))):
        rep.error("TSK-010", path, f"{tid} ausente do grafo")


def raw_section(text: str, title: str) -> str:
    match = re.search(rf"^##\s+{re.escape(title)}\b.*?(?=^## |\Z)",
                      text, re.M | re.S)
    return match.group(0) if match else ""


def check_mermaid(rep: Report, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for index, match in enumerate(MERMAID.finditer(text), start=1):
        lines = [ln.strip() for ln in match.group(1).splitlines()
                 if ln.strip()]
        label = f"bloco Mermaid {index}"
        if not lines or lines[0] != THEME:
            rep.error("MMD-001", path, f"{label}: sem diretiva de tema")
            continue
        kind = lines[1].split()[0] if len(lines) > 1 else ""
        body = "\n".join(lines[1:])
        if kind in GRAPHLIKE:
            for entry in PALETTE:
                if lines.count(entry) != 1:
                    rep.error("MMD-002", path,
                              f"{label}: `{entry.split()[1]}` deve "
                              "aparecer uma vez")
        elif "classDef" in body:
            rep.error("MMD-003", path,
                      f"{label}: {kind} não deve conter classDef")
        for value in HEX.findall(body):
            full = "".join(c * 2 for c in value) if len(value) == 3 \
                else value
            if len({full[0:2], full[2:4], full[4:6]}) != 1:
                rep.error("MMD-004", path,
                          f"{label}: cor cromática #{value}")


def check_links(rep: Report, path: Path) -> None:
    text = without_fences(path.read_text(encoding="utf-8"))
    for target in LINK.findall(text):
        if re.match(r"(https?:|mailto:|#)", target) or "<" in target:
            continue
        local = target.split("#", 1)[0]
        if local and not (path.parent / local).exists():
            rep.error("LNK-001", path, f"link quebrado: {target}")


def packages(root: Path, selected: str | None) -> list[Path]:
    base = root / SPEC_DIR
    if not base.is_dir():
        return []
    found = sorted(p for p in base.iterdir()
                   if p.is_dir() and PACKAGE.match(p.name))
    if selected:
        found = [p for p in found if p.name == selected
                 or p.name.startswith(f"{selected}-")]
    return found


def validate(root: Path, selected: str | None, require_full: bool,
             source_pattern: str) -> tuple[Report, int]:
    rep = Report(root)
    pattern = re.compile(source_pattern)
    for name in FORBIDDEN_DIRS:
        if (root / name).is_dir():
            rep.error("PKG-001", root / name,
                      f"especificações fora de {SPEC_DIR}/; mova para "
                      f"{SPEC_DIR}/<NNN>-<funcionalidade>/")
    constitution = root / "CONSTITUTION.md"
    if not constitution.is_file():
        rep.error("CON-001", constitution,
                  "CONSTITUTION.md ausente; /write-ears-spec cria em "
                  "Rascunho")
    found = packages(root, selected)
    extra = [root / "CONSTITUTION.md", root / "CODEMAP.md"]
    extra += sorted((root / "docs" / "adr").glob("*.md"))
    for path in extra:
        if path.is_file():
            check_mermaid(rep, path)
    for package in found:
        files = {n: package / n for n in REQUIRED_FILES + STAGE_FILES}
        for name in REQUIRED_FILES:
            if not files[name].is_file():
                rep.error("PKG-002", files[name], "arquivo obrigatório "
                          "ausente")
        for name in STAGE_FILES:
            if not files[name].is_file():
                level = rep.error if require_full else rep.warn
                level("PKG-003", files[name],
                      "etapa ainda não produzida")
        if files["tasks.md"].is_file() and not files["plan.md"].is_file():
            rep.error("PKG-004", files["tasks.md"],
                      "tasks.md existe sem plan.md")
        active: set[str] = set()
        docs: list[Path] = []
        if files["spec.md"].is_file():
            active, docs = check_spec(rep, root, files["spec.md"],
                                      pattern)
        if files["frd.md"].is_file():
            check_companion(rep, files["frd.md"], active, "REQ-")
        if files["nfrd.md"].is_file():
            check_companion(rep, files["nfrd.md"], active, "NFR-")
        if files["plan.md"].is_file():
            check_plan(rep, files["plan.md"], active)
        if files["tasks.md"].is_file():
            check_tasks(rep, files["tasks.md"], active)
        primary = docs[0] if docs else None
        for path in sorted(package.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            check_anchors(rep, root, path, text, primary)
            check_mermaid(rep, path)
            check_links(rep, path)
    return rep, len(found)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package", help="ex.: 001 ou 001-sala-do-eco")
    parser.add_argument("--require-full", action="store_true",
                        help="exige plan.md e tasks.md")
    parser.add_argument("--strict", action="store_true",
                        help="trata avisos como erros")
    parser.add_argument("--source-id-pattern", default=SOURCE_ID_DEFAULT,
                        help="regex dos IDs no documento de origem")
    parser.add_argument("--format", choices=("text", "json"),
                        default="text")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    rep, count = validate(root, args.package, args.require_full,
                          args.source_id_pattern)
    errors = [f for f in rep.items if f.level == "ERRO"]
    warnings = [f for f in rep.items if f.level == "AVISO"]
    if args.format == "json":
        print(json.dumps({"packages": count,
                          "findings": [asdict(f) for f in rep.items]},
                         ensure_ascii=False, indent=2))
    else:
        for item in rep.items:
            print(f"{item.level} [{item.code}] {item.path}: "
                  f"{item.message}")
        print(f"{count} pacote(s) em {SPEC_DIR}/, {len(errors)} erro(s), "
              f"{len(warnings)} aviso(s).")
    if count == 0:
        print(f"nenhum pacote em {SPEC_DIR}/<NNN>-<funcionalidade>/; "
              "recusando aprovação vazia", file=sys.stderr)
        return 2
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
