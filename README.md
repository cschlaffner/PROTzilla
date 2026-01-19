# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       39 |       39 |      0% |      1-70 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                         |      353 |      353 |      0% |     1-715 |
| backend/main/views\_helper.py                                                 |       90 |       63 |     30% |16-23, 27-37, 41-57, 61, 74-97, 115-140, 152-155, 159-160, 176-178, 184 |
| backend/main/views\_settings.py                                               |      194 |      118 |     39% |37-38, 60, 64-79, 85-89, 93-106, 121-122, 133-135, 138-141, 152, 182, 190, 216-217, 228-246, 250-322, 328-347, 353 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |       13 |        0 |    100% |           |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       65 |       32 |     51% |36-55, 57, 59-75, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        7 |     46% |     17-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       36 |        3 |     92% | 82-83, 94 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       57 |        2 |     96% |   43, 134 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       44 |        1 |     98% |       190 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       56 |        9 |     84% |52-53, 60-61, 116-122 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       46 |        1 |     98% |       236 |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py         |       59 |       14 |     76% |17, 63-64, 73-77, 108-110, 132-136 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                      |       33 |        6 |     82% |67-72, 100, 165-170, 179 |
| backend/protzilla/data\_analysis/model\_evaluation.py                         |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                  |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                     |      135 |       10 |     93% |79, 139, 293, 322, 324, 330, 372, 380-381, 396 |
| backend/protzilla/data\_analysis/protein\_coverage.py                         |      166 |        3 |     98% |205, 299, 318 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                             |       41 |        2 |     95% |   103-104 |
| backend/protzilla/data\_analysis/ptm\_quantification/\_\_init\_\_.py          |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_quantification/flexiquant.py            |      201 |        1 |     99% |       125 |
| backend/protzilla/data\_analysis/ptm\_quantification/multiflex.py             |      214 |        9 |     96% |225, 264, 305-309, 356, 626, 689 |
| backend/protzilla/data\_analysis/ptm\_visualization/\_\_init\_\_.py           |        3 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_bar\_plot.py         |       20 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_details\_plot.py     |       34 |        2 |     94% |     50-51 |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_overview\_plot.py    |       25 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_vis\_utils.py        |       49 |        0 |    100% |           |
| backend/protzilla/data\_integration/\_\_init\_\_.py                           |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                  |       58 |       10 |     83% |73, 101-114 |
| backend/protzilla/data\_integration/database\_query.py                        |      129 |       60 |     53% |28-81, 85-87, 91, 114-117, 120-138, 142-146, 150-157, 195-200, 211-214 |
| backend/protzilla/data\_integration/di\_plots.py                              |      123 |       23 |     81% |90-91, 107-108, 174-175, 178-179, 181, 184-185, 213-215, 235-240, 293-294, 297, 370 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                   |      359 |      138 |     62% |25-26, 179-180, 216, 223, 278-282, 330, 395, 398-401, 416-433, 539-540, 557-560, 566-696, 789-790, 799-800, 813-814, 816-817, 819-822, 826-827, 829-832, 842-843, 853-857, 861-862, 874-875, 887-888, 891-892, 902-905 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py             |      147 |       17 |     88% |145-146, 149-150, 157-158, 161-163, 166, 216-218, 408-409, 413, 420 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py           |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                         |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                     |       35 |        2 |     94% |   122-123 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                      |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                           |      132 |        3 |     98% |51-57, 179 |
| backend/protzilla/data\_preprocessing/normalisation.py                        |      122 |        5 |     96% |195-196, 209-210, 342 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       63 |        3 |     95% |185, 202, 265 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                      |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       10 |     90% |207-208, 241, 252, 328-347 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                       |       38 |        3 |     92% |39, 83, 99 |
| backend/protzilla/disk\_operator.py                                           |      275 |       59 |     79% |24-25, 36-37, 39, 57-60, 68-70, 113-115, 130, 152, 157, 174-179, 182-190, 196-214, 243, 297-313, 336-343 |
| backend/protzilla/form.py                                                     |      162 |       26 |     84% |26, 29-31, 111-113, 123-127, 225, 232-233, 238, 241, 277-291 |
| backend/protzilla/form\_helper.py                                             |       21 |       13 |     38% |7, 15-16, 31-34, 40-48, 54-55 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/example\_dataset\_import.py                       |       16 |        9 |     44% |     14-46 |
| backend/protzilla/importing/fasta\_import.py                                  |       25 |        0 |    100% |           |
| backend/protzilla/importing/import\_utils.py                                  |       10 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       74 |       38 |     49% |28, 30, 32, 34, 48, 52-53, 87, 98-108, 113, 119-126, 141-166, 192-217 |
| backend/protzilla/importing/ms\_data\_import.py                               |      135 |       22 |     84% |47-48, 122-124, 164-166, 306-324 |
| backend/protzilla/importing/peptide\_import.py                                |       52 |        7 |     87% |16-17, 27, 63-64, 82-83 |
| backend/protzilla/methods/data\_analysis.py                                   |      677 |      300 |     56% |197, 215, 244-253, 260-265, 327-357, 368-373, 391, 425-453, 464-467, 488, 532-562, 573-579, 600, 644-678, 689-691, 710, 738-746, 753-758, 777, 808-821, 828-830, 868-897, 900-919, 944, 977-1022, 1025-1030, 1041, 1057-1068, 1076-1080, 1095, 1119-1132, 1139-1145, 1189-1215, 1227-1230, 1244, 1258, 1276, 1355-1362, 1370-1372, 1390, 1464-1471, 1479-1481, 1498, 1559-1566, 1574-1576, 1594, 1718-1720, 1738, 1861-1863, 1878, 1891, 1894-1896, 1907, 1962-1964, 1975, 2024-2025, 2030-2033, 2042-2052, 2057-2062, 2065, 2107, 2119-2120, 2150, 2185, 2216-2264, 2273-2298, 2314, 2326-2335, 2340-2343, 2359, 2370-2379, 2384-2387, 2396, 2427, 2434-2437, 2450, 2459, 2485, 2501 |
| backend/protzilla/methods/data\_integration.py                                |      295 |      139 |     53% |95, 102-104, 154-161, 168-180, 192, 267-326, 329-345, 359, 416-441, 444-460, 473, 552-600, 609-615, 630, 708-745, 748-753, 768, 788-790, 795-798, 813, 877-897, 902-908, 921, 978, 998, 1052-1053, 1058-1061, 1074 |
| backend/protzilla/methods/data\_preprocessing.py                              |      210 |       18 |     91% |76, 96-99, 113, 145, 250, 311, 374, 388, 422, 501, 535, 579, 687, 741, 842 |
| backend/protzilla/methods/importing.py                                        |      133 |       30 |     77% |29, 134, 203, 221-222, 235, 250-278, 283-287, 298, 320-323, 340, 356-360, 378, 404 |
| backend/protzilla/run.py                                                      |      208 |       46 |     78% |54-100, 194, 199, 206, 210-213, 220-221, 232-237, 276-278, 314, 341, 355, 363 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |       79 |       11 |     86% |87, 113-121, 129-131, 145-146 |
| backend/protzilla/stepfactory.py                                              |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                    |      381 |       81 |     79% |116, 143, 146, 162, 188, 199, 202, 216, 219-221, 250, 276, 299-304, 355-357, 367, 378, 385, 393, 400, 403, 434, 458-459, 481, 491-504, 532, 544, 546-558, 579-594, 605, 661-663, 667-675, 691, 703, 705-712, 717, 758-760, 789, 808-811, 818-821 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      376 |       83 |     78% |97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 315-318, 383-384, 386-387, 402-403, 405-406, 486, 503, 696, 698, 728-735, 744-757, 930-942, 945-957, 983-999, 1013-1029 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |        0 |    100% |           |
| backend/protzilla/utilities/utilities.py                                      |       57 |        9 |     84% |31-32, 75, 86, 104, 139-142 |
| backend/protzilla/workflow.py                                                 |       11 |        6 |     45% |  6, 15-20 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       24 |        5 |     79% | 60-63, 67 |
| **TOTAL**                                                                     | **6916** | **1913** | **72%** |           |


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