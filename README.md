# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       36 |       36 |      0% |      1-67 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                         |      352 |      352 |      0% |     1-715 |
| backend/main/views\_helper.py                                                 |       78 |       64 |     18% |11-17, 21-29, 32-49, 51-62, 66-69, 78-106, 124-144, 147-169 |
| backend/main/views\_settings.py                                               |      139 |      139 |      0% |     1-230 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |        7 |        0 |    100% |           |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       65 |       35 |     46% |36-55, 57, 59-67, 99, 207, 237-239, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        8 |     38% |     16-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       37 |       11 |     70% |1, 5, 73, 88-91, 101, 104-107, 117 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       48 |       11 |     77% |43, 98-101, 125, 132-135, 143-153 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       46 |        9 |     80% |178, 184, 189-191, 196-197, 226-230 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       56 |        9 |     84% |52-53, 60-61, 116-122 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       46 |       11 |     76% |96-131, 157, 202, 208, 211-212, 233, 262-272 |
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
| backend/protzilla/data\_integration/database\_query.py                        |      129 |       81 |     37% |28-81, 85-87, 91, 114, 119-127, 132-149, 151-160, 182, 185-190, 199, 201-202, 217-218, 229-237, 256, 261, 264-273 |
| backend/protzilla/data\_integration/di\_plots.py                              |      123 |       52 |     58% |47, 57, 60, 64, 69, 76, 81-83, 87, 90-92, 95, 106-107, 123, 168-170, 174-178, 180, 183-189, 213-217, 235-239, 283-285, 289, 293-296, 299-300, 305, 326-327, 357-359, 386-387 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                   |      359 |      141 |     61% |25-26, 179-180, 216, 223, 278-282, 330, 395, 398-401, 416-433, 539-540, 557-560, 566-690, 703-705, 782, 790-795, 800, 803, 811, 813-817, 820-821, 824-827, 831, 838, 842, 845-847, 853-854, 888, 891, 894, 899-906 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py             |      147 |       31 |     79% |145-146, 149-150, 157-158, 161-163, 166, 216-218, 386, 391, 395-397, 404, 407-409, 412, 417-422, 430, 438, 454, 476, 496 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py           |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                         |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                     |       19 |        2 |     89% |     59-60 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                      |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                           |      131 |       45 |     66% |47-53, 85-86, 91, 95, 124-125, 129, 132, 136-137, 167-168, 175-178, 204-205, 209, 220, 246-247, 282, 285, 288, 291, 294, 297, 308-312, 315-319, 322, 325, 328, 341-345, 458-459, 482-483, 495 |
| backend/protzilla/data\_preprocessing/normalisation.py                        |       98 |       27 |     72% |14, 36, 42, 49, 79, 84, 88, 92, 98, 107, 109, 119, 142, 146, 150, 156, 163, 165-167, 171, 201, 212, 220, 227-229, 279, 290 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       63 |        3 |     95% |185, 202, 265 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                      |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       25 |     75% |17, 73, 140, 154, 158-159, 200, 203, 206-207, 210, 221, 239-240, 250-251, 257, 298, 328-350 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                       |       24 |        7 |     71% |11, 35, 41-43, 63, 73 |
| backend/protzilla/disk\_operator.py                                           |      266 |       48 |     82% |23-24, 35-36, 38, 56-59, 112-114, 129, 151, 156, 173-178, 181-189, 195-213, 242, 246, 294-297, 320-323 |
| backend/protzilla/form.py                                                     |      146 |       34 |     77% |101, 111-115, 179-181, 185, 188-191, 194-207, 210, 218, 228, 231-254 |
| backend/protzilla/form\_helper.py                                             |       13 |        6 |     54% |7, 15-16, 28-29, 33 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       72 |       38 |     47% |28, 30, 32, 34, 48, 52-53, 74, 85-95, 100, 106-113, 128-153, 179-204 |
| backend/protzilla/importing/ms\_data\_import.py                               |      121 |       61 |     50% |29, 31-33, 83, 93-95, 105, 110-111, 123-126, 134, 153, 189, 215, 240-300 |
| backend/protzilla/importing/peptide\_import.py                                |       45 |       11 |     76% |17-18, 55-56, 74-75, 97-99, 102, 112-114 |
| backend/protzilla/methods/data\_analysis.py                                   |      605 |      376 |     38% |53, 62, 67, 74, 79, 81, 86, 100, 105-106, 117, 121-122, 128-129, 135-136, 143-144, 150-151, 159, 166-167, 174-175, 181-182, 187-189, 194-214, 243-248, 252-257, 264-271, 326-348, 365, 372-390, 424-444, 465-487, 531-553, 570, 577-599, 643-669, 689-696, 702-709, 737-739, 741, 745-750, 756-763, 769-776, 804-807, 817, 825-830, 863-885, 890-908, 915-927, 943-945, 955, 967-978, 1002-1006, 1014, 1046-1064, 1088, 1092-1094, 1100-1102, 1106-1108, 1114-1121, 1131-1133, 1213, 1215-1220, 1230-1232, 1308-1314, 1319-1325, 1387, 1389-1395, 1406, 1531, 1533-1539, 1550, 1674, 1676, 1680, 1682-1690, 1707, 1709-1719, 1775, 1777-1787, 1836-1838, 1846-1862, 1892, 1897, 1899-1907, 1921-1922, 1924-1934, 1939-1955, 1980-1981, 1995-1997, 2009, 2019, 2021-2022, 2038-2040, 2067-2075, 2106-2141, 2155-2180, 2189, 2193-2194, 2200-2204, 2215-2216, 2224-2225, 2233, 2237-2238, 2244-2248, 2259-2260, 2268-2277 |
| backend/protzilla/methods/data\_integration.py                                |      295 |      186 |     37% |30, 40-41, 46, 53, 58, 63-64, 69, 74, 79, 86, 90, 94, 99-103, 110, 118, 165, 168-179, 189-202, 277-320, 332-345, 356-359, 361-369, 426-447, 452-467, 475, 477-483, 562-619, 625-626, 634-758, 764-769, 774-778, 798, 801-809, 813-817, 823, 839-844, 891, 898-912, 919-925, 988, 1009, 1063-1068, 1072-1076 |
| backend/protzilla/methods/data\_preprocessing.py                              |      209 |       93 |     56% |26-27, 32, 37-38, 42-43, 47-48, 53, 58-59, 63-64, 68, 80-81, 90, 120, 124-130, 156-162, 194, 224, 257, 261-267, 292, 318, 322-328, 344, 381-389, 415-423, 449, 494-502, 539-547, 593, 601, 647-655, 701, 703-709, 750-751, 802-810, 864-865 |
| backend/protzilla/methods/importing.py                                        |      137 |       76 |     45% |22, 34-35, 39-44, 49, 53, 55, 59, 64, 67-69, 72-77, 116, 149, 153-161, 189, 197, 218, 220-230, 249-250, 254-262, 277-294, 302-306, 311, 315-325, 347-351, 365-375, 391-400 |
| backend/protzilla/run.py                                                      |      208 |       93 |     55% |22-23, 31-78, 95, 100-103, 110, 116, 119-120, 136, 139, 151, 161, 163, 166, 171, 176, 182-188, 190-191, 194-197, 205-206, 210, 215-220, 232-236, 241, 255-257, 264-265, 277-278, 298, 307, 312, 316, 322, 326, 330, 334, 337, 343-367 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |       79 |        7 |     91% |111-119, 143-144 |
| backend/protzilla/stepfactory.py                                              |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                    |      381 |       66 |     83% |116, 142-143, 146, 162, 188, 199, 202, 216, 219-221, 250, 276, 298-303, 354-356, 366, 377, 384, 392, 399, 402, 433, 457-458, 480, 490-503, 531, 543, 557, 593, 604, 666-674, 690, 702, 704-711, 716, 757-759, 788, 807-810, 817-820 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      375 |       99 |     74% |82, 97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 277-296, 315-318, 331, 383-384, 386-387, 402-403, 405-406, 486, 503, 523, 696, 698, 728-735, 744-757, 767-771, 929-941, 944-956, 982-998, 1012-1028 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |       11 |     56% |23-44, 60-79, 83, 101, 104 |
| backend/protzilla/utilities/utilities.py                                      |       56 |        9 |     84% |29-30, 71, 82, 100, 135-138 |
| backend/protzilla/workflow.py                                                 |       11 |        7 |     36% |  6, 14-20 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       24 |        5 |     79% | 60-63, 67 |
|                                                                     **TOTAL** | **6705** | **2472** | **63%** |           |


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