# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       36 |       36 |      0% |      1-67 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                         |      352 |      352 |      0% |     1-715 |
| backend/main/views\_helper.py                                                 |       78 |       60 |     23% |11-18, 22-32, 36-52, 70, 83-106, 124-149, 161-164, 168-169 |
| backend/main/views\_settings.py                                               |      139 |      139 |      0% |     1-230 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |        7 |        0 |    100% |           |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       65 |       32 |     51% |36-55, 57, 59-75, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        7 |     46% |     17-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       37 |       10 |     73% |1, 5, 71-76, 86, 91, 101, 104-107 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       48 |        2 |     96% |   43, 104 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       46 |        1 |     98% |       199 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       56 |        9 |     84% |52-53, 60-61, 116-122 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       46 |        1 |     98% |       236 |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py         |       53 |       11 |     79% |17, 63-64, 73-77, 124-128 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                      |       33 |        6 |     82% |67-72, 100, 165-170, 179 |
| backend/protzilla/data\_analysis/model\_evaluation.py                         |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                  |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                     |      131 |        9 |     93% |79, 139, 289, 320, 326, 368, 376-377, 392 |
| backend/protzilla/data\_analysis/protein\_graphs.py                           |      412 |       37 |     91% |32-40, 157, 163-166, 169-172, 177, 209-210, 224, 297-299, 308-310, 328-329, 378, 404-408, 452, 466, 535, 566, 573, 774, 836-839 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                             |       41 |        2 |     95% |   103-104 |
| backend/protzilla/data\_analysis/ptm\_quantification/\_\_init\_\_.py          |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_quantification/flexiquant.py            |      201 |        1 |     99% |       125 |
| backend/protzilla/data\_analysis/ptm\_quantification/multiflex.py             |      214 |        9 |     96% |225, 264, 305-309, 356, 626, 689 |
| backend/protzilla/data\_integration/\_\_init\_\_.py                           |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                  |       58 |       10 |     83% |73, 101-114 |
| backend/protzilla/data\_integration/database\_query.py                        |      129 |       60 |     53% |28-81, 85-87, 91, 114-117, 120-138, 142-146, 150-157, 195-200, 211-214 |
| backend/protzilla/data\_integration/di\_plots.py                              |      123 |       49 |     60% |47, 57, 60, 64, 69, 76, 81-83, 87, 90-92, 95, 106-107, 121-123, 168, 172, 174-176, 178-179, 182, 184-189, 192, 212-216, 234-239, 283, 287, 291, 293-295, 298, 303-305, 308, 325, 357, 371, 385 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                   |      359 |      138 |     62% |25-26, 179-180, 216, 223, 278-282, 330, 395, 398-401, 416-433, 539-540, 557-560, 566-696, 789-790, 799-800, 813-814, 816-817, 819-822, 826-827, 829-832, 842-843, 853-857, 861-862, 874-875, 887-888, 891-892, 902-905 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py             |      147 |       17 |     88% |145-146, 149-150, 157-158, 161-163, 166, 216-218, 408-409, 413, 420 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py           |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                         |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                     |       19 |        2 |     89% |     59-60 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                      |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                           |      131 |        3 |     98% |47-53, 175 |
| backend/protzilla/data\_preprocessing/normalisation.py                        |       98 |        1 |     99% |       280 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       63 |        3 |     95% |185, 202, 265 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                      |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       10 |     90% |207-208, 241, 252, 328-347 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                       |       24 |        2 |     92% |    48, 64 |
| backend/protzilla/disk\_operator.py                                           |      266 |       48 |     82% |23-24, 35-36, 38, 56-59, 112-114, 129, 151, 156, 173-178, 181-189, 195-213, 242, 246, 294-297, 320-323 |
| backend/protzilla/form.py                                                     |      146 |       34 |     77% |101, 111-115, 179-181, 185, 188-191, 194-207, 210, 218, 228, 231-254 |
| backend/protzilla/form\_helper.py                                             |       13 |        6 |     54% |7, 15-16, 28-29, 33 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       72 |       38 |     47% |28, 30, 32, 34, 48, 52-53, 74, 85-95, 100, 106-113, 128-153, 179-204 |
| backend/protzilla/importing/ms\_data\_import.py                               |      121 |       22 |     82% |34-35, 110-112, 152-154, 282-300 |
| backend/protzilla/importing/peptide\_import.py                                |       45 |        6 |     87% |17-18, 55-56, 74-75 |
| backend/protzilla/methods/data\_analysis.py                                   |      605 |      391 |     35% |53, 62, 67, 74, 79, 81, 86, 100, 105-106, 117, 121-122, 128-129, 135-136, 143-144, 150-151, 159, 166-167, 174-175, 181-182, 187-189, 194-214, 243-248, 252-257, 264-271, 326-348, 365, 372-390, 424-444, 465-487, 531-553, 570, 577-599, 643-669, 689-696, 702-709, 737-739, 741, 745-750, 756-763, 769-776, 804-807, 817, 825-830, 863-882, 886, 890-907, 914, 920-927, 943-945, 955, 966-978, 1001-1002, 1013, 1046-1064, 1085, 1091-1094, 1100, 1105-1108, 1116-1120, 1122-1133, 1212, 1214-1219, 1221-1232, 1307-1308, 1312-1314, 1319-1325, 1386, 1388-1406, 1530, 1532-1550, 1673, 1675, 1679, 1681-1690, 1706, 1708, 1712-1719, 1774, 1776, 1780-1787, 1836-1838, 1846-1851, 1854-1862, 1891, 1898-1907, 1919-1921, 1923-1942, 1947-1955, 1979-1981, 1988-1997, 2020-2022, 2038-2040, 2066-2075, 2106-2141, 2154-2180, 2189-2193, 2195-2204, 2215-2225, 2233-2237, 2239-2248, 2259-2277 |
| backend/protzilla/methods/data\_integration.py                                |      295 |      200 |     32% |43, 48-49, 56-57, 61-62, 66, 71, 76, 81, 85-90, 95, 102-106, 113, 121, 164, 166-179, 194-202, 277-320, 332-340, 352, 356-369, 426-442, 447-455, 467, 471-483, 562-602, 611-619, 631-640, 718-745, 748-756, 769-778, 798-799, 805, 809, 813-823, 842, 887-898, 903-910, 919-931, 999-1008, 1062-1063, 1068, 1072-1085 |
| backend/protzilla/methods/data\_preprocessing.py                              |      209 |       93 |     56% |26-27, 32, 37-38, 42-43, 47-48, 53, 58-59, 63-64, 68, 80-81, 90, 120, 124-130, 156-162, 194, 224, 257, 261-267, 292, 318, 322-328, 344, 381-389, 415-423, 449, 494-502, 539-547, 593, 601, 647-655, 701, 703-709, 750-751, 802-810, 864-865 |
| backend/protzilla/methods/importing.py                                        |      137 |       69 |     50% |22, 34-35, 39-44, 49, 53, 55, 59, 64, 67-69, 72-77, 116, 153, 155-161, 189, 199, 220, 224-230, 254, 256-262, 277-296, 305-310, 315, 319-325, 347-353, 365, 369-375, 391-400 |
| backend/protzilla/run.py                                                      |      208 |       48 |     77% |22-23, 54-100, 194, 199, 206, 210-213, 220-221, 232-237, 276-278, 314, 341, 355, 363 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |       79 |        7 |     91% |111-119, 143-144 |
| backend/protzilla/stepfactory.py                                              |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                    |      381 |       66 |     83% |116, 142-143, 146, 162, 188, 199, 202, 216, 219-221, 250, 276, 298-303, 354-356, 366, 377, 384, 392, 399, 402, 433, 457-458, 480, 490-503, 531, 543, 557, 593, 604, 666-674, 690, 702, 704-711, 716, 757-759, 788, 807-810, 817-820 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      375 |       99 |     74% |82, 97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 277-296, 315-318, 331, 383-384, 386-387, 402-403, 405-406, 486, 503, 523, 696, 698, 728-735, 744-757, 767-771, 929-941, 944-956, 982-998, 1012-1028 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |        0 |    100% |           |
| backend/protzilla/utilities/utilities.py                                      |       56 |        9 |     84% |29-30, 71, 82, 100, 135-138 |
| backend/protzilla/workflow.py                                                 |       11 |        6 |     45% |  6, 15-20 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       24 |        5 |     79% | 60-63, 67 |
|                                                                     **TOTAL** | **6705** | **2228** | **67%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://github.com/cschlaffner/PROTzilla/raw/python-coverage-comment-action-data/badge.svg)](https://github.com/cschlaffner/PROTzilla/tree/python-coverage-comment-action-data)

This is the one to use if your repository is private or if you don't want to customize anything.



## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.