from pathlib import Path
import subprocess
from typing import Literal

#usando como referência em 02/11/2026
#https://developers.openai.com/api/docs/models


type Model = Literal[
    "gpt-6-astra",
    "gpt-6.1-sol",
    "gpt-6.1-terra",
    "gpt-6-luna",
]

type Thinking = Literal[
    "none", "low", "medium", "high", "xhigh", "max"
]

def results_csv_path(model:Model,thinking:Thinking)->Path:
    return Path("results") / f"{model}-{thinking}.csv"


def run_unbiased_codex(model: Model, thinking: Thinking):
    resposta =results_csv_path(model,thinking)
    resposta.parent.mkdir(exist_ok=True)
    prompt = f"""
    Resolva a prova da FUVEST 2027 presente no arquivo
    fuvest2027-fase1-V1.pdf.

    Utilize somente seu conhecimento interno e o conteúdo do PDF.
    Analise também gráficos, figuras e diagramas.

    Responda exclusivamente em CSV, com o cabeçalho:
    questao,resposta

    Inclua exatamente 80 questões, numeradas de 1 a 80.
    Não inclua explicações nem blocos Markdown.
    """
    subprocess.run(
         [
        "codex", "exec",
        "--ignore-user-config",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox", "workspace-write",
        "--model", model,
        "--config", f'model_reasoning_effort="{thinking}"',
        "--config", 'web_search="disabled"',
        "--config", "sandbox_workspace_write.network_access=false",
        "--config", "features.apps=false",
        "--config", "plugins._default.enabled=false",
        "--output-last-message", str(resposta.resolve()),
        "-",
    ],
        input=prompt,
        text=True,
        stdout=subprocess.DEVNULL,
        check=True,
    )
    return resposta


def main():
    run_unbiased_codex("gpt-6.1-terra", "low")


if __name__=="__main__":
    main()