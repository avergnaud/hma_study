# WMA, HMA, EHMA, Hull-WEMA ?

J'ai fait cette étude suite à [ce tweet](https://twitter.com/PrfDude/status/1510050235611062277)

![tweet_EHMA](./doc/tweet.jpg?raw=true)

## WMA

_Weighted Moving Average_, Moyenne mobile "pondérée".

Par exemple, on récupère les 1000 dernières valeurs de :
```
pair_symbol = "ETH/USDT"
resolution = 3600 (1 heure)
```
|date et heure|index|poids(Weight)|valeur|
|-------------------|-----|-------------|------|
|2022-04-02T20:00:00|980|1|3470.2|
|2022-04-02T21:00:00|981|2|3477.6|
|2022-04-02T22:00:00|982|3|3466.5|
|...|...|...|...|
|2022-04-03T13:00:00|997|18|3498.9|
|2022-04-03T14:00:00|998|19|3513.7|
|2022-04-03T15:00:00|999|20|3518.1|

somme / (n*(n + 1) / 2) = 3487.3290476190473

C'est une moyenne mobile, avec des poids croissants : sur 20 périodes, le close de la dernière période a un poids de 20, le précédent 19...
 La somme des poids est donc `1 + 2 + 3 + ... + 18 + 19 + 20 = 20*(20 + 1)/2`

[https://en.wikipedia.org/wiki/Moving_average#Weighted_moving_average](https://en.wikipedia.org/wiki/Moving_average#Weighted_moving_average)

## HMA

_Hull Moving Average_

Une moyenne mobile "lente" est calculée sur plus de périodes, donc le poids de sa dernière période est plus faible.
 C'est vrai aussi pour une moyenne mobile pondérée, par rapport à une autre moyenne mobile pondérée calculée sur moins de périodes.

* On choisit N, le _Hull Moving Average look back_. Ici N = 20.
Pour chaque période :
* On calcule la `WMA_20` (moyenne mobile pondérée lente)
* On calcule la `WMA_10` (pour N/2, moyenne mobile pondérée rapide)
* On calcule le `delta = 2*WMA_10 - WMA_20`. Cette valeur vaut 2 fois la moyenne mobile rapide, moins la moyenne mobile lente.
* On calcule la `HMA` : moyenne mobile pondérée du `delta`, calculée sur `&radic;N. &radic;20 = 4.47` (arrondi à 5...)

[https://oxfordstrat.com/trading-strategies/hull-moving-average/](https://oxfordstrat.com/trading-strategies/hull-moving-average/)

## EHMA

_Exponential Hull Moving Average_

Définition d'une EMA : [Exponential Moving Average](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average)

* On choisit N, le _Hull Moving Average look back_. Ici N = 20.
Pour chaque période :
* On calcule la `EMA_20` (moyenne mobile exponentielle lente)
* On calcule la `EMA_10` (pour N/2, moyenne mobile exponentielle rapide)
* On calcule le `delta = 2*EMA_10 - EMA_20`. Cette valeur vaut 2 fois la moyenne mobile rapide, moins la moyenne mobile lente.
* On calcule la `EHMA` : moyenne mobile exponentielle du `delta`, calculée sur &radic;N. &radic;20 = 4.47 (arrondi à 5...)

### Trading

Stratégie : 
* Quand la EHMA devient décroissante, on a un signal de vente
* Quand la EHMA devient croissante, on a un signal d'achat

Cette stratégie n'est pas rentable sur les périodes courtes. En revanche, le EHMA est un très bon indicateur de tendance sur le long terme.

Pour 
```
pair_symbol = "BTC/USDT"
resolution = 604800 (1 semaine)
```

Tradingview :
![tradingview](./doc/tradingview_btcusd_1w_ehma.PNG?raw=true)

Python 3_ehma_colored.py :
![python](./doc/python_btcusd_1w_ehma.PNG?raw=true)

## Hull-WEMA

à creuser... cf [Hull-WEMA: A Novel Zero-Lag Approach in the Moving Average Family](./doc/IJMDMPaperRG.pdf)
