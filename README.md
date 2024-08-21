# Trading Algorítmico de la A a la Z con Python

- [Curso](https://cursos.frogamesformacion.com/courses/take/trading-algoritmico-1)
- [Repo](https://github.com/joanby/trading-algoritmico-a-z-con-python)

## Índice Sortino

El índice de Sortino es una estadística similar al índice de Sharpe con la misma interpretación. Sin embargo, el cálculo es ligeramente diferente. En efecto, en el índice de Sortino sólo se tiene en cuenta la volatilidad de las ganancias negativas porque es lo que tememos y no las ganancias alcistas que nos hacen ganar dinero.

- SortinoRatio < 0 : Inversión no rentable porque las ganancias son negativas.
- SortinoRatio < 1: Inversión rentable, pero el riesgo de la inversión es mayor que la rentabilidad.
- SortinoRatio > 1: Inversión muy rentable porque el riesgo es menor que el rendimiento.

## Índice Beta

La beta es un estadístico que indica la relación entre las variaciones de nuestra cartera y las del mercado que está representado por un índice (por ejemplo el SP500).

- abs(Beta) < 1: Es bueno porque significa que la cartera tiene una variación menor que el índice. (Si beta=0,9 significa que si el índice varía en 1 la cartera varía en 0,9)
- abs(Beta) > 1: No es bueno porque significa que su cartera tiene una variación mayor que el índice. (Si beta=1,1 significa que si el índice varía de 1 la cartera varía en 1,1)

abs(-x) = x = abs(x) (abs da sólo el valor de la variable no el signo)

## Alpha

El alfa es una estadístico que indica si la cartera supera al mercado en términos de rentabilidad del riesgo.

- alfa > 0: La cartera supera al mercado en términos de rentabilidad del riesgo.
- alfa < 0: la cartera tiene un rendimiento inferior al del mercado en términos de riesgo-rendimiento.

## Drawdown

El drawdown (reducción) es una medida del riesgo de la estrategia. Una estadística interesante para conocer el rendimiento del algoritmo es el drawdown máximo. En efecto, representa la pérdida máxima de una estrategia durante un período de tiempo que nos permite comprender si la estrategia es arriesgada y, por tanto, elegirla en función de nuestro nivel de aversión al riesgo.

## Scalping Price Action

- Scalping: operación basada en negociaciones a corto plazo
- RSI: el indicador que mide los niveles de sobrecompra y sobreventa

## Librerias
- `pip install yfinance` -> Yahoo Finances
- `pip install mpl_finance` -> Extensión de mpl para representar información financiera
- `pip install ta` -> Indicadores técnicos de finasas

## Environment
- `source env/bin/activate` -> Activar el ambiente
- `alias avenv="source env/bin/activate"` -> Crear un alias para activar el ambiente
- `deactivate` -> Salir del ambiente virtual

## requirements.txt
- `pip3 freeze > requirements.txt` > requirements.txt -> Generar el archivo
- `cat requirements.txt` -> Revisar lo que hay dentro del archivo
- `pip3 install -r requirements.txt` -> Instalar las dependencias necesarias para contribuir más rápido en proyectos

## Other resources
- [How To Build A Trading Bot In Python](https://www.youtube.com/watch?v=WcfKaZL4vpA)
- [Le Doy $100 a Chat GPT Para Que Haga Trading Por Mi](https://www.youtube.com/watch?v=JRYqsG4iUpw)
- [Yahoo Finance](https://es.finance.yahoo.com/)
- [ETF Database](https://etfdb.com/)
- [S&P 500 Map](https://finviz.com/map.ashx)
- [Tipranks](https://www.tipranks.com/)