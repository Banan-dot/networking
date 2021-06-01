## Скрипт для трассировки автономных систем
___
### Пример запуска
```cmd
>>> python main.py 8.8.8.8
```
___
### Пример вывода
```
Трассировка маршрута к dns.google [8.8.8.8]

+----+----------------+---------+------------------+----------------+
| #  |       IP       |    AS   | COUNTRY || CITY  |    PROVIDER    |
+----+----------------+---------+------------------+----------------+
| 1  |  192.168.0.1   |    *    |       * *        |       *        |
| 2  |  128.75.32.1   |  AS3253 | RU Yekaterinburg | PJSC Vimpelcom |
| 3  |  195.58.0.166  |  AS3253 | RU Yekaterinburg | PJSC Vimpelcom |
| 4  | 194.186.175.65 |  AS3216 | RU Yekaterinburg | PJSC Vimpelcom |
| 5  | 79.104.235.213 |    *    |    RU Moscow     |       *        |
| 6  | 72.14.213.116  | AS15169 | US Mountain View |   Google LLC   |
| 7  | 108.170.250.34 | AS15169 | US New York City |   Google LLC   |
| 8  | 172.253.66.116 | AS15169 | US Mountain View |   Google LLC   |
| 9  |  72.14.235.69  | AS15169 | US Mountain View |   Google LLC   |
| 10 |  216.239.49.3  | AS15169 |    US Bolivar    |   Google LLC   |
+----+----------------+---------+------------------+----------------+
```
