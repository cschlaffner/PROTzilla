# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       39 |       39 |      0% |      1-70 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                         |      425 |      425 |      0% |     1-905 |
| backend/main/views\_helper.py                                                 |       86 |       57 |     34% |17-24, 28-38, 42-58, 63, 83-89, 107-132, 144-147, 151-152, 168, 176 |
| backend/main/views\_settings.py                                               |      194 |      118 |     39% |37-38, 60, 64-79, 85-89, 93-106, 121-122, 133-135, 138-141, 152, 182, 190, 216-217, 228-246, 250-322, 328-347, 353 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |       17 |        1 |     94% |       113 |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       78 |       45 |     42% |39-58, 60, 62-78, 345-428 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       85 |       20 |     76% |44, 62-65, 79, 89-90, 112-123, 140, 175-178 |
| backend/protzilla/data\_analysis/clustering.py                                |       70 |       11 |     84% |153, 393-410, 414-418 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        7 |     46% |     17-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       38 |        1 |     97% |       106 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       60 |        3 |     95% |34, 46, 137 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       48 |        1 |     98% |       185 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       60 |        7 |     88% |54-55, 62-63, 126-127, 132 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       52 |        0 |    100% |           |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py         |       76 |       11 |     86% |28, 77-78, 87-91, 151-155 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                      |       30 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation.py                         |        8 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                  |       14 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                     |      163 |        9 |     94% |137-138, 142, 363, 394, 396, 402, 453, 468 |
| backend/protzilla/data\_analysis/protein\_coverage.py                         |      166 |        3 |     98% |205, 299, 318 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                             |       34 |        2 |     94% |     67-68 |
| backend/protzilla/data\_analysis/ptm\_quantification/\_\_init\_\_.py          |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_quantification/flexiquant.py            |      201 |        1 |     99% |       125 |
| backend/protzilla/data\_analysis/ptm\_quantification/multiflex.py             |      214 |        9 |     96% |225, 264, 305-309, 356, 626, 689 |
| backend/protzilla/data\_analysis/ptm\_visualization/\_\_init\_\_.py           |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_bar\_plot.py         |       20 |        1 |     95% |        23 |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_details\_plot.py     |       34 |        3 |     91% | 50-51, 58 |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_overview\_plot.py    |       25 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_vis\_utils.py        |       49 |        1 |     98% |       144 |
| backend/protzilla/data\_integration/\_\_init\_\_.py                           |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                  |       58 |       10 |     83% |75, 103-116 |
| backend/protzilla/data\_integration/database\_query.py                        |      129 |       60 |     53% |28-81, 85-87, 91, 114-117, 120-138, 142-146, 150-157, 195-200, 211-214 |
| backend/protzilla/data\_integration/di\_plots.py                              |      125 |       21 |     83% |87-88, 174-175, 178-179, 181, 184-185, 211-213, 231-236, 289-290, 293, 365 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                   |      363 |      139 |     62% |25-26, 183-184, 220, 227, 282-286, 334, 399, 402-405, 420-437, 444, 553-554, 566-569, 575-705, 793-794, 803-804, 817-818, 820-821, 823-826, 830-831, 833-836, 846-847, 857-861, 865-866, 878-879, 891-892, 895-896, 906-909 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py             |      146 |       17 |     88% |143-144, 147-148, 155-156, 159-161, 164, 214-216, 406-407, 411, 418 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py           |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                         |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_peptides\_or\_psm.py            |       48 |       11 |     77% |40-41, 61-62, 73, 101, 132, 140-148, 154, 160 |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                     |       32 |        2 |     94% |   111-112 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                      |       38 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                           |      132 |        3 |     98% |52-58, 178 |
| backend/protzilla/data\_preprocessing/normalisation.py                        |      141 |        5 |     96% |203, 217, 230-231, 379 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       55 |        3 |     95% |142, 163, 207 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       10 |     90% |207-208, 241, 252, 328-347 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/simplification.py                       |       18 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/transformation.py                       |       38 |        4 |     89% |42, 69-70, 100 |
| backend/protzilla/disk\_operator.py                                           |      366 |      106 |     71% |34-35, 47, 49, 64-65, 85-88, 96-98, 111-113, 117-120, 132-137, 141-146, 209, 233, 238, 255-260, 263-271, 277-303, 331-339, 345, 409-430, 459-466, 471-477, 489-496, 539, 547 |
| backend/protzilla/form.py                                                     |      176 |       20 |     89% |36-38, 138, 140, 238-241, 247, 263, 299-313 |
| backend/protzilla/form\_helper.py                                             |       21 |        3 |     86% |25, 40, 60 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/debug\_import.py                                  |        6 |        1 |     83% |        11 |
| backend/protzilla/importing/example\_dataset\_import.py                       |       54 |       25 |     54% |     24-66 |
| backend/protzilla/importing/fasta\_import.py                                  |       26 |        0 |    100% |           |
| backend/protzilla/importing/import\_utils.py                                  |       10 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       60 |       26 |     57% |27, 29, 31, 33, 47, 51-52, 71, 85, 96-106, 111, 135-158 |
| backend/protzilla/importing/ms\_data\_import.py                               |      136 |       20 |     85% |123-125, 165-167, 309-327 |
| backend/protzilla/importing/peptide\_import.py                                |       90 |       24 |     73% |54-55, 72-73, 86-97, 127-131, 224-228 |
| backend/protzilla/methods/data\_analysis.py                                   |      625 |      188 |     70% |252-264, 341-342, 483-484, 552-553, 621-622, 672-673, 723-724, 846-885, 907-912, 988-1006, 1054, 1081-1082, 1223-1234, 1333-1344, 1427-1438, 1606-1657, 1676-1685, 1689-1700, 1710-1718, 1871-1923, 1926-1927, 2097-2098, 2158-2159, 2317-2318 |
| backend/protzilla/methods/data\_integration.py                                |      262 |       85 |     68% |121, 131-133, 280-339, 405-430, 531-568, 666-686, 716-717, 748-749, 873-878 |
| backend/protzilla/methods/data\_preprocessing.py                              |      279 |       21 |     92% |118, 131-140, 247, 277, 291, 913, 931-938, 951, 964-971 |
| backend/protzilla/methods/importing.py                                        |      121 |       17 |     86% |60, 246-281, 404-405 |
| backend/protzilla/run.py                                                      |      211 |       50 |     76% |55-101, 195, 200, 207, 211-214, 221-222, 233-238, 261-264, 285-287, 316, 338, 352, 364 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |      144 |        9 |     94% |92, 201, 204, 209, 224, 230, 234, 269-270 |
| backend/protzilla/step\_manager.py                                            |      184 |       14 |     92% |210, 214, 218, 284, 294-304, 452, 537-542 |
| backend/protzilla/stepfactory.py                                              |       16 |        1 |     94% |        22 |
| backend/protzilla/steps.py                                                    |      266 |       39 |     85% |121, 131-137, 161, 164, 180, 219, 245, 247, 256, 263-290, 302, 305, 319, 353, 381, 517, 525-526, 538-547, 562-569, 590, 593 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      401 |       80 |     80% |107, 109, 116, 161-162, 164, 166, 201, 215, 219, 223, 227, 237, 241-246, 254, 256, 258, 278, 283, 285, 328-331, 396-397, 399-400, 415-416, 418-419, 499, 516, 566, 576, 744, 746, 776-783, 792-805, 981-993, 996-1008, 1034-1050, 1064-1080 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |        0 |    100% |           |
| backend/protzilla/utilities/utilities.py                                      |       61 |       14 |     77% |31-32, 75, 77, 88, 131-137, 141-144 |
| backend/protzilla/workflow.py                                                 |       14 |        9 |     36% |  6, 17-25 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       28 |        5 |     82% | 90-93, 97 |
| **TOTAL**                                                                     | **7423** | **1848** | **75%** |           |


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