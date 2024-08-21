
# Detalhamento da Pergunta 2.1: Quais são os grupos mais influentes na aprovação de projetos?

## Modularidade: Conceito e Avaliação

**O que é Modularidade?**
A modularidade é uma métrica utilizada em análise de redes para avaliar a qualidade da divisão de uma rede em comunidades. Ela quantifica o quão bem a rede é particionada em grupos (comunidades) que têm muitas conexões internas em comparação com o esperado aleatoriamente. Em outras palavras, quanto maior a modularidade, mais densas e bem definidas são as comunidades em termos de conexões internas, em oposição às conexões entre diferentes comunidades.

**Como é Calculada?**
A modularidade é calculada da seguinte forma:

```
Q = (1/2m) * sum_ij [ A_ij - (k_i * k_j / 2m) ] * delta(c_i, c_j)
```

Onde:
- `A_ij` é o peso da aresta entre os nós `i` e `j`.
- `k_i` e `k_j` são os graus (número de conexões) dos nós `i` e `j`, respectivamente.
- `m` é o número total de arestas na rede.
- `delta(c_i, c_j)` é a função delta de Kronecker, que é 1 se `i` e `j` estiverem na mesma comunidade, e 0 caso contrário.

**Avaliação da Modularidade**
Para avaliar a modularidade em diferentes períodos ou cenários, você pode:
1. **Comparar Modularity Scores ao Longo do Tempo:** Calcular a modularidade para diferentes períodos (e.g., anos eleitorais vs. não-eleitorais) e comparar os valores. Se houver uma mudança significativa na modularidade, isso pode indicar que a estrutura das comunidades está mudando ao longo do tempo, possivelmente refletindo mudanças nas alianças políticas.
  
2. **Comparação entre Cenários:** Avaliar a modularidade em cenários específicos, como antes e depois de crises políticas, mudanças de governo, ou eventos marcantes. Comparar a modularidade nesses cenários pode revelar a resiliência ou vulnerabilidade das comunidades a essas mudanças.

## Frequência de Aprovação de Projetos: Conceito e Avaliação

**O que Significa?**
A frequência de aprovação de projetos dentro de uma comunidade mede a proporção de proposições que são aprovadas em que a maioria dos membros dessa comunidade vota favoravelmente. Isso pode indicar a coesão e a força da influência de uma comunidade em particular.

**Como Avaliar?**
1. **Identificação de Comunidades:** Primeiramente, você detecta as comunidades usando o algoritmo Leiden ou outro de sua escolha.
  
2. **Contagem de Votos Favoráveis:** Dentro de cada comunidade, conte quantas proposições foram votadas favoravelmente pela maioria dos membros dessa comunidade.

3. **Comparação com o Total de Proposições:** Compare a frequência de aprovação dentro da comunidade com o total de proposições em que os membros dessa comunidade participaram. Isso dará uma ideia de quão influente essa comunidade é na aprovação de projetos.

4. **Análise Temporal:** Repita essa avaliação em diferentes períodos para ver se a influência das comunidades muda com o tempo.

## Normalized Mutual Information (NMI): Conceito e Avaliação

**O que é NMI?**
O NMI (Normalized Mutual Information) é uma métrica usada para comparar duas partições diferentes da mesma rede, ou seja, para comparar como duas diferentes divisões em comunidades correspondem entre si. Um valor de NMI de 1 indica que as duas partições são idênticas, enquanto um valor de 0 indica que não há correspondência entre elas.

**Como é Calculado?**
O NMI é calculado com base na entropia das duas partições e na entropia conjunta delas. A fórmula básica é:

```
NMI(X, Y) = (2 * I(X; Y)) / (H(X) + H(Y))
```

Onde:
- `I(X; Y)` é a informação mútua entre as partições `X` e `Y`.
- `H(X)` e `H(Y)` são as entropias de `X` e `Y`, respectivamente.

**Avaliação com NMI**
Na prática, você usaria NMI para:
1. **Comparar Partições ao Longo do Tempo:** Comparar a detecção de comunidades em diferentes períodos para ver se as comunidades permanecem consistentes.
  
2. **Comparar Diferentes Algoritmos:** Avaliar se diferentes algoritmos de detecção de comunidades (e.g., Leiden vs. Louvain) produzem resultados semelhantes.

## Comparação da Taxa de Aprovação Dentro e Fora das Comunidades

**Como Comparar?**
1. **Definição de Taxa de Aprovação:** Calcular a taxa de aprovação como o número de projetos aprovados dividido pelo número total de projetos propostos dentro da comunidade.

2. **Taxa de Aprovação Interna:** Para cada comunidade detectada, calcule a taxa de aprovação interna, ou seja, projetos em que a maioria dos membros da comunidade vota a favor.

3. **Taxa de Aprovação Externa:** Calcule a taxa de aprovação para os membros fora dessa comunidade.

4. **Análise Comparativa:** Compare essas taxas para ver se as comunidades têm uma influência maior ou menor na aprovação de projetos em comparação com membros fora das comunidades. Se a taxa de aprovação interna for significativamente maior, isso pode indicar que a comunidade é influente na aprovação de projetos.

5. **Testes Estatísticos:** Realizar testes de significância (e.g., teste de Mann-Whitney) para avaliar se as diferenças nas taxas de aprovação são estatisticamente significativas.
