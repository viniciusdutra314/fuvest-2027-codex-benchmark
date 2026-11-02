import argparse
import csv
import shutil
import subprocess
import time
from datetime import timedelta
from io import BytesIO, StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
from urllib.request import urlopen

import pdfplumber


type Model = Literal[
    "gpt-6-astra", "gpt-6.1-sol", "gpt-6.1-terra", "gpt-6-luna"
]
type Thinking = Literal["none", "low", "medium", "high", "xhigh", "max"]

ROOT = Path(__file__).resolve().parent
GABARITO_URL = "https://www.fuvest.br/arquivos/vestibular/fuvest2027-fase1-gabarito.pdf"
PROVA = "fuvest2027-fase1-V1.pdf"


def obter_gabarito() -> list[str]:
    with urlopen(GABARITO_URL, timeout=30) as resposta:
        with pdfplumber.open(BytesIO(resposta.read())) as pdf:
            tabela = sorted(
                pdf.pages[0].find_tables(), key=lambda t: t.bbox[0]
            )[0].extract()[1:]

    return [linha[1] for linha in tabela] + [linha[3] for linha in tabela]


def ler_respostas(texto: str) -> list[str]:
    linhas = list(csv.DictReader(StringIO(texto.strip())))
    assert len(linhas) == 80
    assert [int(linha["questao"]) for linha in linhas] == list(range(1, 81))
    respostas = [linha["resposta"].strip() for linha in linhas]
    assert all(resposta in "ABCDE" for resposta in respostas)
    return respostas


def acertos(respostas: list[str], gabarito: list[str]) -> int:
    return 1 + sum(
        resposta == correta
        for questao, (resposta, correta) in enumerate(
            zip(respostas, gabarito, strict=True), start=1
        )
        if questao != 23  # Questão anulada na prova V1.
    )


def run_unbiased_codex(model: Model, thinking: Thinking) -> list[str]:
    prompt = f"""Resolva as 80 questões da FUVEST 2027 no arquivo {PROVA}.
    Use somente seu conhecimento interno e o conteúdo do PDF.
    Analise também figuras, gráficos e diagramas.

    Responda exclusivamente em CSV, com o cabeçalho:
    questao,resposta

    Inclua exatamente 80 questões, numeradas de 1 a 80, em ordem.
    Não inclua explicações nem blocos Markdown.
    """

    with TemporaryDirectory(prefix="fuvest-") as tmp:
        trabalho = Path(tmp)
        shutil.copy2(ROOT / PROVA, trabalho / PROVA)

        processo = subprocess.run(
            [
                "codex", "exec",
                "--ignore-user-config",
                "--ignore-rules",
                "--ephemeral",
                "--skip-git-repo-check",
                "--sandbox", "workspace-write",
                "--model", model,
                "--config", 'approval_policy="never"',
                "--config", f'model_reasoning_effort="{thinking}"',
                "--config", 'web_search="disabled"',
                "--config", "sandbox_workspace_write.network_access=false",
                "--config", "features.apps=false",
                "--config", "apps._default.enabled=false",
                "--config", "plugins._default.enabled=false",
                "--config", "project_doc_max_bytes=0",
                "-",
            ],
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            cwd=trabalho,
            check=True,
        )

    return ler_respostas(processo.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark FUVEST 2027 — Codex")
    parser.add_argument("model")
    parser.add_argument("thinking")
    args = parser.parse_args()

    inicio = time.perf_counter()
    respostas = run_unbiased_codex(args.model, args.thinking)
    duracao = time.perf_counter() - inicio

    gabarito = obter_gabarito()  # Download somente depois que o Codex terminar.
    nota = acertos(respostas, gabarito)

    print(f"Modelo: {args.model}")
    print(f"Thinking: {args.thinking}")
    print(f"Tempo: {timedelta(seconds=round(duracao))}")
    print(f"Acertos: {nota}/80")
    erros=[
        questao
        for questao, (resposta, correta) in enumerate(
            zip(respostas, gabarito, strict=True), start=1
        )
        if questao != 23 and resposta!=correta
    ]
    print(f"Questões erradas: {erros}")


if __name__ == "__main__":
    main()
