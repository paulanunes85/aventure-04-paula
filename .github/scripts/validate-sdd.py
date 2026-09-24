#!/usr/bin/env python3
"""Valida os pacotes SDD em .spec/ e a rastreabilidade com as fontes.

Contrato: .github/instructions/sdd-artifacts.instructions.md.
Somente leitura. Validacao textual nao prova semantica EARS, aprovacao
humana, renderizacao de diagramas nem resultado de testes.
A cobertura dos IDs da fonte e o indice .spec/README.md sao verificados
sobre todos os pacotes, mesmo com --package.

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
INDEX = "README.md"
FORBIDDEN_DIRS = ("specs", ".specs")
PACKAGE = re.compile(r"^\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SOURCE_ID_DEFAULT = r"\b(?:RF|RNF|RN)-\d+\b"
HISTORY = ("histórico de mudanças",)

SPECIFICATION = "SPECIFICATION.md"
TRACEABILITY = "SOURCE_TRACEABILITY.md"
FRD = "FRD.md"
NFRD = "NFRD.md"
ANALYSIS = "ANALYSIS.md"
DESIGN = "DESIGN.md"
DECISIONS = "DECISIONS.md"
TASKS = "TASKS.md"
TESTING = "TESTING.md"
TDD = "TDD.md"
CHECKLIST = "CHECKLIST.md"
CROSS = "CROSS_ANALYSIS.md"
VERIFICATION = "VERIFICATION.md"

STAGES: tuple[tuple[str, ...], ...] = (
    (SPECIFICATION, TRACEABILITY, FRD, NFRD),
    (ANALYSIS, DESIGN, DECISIONS),
    (TASKS, TESTING, TDD, CHECKLIST, CROSS, VERIFICATION),
)
FILES = tuple(name for stage in STAGES for name in stage)
FOLDERS = ("checkpoints", "contracts", "evidence")
CHECKPOINTS = {
    "spec-to-plan.yaml": 1,
    "plan-to-tasks.yaml": 2,
    "test-coverage.yaml": 2,
}
LEGACY = ("spec.md", "plan.md", "tasks.md", "frd.md", "nfrd.md")

SECTIONS: dict[str, tuple[tuple[str, ...], ...]] = {
    SPECIFICATION: (
        ("problema e resultado",),
        ("escopo e não objetivos",),
        ("atores e dependências",),
        ("requisitos",),
        ("premissas, bloqueios e perguntas em aberto",),
        ("validação",),
        HISTORY,
    ),
    TRACEABILITY: (
        ("registro de fontes",),
        ("matriz de rastreabilidade",),
        ("cobertura da fonte", "disposição dos ids da fonte"),
        ("disposições históricas",),
        HISTORY,
    ),
    FRD: (
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
    NFRD: (
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
    ANALYSIS: (
        ("inventário de evidências",),
        ("análise de lacunas",),
        ("opções e trade-offs",),
        ("registro de riscos",),
        HISTORY,
    ),
    DESIGN: (
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
        ("design de observabilidade",),
        ("superfície de implementação",),
        ("visão de entrega e rastreabilidade",),
        ("riscos e trade-offs",),
        ("desenvolvimento em fases",),
        HISTORY,
    ),
    DECISIONS: (
        ("registro de decisões",),
        ("adrs vinculados",),
        HISTORY,
    ),
    TASKS: (
        ("gate pré-implementação",),
        ("regras de execução",),
        ("grafo de dependências",),
        ("desvios",),
        ("gate de conclusão",),
        ("registro de execução",),
        HISTORY,
    ),
    TESTING: (
        ("estratégia de testes",),
        ("ambientes e dados de teste",),
        ("catálogo de testes",),
        ("mapa de testes",),
        ("cobertura e limites",),
        HISTORY,
    ),
    TDD: (
        ("regras do ciclo",),
        ("ciclos por critério de aceite",),
        ("refatorações planejadas",),
        HISTORY,
    ),
    CHECKLIST: (
        ("requisitos",),
        ("design",),
        ("prontidão para implementação",),
        ("verificação e release",),
        HISTORY,
    ),
    CROSS: (
        ("análise cruzada",),
        ("análise de órfãos",),
        ("consistência entre arquivos",),
        HISTORY,
    ),
    VERIFICATION: (
        ("verificações planejadas",),
        ("execuções de validadores",),
        ("resultados",),
        HISTORY,
    ),
}
MUST_COVER = (TRACEABILITY, DESIGN, TESTING, CROSS, VERIFICATION)
FILE_STATUS = (
    "não iniciado", "rascunho", "pronto para revisão", "planejado",
    "aprovado", "implementado", "verificado",
)
EARS_PATTERNS = (
    "ubiquo", "orientado a evento", "evento", "orientado a estado",
    "estado", "opcional", "indesejado", "complexo",
)

H2 = re.compile(r"^##[ \t]+([^\n]*\S)", re.M)
FENCE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
REQ_HEAD = re.compile(r"^###\s+((?:REQ|NFR)-\d{3})\s*:", re.M)
NEXT_HEAD = re.compile(r"^#{2,3}\s", re.M)
REQ_ID = re.compile(r"\b(?:REQ|NFR)-\d{3}\b")
AC_ID = re.compile(r"\bAC-(?:REQ|NFR)-\d{3}-\d{2}\b")
SRC_ID = re.compile(r"\bSRC-\d{3}\b")
SRC_ROW = re.compile(r"^\|\s*(SRC-\d{3})\s*\|", re.M)
ORIGEM = re.compile(r"^origem:[ \t]*(\S[^\n]*)", re.M)
STATUS = re.compile(r"^- Status:[ \t]*(\S[^\n]*)", re.M)
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
DEPENDS = re.compile(r"Depende de:[ \t]*([^\n]+)")
LEDGER = re.compile(
    r"Marcadas como concluídas pela verificação:[ \t]*([^\n]*)")
COUNT = re.compile(r"Tarefas concluídas:\s*\*\*(\d+) de (\d+)\*\*")
FEATURE_ID = re.compile(r"\bid:\s*\"?(\d{3})\"?")
EVIDENCE_PATH = re.compile(r"\bevidence/[\w./-]+\.\w+")
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


@dataclass
class Package:
    path: Path
    texts: dict[str, str]
    produced: set[str]
    active: set[str]
    docs: list[Path]


def normalize(heading: str) -> str:
    text = unicodedata.normalize("NFC", heading).replace("`", "")
    text = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", text)
    text = re.sub(r"\s*\([^()]*\)$", "", text.strip())
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


def raw_section(text: str, title: str) -> str:
    match = re.search(rf"^##[ \t]+{re.escape(title)}\b.*?(?=^## |\Z)",
                      text, re.M | re.S | re.I)
    return match.group(0) if match else ""


def header(text: str) -> str:
    return text.split("\n## ", 1)[0]


def file_status(text: str) -> str | None:
    match = STATUS.search(header(text))
    if match is None:
        return None
    value = normalize(match.group(1))
    return next((s for s in FILE_STATUS if value.startswith(s)), None)


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
    if path.name == TASKS and not any(k.startswith("fase") for k in found):
        rep.error("SEC-001", path, "nenhuma seção `## Fase N`")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def resolve(root: Path, base: Path, token: str) -> Path | None:
    for candidate in (root / token, base / token):
        if candidate.is_file():
            return candidate
    return None


def shown_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def check_range(rep: Report, root: Path, path: Path, number: int,
                target: Path, match: re.Match[str],
                lengths: dict[Path, int]) -> None:
    start = int(match.group("a"))
    end = int(match.group("b") or start)
    size = lengths.setdefault(target, line_count(target))
    shown = shown_path(root, target)
    if start < 1 or end < start:
        rep.error("ANC-003", path,
                  f"L{number}: intervalo inválido {shown}#L{start}-L{end}")
    elif end > size:
        rep.error("ANC-004", path,
                  f"L{number}: {shown}#L{end} além do fim do arquivo "
                  f"({size} linhas)")


def check_anchors(rep: Report, root: Path, path: Path, text: str,
                  primary: Path | None) -> None:
    lengths: dict[Path, int] = {}
    for number, line in enumerate(text.splitlines(), start=1):
        current = primary
        for match in ANCHOR.finditer(line):
            token = match.group("path")
            if token:
                current = resolve(root, path.parent, token)
            if token and current is None:
                rep.error("ANC-001", path,
                          f"L{number}: arquivo citado não existe: {token}")
            elif current is None:
                rep.warn("ANC-002", path,
                         f"L{number}: âncora #L{match.group('a')} sem "
                         "documento de origem identificável")
            else:
                check_range(rep, root, path, number, current, match,
                            lengths)


def requirement_blocks(text: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    for match in REQ_HEAD.finditer(text):
        rest = text[match.end():]
        nxt = NEXT_HEAD.search(rest)
        blocks.setdefault(match.group(1), rest[:nxt.start()] if nxt
                          else rest)
    return blocks


def source_documents(root: Path, spec: Path, text: str) -> list[Path]:
    docs: list[Path] = []
    for value in ORIGEM.findall(text):
        for token in PATH_TOKEN.findall(value):
            found = None if token.startswith(".github/") \
                else resolve(root, spec.parent, token)
            if found and found not in docs:
                docs.append(found)
    return docs


def field_value(block: str, name: str) -> str | None:
    match = re.search(rf"^- {name}:[ \t]*(\S[^\n]*)", block, re.M)
    return match.group(1).strip() if match else None


def check_origem(rep: Report, spec: Path, rid: str, block: str,
                 sources: set[str] | None) -> None:
    origem = ORIGEM.search("\n".join(block.splitlines()[:21]))
    if origem is None:
        rep.error("REQ-001", spec,
                  f"{rid}: sem linha `origem:` até 20 linhas após o título")
        return
    value = origem.group(1)
    cited = set(SRC_ID.findall(value))
    greenfield = re.search(r"\[GREENFIELD\]\s*\S", value)
    if not cited and not PATH_TOKEN.search(value) and not greenfield:
        rep.error("REQ-002", spec,
                  f"{rid}: `origem:` sem SRC-###, caminho ou "
                  "[GREENFIELD] justificado")
    for src in sorted(cited - (sources or cited)):
        rep.error("SRC-001", spec,
                  f"{rid}: {src} não está no registro de fontes de "
                  f"{TRACEABILITY}")


def check_metadata(rep: Report, spec: Path, rid: str, block: str) -> None:
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


def check_statement(rep: Report, spec: Path, rid: str, block: str) -> None:
    statements = EARS_LINE.findall(block)
    if not statements:
        rep.error("REQ-006", spec,
                  f"{rid}: sem declaração EARS (`> ... deve ...`)")
    elif len(statements) > 1:
        rep.warn("REQ-006", spec,
                 f"{rid}: mais de uma declaração EARS no bloco")
    has_ac = re.search(rf"\bAC-{rid}-\d{{2}}\b", block)
    if not has_ac and "BLOQUEADO" in block:
        rep.warn("REQ-007", spec,
                 f"{rid}: aceite BLOQUEADO; não entra no handoff")
    elif not has_ac:
        rep.error("REQ-007", spec, f"{rid}: sem AC-{rid}-NN")
    if "**Verificação**" not in block:
        rep.error("REQ-008", spec, f"{rid}: sem bloco **Verificação**")
    if rid.startswith("NFR-") and NFRD not in block:
        rep.warn("REQ-009", spec,
                 f"{rid}: não aponta o envelope de medição em {NFRD}")


def check_specification(rep: Report, pkg: Package) -> None:
    spec = pkg.path / SPECIFICATION
    text = pkg.texts[SPECIFICATION]
    if not re.search(r"^- Constituição:", header(text), re.M):
        rep.warn("SPC-002", spec, "cabeçalho sem `- Constituição:`")
    trace = pkg.texts.get(TRACEABILITY) if TRACEABILITY in pkg.produced \
        else None
    sources = None
    if trace is not None:
        registry = sections(trace).get("registro de fontes", "")
        sources = set(SRC_ROW.findall(registry))
        if not sources:
            rep.error("SRC-002", pkg.path / TRACEABILITY,
                      "registro de fontes sem SRC-###")
    blocks = requirement_blocks(text)
    if not blocks:
        rep.error("REQ-000", spec, "nenhum REQ-NNN/NFR-NNN declarado")
    headings = REQ_HEAD.findall(text)
    for rid in sorted({h for h in headings if headings.count(h) > 1}):
        rep.error("REQ-010", spec, f"{rid}: ID duplicado")
    for rid, block in blocks.items():
        check_origem(rep, spec, rid, block, sources)
        check_metadata(rep, spec, rid, block)
        check_statement(rep, spec, rid, block)
    cited = set(SRC_ID.findall("\n".join(ORIGEM.findall(text))))
    for src in sorted((sources or set()) - cited):
        rep.warn("SRC-003", pkg.path / TRACEABILITY,
                 f"{src} não é citado em nenhum origem:")
    if not pkg.docs:
        rep.warn("FON-001", spec,
                 "nenhum documento de origem fora de .github/ citado")


def check_coverage(rep: Report, path: Path, text: str, active: set[str],
                   prefix: str = "") -> None:
    wanted = {i for i in active if i.startswith(prefix)}
    present = {i for i in REQ_ID.findall(text) if i.startswith(prefix)}
    for rid in sorted(wanted - present):
        rep.error("XRF-001", path, f"{rid} de {SPECIFICATION} ausente")
    for rid in sorted(present - active):
        rep.error("XRF-002", path, f"{rid} não existe em {SPECIFICATION}")


def check_no_ears(rep: Report, path: Path, text: str) -> None:
    for number, line in enumerate(text.splitlines(), start=1):
        if EARS_LINE.match(line):
            rep.error("XRF-003", path,
                      f"L{number}: declaração EARS copiada; referencie o "
                      f"ID de {SPECIFICATION}")


def check_tdd(rep: Report, pkg: Package) -> None:
    text = pkg.texts[TDD]
    spec = pkg.texts.get(SPECIFICATION, "")
    for ac in sorted(set(AC_ID.findall(spec)) - set(AC_ID.findall(text))):
        rep.error("XRF-005", pkg.path / TDD,
                  f"{ac} sem ciclo RED/GREEN planejado")


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in sorted(graph.get(node, ())):
            if state.get(nxt) == 1:
                return stack[stack.index(nxt):] + [nxt]
            found = None if nxt in state else visit(nxt)
            if found:
                return found
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        found = None if node in state else visit(node)
        if found:
            return found
    return None


def task_graph(rep: Report, path: Path, tasks: list[re.Match[str]],
               active: set[str]) -> tuple[dict[str, set[str]], set[str]]:
    known = {t.group("id") for t in tasks}
    graph: dict[str, set[str]] = {}
    traced: set[str] = set()
    for task in tasks:
        tid, meta, body = task.group("id", "meta", "body")
        if "[S]" not in meta and "[P]" not in meta:
            rep.error("TSK-002", path, f"{tid}: sem marcador [S] ou [P]")
        refs = set(REQ_ID.findall(meta + body))
        if not refs:
            rep.warn("TSK-003", path, f"{tid}: não rastreia REQ/NFR")
        for rid in sorted(refs - active):
            rep.error("TSK-004", path, f"{tid}: {rid} não existe")
        traced |= refs
        deps = {d for v in DEPENDS.findall(body) for d in TASK_ID.findall(v)}
        for dep in sorted(deps - known):
            rep.error("TSK-005", path,
                      f"{tid}: depende de {dep} inexistente")
        graph[tid] = deps & known
    for rid in sorted(active - traced):
        rep.error("TSK-006", path, f"{rid} sem tarefa")
    return graph, known


def check_ledger(rep: Report, path: Path, text: str,
                 tasks: list[re.Match[str]]) -> None:
    done = {t.group("id") for t in tasks if t.group("mark") in "xX"}
    ledger = LEDGER.search(text)
    marked = set(TASK_ID.findall(ledger.group(1))) if ledger else set()
    for tid in sorted(done - marked):
        rep.error("TSK-008", path,
                  f"{tid} marcada [x] sem entrada no registro datado")
    for tid in sorted(marked - done):
        rep.error("TSK-008", path, f"{tid} no registro, mas desmarcada")
    count = COUNT.search(text)
    expected = (len(done), len(tasks))
    if count is None:
        rep.error("TSK-009", path, "sem `Tarefas concluídas: **N de M**`")
    elif (int(count.group(1)), int(count.group(2))) != expected:
        rep.error("TSK-009", path,
                  f"contagem {count.group(1)} de {count.group(2)} "
                  f"diverge de {expected[0]} de {expected[1]}")


def check_tasks(rep: Report, pkg: Package) -> set[str]:
    path = pkg.path / TASKS
    text = pkg.texts[TASKS]
    tasks = list(TASK.finditer(text))
    if not tasks:
        rep.error("TSK-000", path, "nenhuma tarefa `- [ ] **T001 ...**`")
        return set()
    ids = [t.group("id") for t in tasks]
    for tid in sorted({i for i in ids if ids.count(i) > 1}):
        rep.error("TSK-001", path, f"{tid}: ID de tarefa duplicado")
    graph, known = task_graph(rep, path, tasks, pkg.active)
    cycle = find_cycle(graph)
    if cycle:
        rep.error("TSK-007", path, f"ciclo: {' -> '.join(cycle)}")
    check_ledger(rep, path, text, tasks)
    graph_text = raw_section(text, "Grafo de dependências")
    for tid in sorted(known - set(TASK_ID.findall(graph_text))):
        rep.error("TSK-010", path, f"{tid} ausente do grafo")
    return known


def check_mermaid(rep: Report, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for index, match in enumerate(MERMAID.finditer(text), start=1):
        lines = [ln.strip() for ln in match.group(1).splitlines()
                 if ln.strip()]
        label = f"bloco Mermaid {index}"
        if not lines or lines[0] != THEME:
            rep.error("MMD-001", path, f"{label}: sem diretiva de tema")
            continue
        check_palette(rep, path, label, lines[1:])


def check_palette(rep: Report, path: Path, label: str,
                  lines: list[str]) -> None:
    kind = lines[0].split()[0] if lines else ""
    body = "\n".join(lines)
    if kind in GRAPHLIKE:
        for entry in PALETTE:
            if lines.count(entry) != 1:
                rep.error("MMD-002", path,
                          f"{label}: `{entry.split()[1]}` deve aparecer "
                          "uma vez")
    elif "classDef" in body:
        rep.error("MMD-003", path,
                  f"{label}: {kind} não deve conter classDef")
    for value in HEX.findall(body):
        full = "".join(c * 2 for c in value) if len(value) == 3 else value
        if len({full[0:2], full[2:4], full[4:6]}) != 1:
            rep.error("MMD-004", path, f"{label}: cor cromática #{value}")


def check_links(rep: Report, path: Path) -> None:
    text = without_fences(path.read_text(encoding="utf-8"))
    for target in LINK.findall(text):
        if re.match(r"(https?:|mailto:|#)", target) or "<" in target:
            continue
        local = target.split("#", 1)[0]
        if local and not (path.parent / local).exists():
            rep.error("LNK-001", path, f"link quebrado: {target}")


def check_evidence_refs(rep: Report, pkg: Package) -> None:
    for name in pkg.produced:
        for token in sorted(set(EVIDENCE_PATH.findall(pkg.texts[name]))):
            if not (pkg.path / token).is_file():
                rep.error("EVD-001", pkg.path / name,
                          f"evidência citada não existe: {token}")


def reached(produced: set[str]) -> int:
    return max((i for i, stage in enumerate(STAGES)
                if produced & set(stage)), default=-1)


def check_layout(rep: Report, path: Path, require_full: bool,
                 produced: set[str], texts: dict[str, str]) -> None:
    for name in LEGACY:
        if (path / name).is_file():
            rep.error("PKG-007", path / name,
                      "nome fora do padrão; use os arquivos em "
                      "MAIÚSCULAS do pacote")
    for name in FILES:
        if name not in texts:
            rep.error("PKG-002", path / name, "arquivo obrigatório ausente")
    for folder in FOLDERS:
        if not (path / folder / INDEX).is_file():
            rep.error("PKG-006", path / folder / INDEX,
                      f"pasta {folder}/ sem índice {INDEX}")
    top = reached(produced)
    for level, stage in enumerate(STAGES):
        stubs = [n for n in stage if n in texts and n not in produced]
        for name in stubs:
            if level == 0:
                rep.error("STG-001", path / name,
                          "arquivo da etapa de requisitos não iniciado")
            elif level < top:
                rep.error("STG-003", path / name,
                          "não iniciado, mas uma etapa posterior já foi "
                          "produzida")
            else:
                (rep.error if require_full else rep.warn)(
                    "PKG-003", path / name, "etapa ainda não produzida")
    for name, level in CHECKPOINTS.items():
        if top >= level and not (path / "checkpoints" / name).is_file():
            rep.error("CKP-001", path / "checkpoints" / name,
                      "checkpoint ausente para a etapa produzida")
    if top >= 1 and not (path / "contracts" / "manifest.yaml").is_file():
        rep.error("CTR-001", path / "contracts" / "manifest.yaml",
                  "manifesto de contratos ausente")
    extras = {p.name for p in path.glob("*.md")} - set(FILES) - set(LEGACY)
    for name in sorted(extras):
        rep.warn("PKG-008", path / name, "arquivo fora da estrutura")


def check_checkpoints(rep: Report, pkg: Package,
                      task_ids: set[str]) -> None:
    number = pkg.path.name[:3]
    wanted = {
        "spec-to-plan.yaml": (pkg.active, REQ_ID),
        "plan-to-tasks.yaml": (task_ids, TASK_ID),
        "test-coverage.yaml": (pkg.active, REQ_ID),
    }
    for name, (ids, pattern) in wanted.items():
        path = pkg.path / "checkpoints" / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        feature = FEATURE_ID.search(text)
        if feature is None or feature.group(1) != number:
            rep.error("CKP-002", path,
                      f"`feature.id` deve ser \"{number}\"")
        for item in sorted(ids - set(pattern.findall(text))):
            rep.error("CKP-003", path, f"{item} ausente do checkpoint")


def load_package(root: Path, path: Path) -> Package:
    texts = {n: (path / n).read_text(encoding="utf-8")
             for n in FILES if (path / n).is_file()}
    produced = {n for n, t in texts.items()
                if file_status(t) not in (None, "não iniciado")}
    spec = texts.get(SPECIFICATION, "") if SPECIFICATION in produced \
        else ""
    active = set(requirement_blocks(spec))
    docs = source_documents(root, path / SPECIFICATION, spec)
    return Package(path, texts, produced, active, docs)


def check_content(rep: Report, pkg: Package) -> None:
    for name in sorted(pkg.produced):
        check_sections(rep, pkg.path / name, pkg.texts[name])
    for name, text in pkg.texts.items():
        if file_status(text) is None:
            rep.error("SPC-001", pkg.path / name,
                      "cabeçalho sem `- Status:` válido "
                      f"({', '.join(FILE_STATUS)})")
    if SPECIFICATION in pkg.produced:
        check_specification(rep, pkg)
    for name in MUST_COVER:
        if name in pkg.produced:
            check_coverage(rep, pkg.path / name, pkg.texts[name],
                           pkg.active)
    for name, prefix in ((FRD, "REQ-"), (NFRD, "NFR-")):
        if name in pkg.produced:
            check_coverage(rep, pkg.path / name, pkg.texts[name],
                           pkg.active, prefix)
            check_no_ears(rep, pkg.path / name, pkg.texts[name])
    if TDD in pkg.produced:
        check_tdd(rep, pkg)
    task_ids = check_tasks(rep, pkg) if TASKS in pkg.produced else set()
    check_checkpoints(rep, pkg, task_ids)
    check_evidence_refs(rep, pkg)


def check_package(rep: Report, root: Path, path: Path,
                  require_full: bool) -> Package:
    pkg = load_package(root, path)
    check_layout(rep, path, require_full, pkg.produced, pkg.texts)
    check_content(rep, pkg)
    primary = pkg.docs[0] if pkg.docs else None
    for md in sorted(path.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        check_anchors(rep, root, md, text, primary)
        check_mermaid(rep, md)
        check_links(rep, md)
    return pkg


def check_repository(rep: Report, root: Path) -> None:
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
    extra = [constitution, root / "CODEMAP.md"]
    extra += sorted((root / "docs" / "adr").glob("*.md"))
    for path in extra:
        if path.is_file():
            check_mermaid(rep, path)


def check_index(rep: Report, root: Path, found: list[Path]) -> None:
    index = root / SPEC_DIR / INDEX
    numbers = [p.name[:3] for p in found]
    for number in sorted({n for n in numbers if numbers.count(n) > 1}):
        rep.error("PKG-005", root / SPEC_DIR,
                  f"número de pacote {number} repetido")
    if not found:
        return
    if not index.is_file():
        rep.error("IDX-001", index,
                  "índice de funcionalidades ausente; liste todo pacote")
        return
    check_mermaid(rep, index)
    check_links(rep, index)
    text = index.read_text(encoding="utf-8")
    listed = set(re.findall(r"\b\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*", text))
    names = {p.name for p in found}
    for name in sorted(names - listed):
        rep.error("IDX-002", index, f"pacote {name} ausente do índice")
    for name in sorted(listed - names):
        rep.error("IDX-003", index,
                  f"{name} citado no índice, mas não existe em {SPEC_DIR}/")


def check_source_coverage(rep: Report, root: Path, pkgs: list[Package],
                          pattern: re.Pattern[str]) -> None:
    joined = "\n".join(
        p.texts.get(n, "") for p in pkgs
        for n in (SPECIFICATION, TRACEABILITY))
    docs: list[Path] = []
    for pkg in pkgs:
        docs += [d for d in pkg.docs if d not in docs]
    for doc in docs:
        shown = shown_path(root, doc)
        ids = set(pattern.findall(doc.read_text(encoding="utf-8")))
        for sid in sorted(ids):
            if not re.search(rf"\b{re.escape(sid)}\b", joined):
                rep.error("FON-002", doc,
                          f"{sid} sem requisito nem disposição em nenhum "
                          f"pacote de {SPEC_DIR}/ (fonte: {shown})")


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
    check_repository(rep, root)
    every = packages(root, None)
    check_index(rep, root, every)
    chosen = set(packages(root, selected))
    loaded: list[Package] = []
    for path in every:
        if path in chosen:
            loaded.append(check_package(rep, root, path, require_full))
        else:
            loaded.append(load_package(root, path))
    if any(reached(p.produced) >= 1 for p in loaded) and \
            not (root / "CODEMAP.md").is_file():
        rep.error("CMP-001", root / "CODEMAP.md",
                  "CODEMAP.md ausente com design produzido")
    check_source_coverage(rep, root, loaded, re.compile(source_pattern))
    return rep, len(chosen)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--package", help="ex.: 001 ou 001-sala-do-eco")
    parser.add_argument("--require-full", action="store_true",
                        help="exige todas as etapas produzidas")
    parser.add_argument("--strict", action="store_true",
                        help="trata avisos como erros")
    parser.add_argument("--source-id-pattern", default=SOURCE_ID_DEFAULT,
                        help="regex dos IDs no documento de origem")
    parser.add_argument("--format", choices=("text", "json"),
                        default="text")
    args = parser.parse_args(argv)
    rep, count = validate(args.root.resolve(), args.package,
                          args.require_full, args.source_id_pattern)
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
