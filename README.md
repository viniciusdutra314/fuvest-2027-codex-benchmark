# Fuvest-2027-Codex-Benchmark

O quão bem será que diferentes modelos do ChatGPT performam na prova da Fuvest 2027? Hoje (02/11/2026) só faz
um dia que a prova da Fuvest foi aplicada, portanto isso não está no treinamento do modelo (ainda), eu desativei acesso a internet, dando somente o PDF da prova e um educado "se vira ai".

O código é um simples CLI que chama o codex com as permissões adequadas (o gabarito só é baixado
após o codex ser fechado):
```python
uv run benchmark.py model thinking
```

O output é o tempo de execução considerando o tool calling, taxa de acertos e questões erradas , algo importante
é que a Fuvest anulou uma questão, então tem uma questão que todo os modelos vão ganhar ponto.

### Resultados
Isso varia um pouco de execução à execução mas estão aqui alguns resultados interessantes, foi usada a prova V1 https://www.fuvest.br/arquivos/vestibular/fuvest2027-fase1-V1.pdf

```
Modelo: gpt-6.1-terra
Thinking: medium
Tempo: 0:00:56
Acertos: 79/80
Questões erradas: [6]
```

```
Modelo: gpt-6-astra
Thinking: low
Tempo: 0:01:49
Acertos: 78/80
Questões erradas: [6, 8]
```

```
Modelo: gpt-6.1-sol
Thinking: low
Tempo: 0:01:30
Acertos: 77/80
Questões erradas: [6, 8, 77]
```

```
Modelo: gpt-6-luna
Thinking: medium
Tempo: 0:02:22
Acertos: 77/80
Questões erradas: [8, 18, 35]
```