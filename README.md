# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       39 |       39 |      0% |      1-70 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                         |      389 |      389 |      0% |     1-798 |
| backend/main/views\_helper.py                                                 |       90 |       63 |     30% |16-23, 27-37, 41-57, 61, 74-97, 115-140, 152-155, 159-160, 176-178, 184 |
| backend/main/views\_settings.py                                               |      194 |      118 |     39% |37-38, 60, 64-79, 85-89, 93-106, 121-122, 133-135, 138-141, 152, 182, 190, 216-217, 228-246, 250-322, 328-347, 353 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |       13 |        0 |    100% |           |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       65 |       32 |     51% |36-55, 57, 59-75, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        7 |     46% |     17-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       40 |        1 |     98% |       118 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       60 |        3 |     95% |34, 46, 137 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       47 |        1 |     98% |       190 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       59 |        7 |     88% |52-53, 60-61, 116-117, 122 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       50 |        0 |    100% |           |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py         |       75 |       11 |     85% |23, 74-75, 84-88, 144-148 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                      |       28 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation.py                         |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                  |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                     |      136 |       10 |     93% |151, 329, 343, 372, 374, 380, 422, 430-431, 446 |
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
| backend/protzilla/data\_integration/di\_plots.py                              |      123 |       21 |     83% |90-91, 174-175, 178-179, 181, 184-185, 213-215, 235-240, 293-294, 297, 370 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                   |      361 |      138 |     62% |25-26, 185-186, 222, 229, 284-288, 336, 401, 404-407, 422-439, 545-546, 558-561, 567-697, 785-786, 795-796, 809-810, 812-813, 815-818, 822-823, 825-828, 838-839, 849-853, 857-858, 870-871, 883-884, 887-888, 898-901 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py             |      146 |       17 |     88% |144-145, 148-149, 156-157, 160-162, 165, 215-217, 407-408, 412, 419 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py           |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                         |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                     |       35 |        2 |     94% |   122-123 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                      |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                           |      132 |        3 |     98% |51-57, 179 |
| backend/protzilla/data\_preprocessing/normalisation.py                        |      143 |        6 |     96% |203-207, 222, 235-236, 389 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       63 |        3 |     95% |185, 202, 265 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                      |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       10 |     90% |207-208, 241, 252, 328-347 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                       |       38 |        3 |     92% |39, 83, 99 |
| backend/protzilla/disk\_operator.py                                           |      275 |       59 |     79% |24-25, 36-37, 39, 57-60, 68-70, 113-115, 130, 152, 157, 174-179, 182-190, 196-214, 243, 297-313, 336-343 |
| backend/protzilla/form.py                                                     |      166 |       26 |     84% |26, 29-31, 117-119, 129-133, 231, 238-239, 244, 247, 283-297 |
| backend/protzilla/form\_helper.py                                             |       21 |       13 |     38% |7, 15-16, 31-34, 40-48, 54-55 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/example\_dataset\_import.py                       |       16 |        9 |     44% |     14-46 |
| backend/protzilla/importing/fasta\_import.py                                  |       25 |        0 |    100% |           |
| backend/protzilla/importing/import\_utils.py                                  |       10 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       74 |       38 |     49% |28, 30, 32, 34, 48, 52-53, 87, 98-108, 113, 119-126, 141-166, 192-217 |
| backend/protzilla/importing/ms\_data\_import.py                               |      135 |       22 |     84% |47-48, 122-124, 164-166, 306-324 |
| backend/protzilla/importing/peptide\_import.py                                |       75 |       22 |     71% |26, 41-42, 59-60, 73-84, 110-114, 128-129 |
| backend/protzilla/methods/data\_analysis.py                                   |      686 |      295 |     57% |197, 215, 244-253, 260-265, 344-374, 408, 442-470, 481-484, 505, 549-579, 590-596, 617, 661-695, 706-708, 727, 755-763, 770-775, 794, 825-838, 845-847, 885-914, 933-934, 961, 994-1039, 1042-1047, 1058, 1078-1095, 1103-1107, 1122, 1183-1214, 1220-1234, 1278-1304, 1333, 1347, 1365, 1444-1451, 1459-1461, 1479, 1553-1560, 1568-1570, 1587, 1648-1655, 1663-1665, 1683, 1807-1809, 1827, 1950-1952, 1967, 1980, 1983-1985, 1996, 2060-2062, 2073, 2126-2127, 2132-2135, 2144-2154, 2159-2164, 2167, 2209, 2221-2222, 2252, 2287, 2318-2366, 2375-2400, 2416, 2428-2437, 2442-2445, 2461, 2472-2481, 2486-2489, 2498, 2529, 2536-2539, 2552, 2561, 2587, 2603 |
| backend/protzilla/methods/data\_integration.py                                |      295 |      132 |     55% |95, 102-104, 154-161, 175, 192, 267-326, 329-345, 359, 416-441, 444-460, 473, 552-600, 609-615, 630, 708-745, 748-753, 768, 788-790, 795-798, 813, 877-897, 921, 978, 998, 1052-1053, 1058-1061, 1074 |
| backend/protzilla/methods/data\_preprocessing.py                              |      214 |       20 |     91% |77, 97-100, 114, 146, 176-177, 255, 316, 379, 393, 427, 506, 540, 584, 692, 746, 847 |
| backend/protzilla/methods/importing.py                                        |      133 |       29 |     78% |29, 203, 221-222, 235, 250-278, 283-287, 298, 320-323, 340, 356-360, 378, 404 |
| backend/protzilla/run.py                                                      |      208 |       46 |     78% |54-100, 194, 199, 206, 210-213, 220-221, 232-237, 276-278, 314, 341, 355, 363 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |       80 |        7 |     91% |113-121, 145-146 |
| backend/protzilla/stepfactory.py                                              |       15 |        2 |     87% |    21, 35 |
| backend/protzilla/steps.py                                                    |      383 |       67 |     83% |116, 143, 146, 162, 188, 199, 202, 216, 250, 276, 299-304, 367, 378, 385, 393, 400, 403, 437, 461-462, 484, 494-507, 535, 547, 549-561, 597, 608, 670-678, 694, 706, 708-715, 720, 761-763, 792, 811-814, 821-824 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      401 |       80 |     80% |107, 109, 116, 161-162, 164, 166, 201, 215, 219, 223, 227, 237, 241-246, 254, 256, 258, 278, 283, 285, 328-331, 396-397, 399-400, 415-416, 418-419, 499, 516, 566, 576, 744, 746, 776-783, 792-805, 981-993, 996-1008, 1034-1050, 1064-1080 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |        0 |    100% |           |
| backend/protzilla/utilities/utilities.py                                      |       59 |        8 |     86% |31-32, 75, 86, 139-142 |
| backend/protzilla/workflow.py                                                 |       11 |        6 |     45% |  6, 15-20 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       24 |        5 |     79% | 60-63, 67 |
| **TOTAL**                                                                     | **7073** | **1916** | **73%** |           |


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