from io import BytesIO
from urllib.request import urlopen
import pdfplumber
from typing import Literal
from benchmark import Model,Thinking,results_csv_path
import csv
type Respostas=Literal["A","B","C","D","E"]

def obter_gabarito():
    with urlopen("https://www.fuvest.br/arquivos/vestibular/fuvest2027-fase1-gabarito.pdf", timeout=30) as resposta:
        with pdfplumber.open(BytesIO(resposta.read())) as pdf:
            tabela = sorted(
                pdf.pages[0].find_tables(),
                key=lambda t: t.bbox[0]
            )[0].extract()[1:]

    return [linha[1] for linha in tabela] + [linha[3] for linha in tabela]

GABARITO=obter_gabarito()
NUM_QUESTÕES=len(GABARITO)

def acertos(respostas:list[Respostas])->int:
    return sum((x==y for x,y in zip(respostas,GABARITO,strict=True)))

def load_answers(model:Model,thinking:Thinking)->list[Respostas]:
    with open(results_csv_path(model,thinking), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row['resposta'] for row in reader]

def main()->None:
    x=load_answers("gpt-6.1-terra","low")
    print(acertos(x))

    
if __name__=="__main__":
    main()