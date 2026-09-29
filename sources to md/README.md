# Algorithmic Game Theory — постраничный Markdown-архив

Источник: Nisan et al., *Algorithmic Game Theory*, файл [Nisan-et-al-AGT-book.pdf](../materials/sources/Nisan-et-al-AGT-book.pdf). Здесь сохранены **все 775 страниц**: вводные материалы, четыре части, 29 глав и предметный указатель. Книжная нумерация после вводных страниц равна номеру страницы PDF минус 21.

Контрольная сумма исходного PDF (SHA-256): `83084d9996024ca92f313c5ae55fec7b3b379f06172a4c24b62229da9c558543`.

## Как читать

- [Вся книга одним большим Markdown-файлом](00_full_book.md). Для быстрого просмотра удобнее файлы глав ниже.
- [Теоремы, определения, леммы и другие формальные утверждения](KEY_STATEMENTS.md) (489 фрагментов исходных страниц).
- [Рисунки и таблицы](FIGURES.md) (69 фрагментов исходных страниц).
- Текст под каждой страницей можно искать и копировать. Он получен автоматически; математические шрифты PDF местами не имеют однозначного Unicode-соответствия. Такие знаки встречаются на 321 страницах и показаны как `⟦U+0001; см. снимок страницы⟧` и подобные маркеры. В указателе и других многоколоночных местах порядок извлечённых строк также может отличаться от порядка чтения. **Не используйте поисковый слой как источник точной формулы**: сверяйте её с изображением страницы.
- Фрагмент под заголовком формального утверждения помогает быстро найти его; если текст продолжается ниже или на следующей странице, откройте полный снимок. Дополнительный фрагмент следующей страницы не означает, что утверждение непременно продолжается.
- Для повторной сборки запустите [build_book.py](build_book.py) с PyMuPDF и Pillow. Скрипт и изображения сохранены вместе с Markdown.

## Содержание

| Раздел | PDF-страницы | Файл |
|---|---:|---|
| Вводные страницы | 1–21 | [Открыть](chapters/00_front_matter.md) |
| Часть 1. Computing in Games | 22–23 | [Открыть](chapters/part_01.md) |
| 1. Basic Solution Concepts and Computational Issues | 24–49 | [Открыть](chapters/01_basic-solution-concepts-and-computational-issues.md) |
| 2. The Complexity of Finding Nash Equilibria | 50–73 | [Открыть](chapters/02_the-complexity-of-finding-nash-equilibria.md) |
| 3. Equilibrium Computation for Two-Player Games in Strategic and Extensive Form | 74–99 | [Открыть](chapters/03_equilibrium-computation-for-two-player-games-in-strategic-and-extensive-form.md) |
| 4. Learning, Regret Minimization, and Equilibria | 100–123 | [Открыть](chapters/04_learning-regret-minimization-and-equilibria.md) |
| 5. Combinatorial Algorithms for Market Equilibria | 124–155 | [Открыть](chapters/05_combinatorial-algorithms-for-market-equilibria.md) |
| 6. Computation of Market Equilibria by Convex Programming | 156–179 | [Открыть](chapters/06_computation-of-market-equilibria-by-convex-programming.md) |
| 7. Graphical Games | 180–201 | [Открыть](chapters/07_graphical-games.md) |
| 8. Cryptography and Game Theory | 202–227 | [Открыть](chapters/08_cryptography-and-game-theory.md) |
| Часть 2. Algorithmic Mechanism Design | 228–229 | [Открыть](chapters/part_02.md) |
| 9. Introduction to Mechanism Design (for Computer Scientists) | 230–263 | [Открыть](chapters/09_introduction-to-mechanism-design-for-computer-scientists.md) |
| 10. Mechanism Design without Money | 264–287 | [Открыть](chapters/10_mechanism-design-without-money.md) |
| 11. Combinatorial Auctions | 288–321 | [Открыть](chapters/11_combinatorial-auctions.md) |
| 12. Computationally Efficient Approximation Mechanisms | 322–351 | [Открыть](chapters/12_computationally-efficient-approximation-mechanisms.md) |
| 13. Profit Maximization in Mechanism Design | 352–383 | [Открыть](chapters/13_profit-maximization-in-mechanism-design.md) |
| 14. Distributed Algorithmic Mechanism Design | 384–405 | [Открыть](chapters/14_distributed-algorithmic-mechanism-design.md) |
| 15. Cost Sharing | 406–431 | [Открыть](chapters/15_cost-sharing.md) |
| 16. Online Mechanisms | 432–461 | [Открыть](chapters/16_online-mechanisms.md) |
| Часть 3. Quantifying the Inefficiency of Equilibria | 462–463 | [Открыть](chapters/part_03.md) |
| 17. Introduction to the Inefficiency of Equilibria | 464–481 | [Открыть](chapters/17_introduction-to-the-inefficiency-of-equilibria.md) |
| 18. Routing Games | 482–507 | [Открыть](chapters/18_routing-games.md) |
| 19. Network Formation Games and the Potential Function Method | 508–537 | [Открыть](chapters/19_network-formation-games-and-the-potential-function-method.md) |
| 20. Selfish Load Balancing | 538–563 | [Открыть](chapters/20_selfish-load-balancing.md) |
| 21. The Price of Anarchy and the Design of Scalable Resource Allocation Mechanisms | 564–589 | [Открыть](chapters/21_the-price-of-anarchy-and-the-design-of-scalable-resource-allocation-mechanisms.md) |
| Часть 4. Additional Topics | 590–591 | [Открыть](chapters/part_04.md) |
| 22. Incentives and Pricing in Communications Networks | 592–613 | [Открыть](chapters/22_incentives-and-pricing-in-communications-networks.md) |
| 23. Incentives in Peer-to-Peer Systems | 614–633 | [Открыть](chapters/23_incentives-in-peer-to-peer-systems.md) |
| 24. Cascading Behavior in Networks: Algorithmic and Economic Issues | 634–653 | [Открыть](chapters/24_cascading-behavior-in-networks-algorithmic-and-economic-issues.md) |
| 25. Incentives and Information Security | 654–671 | [Открыть](chapters/25_incentives-and-information-security.md) |
| 26. Computational Aspects of Prediction Markets | 672–697 | [Открыть](chapters/26_computational-aspects-of-prediction-markets.md) |
| 27. Manipulation-Resistant Reputation Systems | 698–719 | [Открыть](chapters/27_manipulation-resistant-reputation-systems.md) |
| 28. Sponsored Search Auctions | 720–737 | [Открыть](chapters/28_sponsored-search-auctions.md) |
| 29. Computational Evolutionary Game Theory | 738–757 | [Открыть](chapters/29_computational-evolutionary-game-theory.md) |
| Предметный указатель | 758–775 | [Открыть](chapters/30_index.md) |

Этот архив сохраняет **содержание исходных страниц**, а не выдаёт автоматическое распознавание формул за проверенную TeX-транскрипцию. Скриншоты утверждений представляют оригинал учебника, а не перерисованную схему.
