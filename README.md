# Repository Coverage



| Name                                                                             |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                          |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                     |        0 |        0 |    100% |           |
| backend/main/asgi.py                                                             |        4 |        4 |      0% |     10-16 |
| backend/main/settings.py                                                         |       42 |       42 |      0% |    13-192 |
| backend/main/upload\_handler.py                                                  |       37 |       37 |      0% |      1-73 |
| backend/main/urls.py                                                             |        6 |        6 |      0% |     16-23 |
| backend/main/views.py                                                            |       78 |       78 |      0% |     1-121 |
| backend/main/views\_with\_api.py                                                 |      252 |      252 |      0% |     1-465 |
| backend/main/views\_with\_api\_helper.py                                         |       43 |       37 |     14% |7-37, 41, 51-92 |
| backend/main/wsgi.py                                                             |        4 |        4 |      0% |     10-16 |
| backend/manage.py                                                                |       13 |       13 |      0% |      3-24 |
| backend/protzilla/\_\_init\_\_.py                                                |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                                  |        7 |        1 |     86% |        84 |
| backend/protzilla/constants/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| backend/protzilla/constants/colors.py                                            |        2 |        0 |    100% |           |
| backend/protzilla/constants/paths.py                                             |       11 |        2 |     82% |     13-14 |
| backend/protzilla/constants/protzilla\_logging.py                                |       43 |       16 |     63% |5-14, 20, 36, 41, 45, 47-49, 51-53, 55-57, 59-61, 63-70 |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                                 |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                               |       65 |       32 |     51% |33-52, 54, 56-66, 263-313 |
| backend/protzilla/data\_analysis/classification\_helper.py                       |       82 |       15 |     82% |41, 81-82, 104-115, 132, 167-170 |
| backend/protzilla/data\_analysis/clustering.py                                   |       69 |       11 |     84% |141, 365-380, 384-388 |
| backend/protzilla/data\_analysis/differential\_expression.py                     |       13 |        8 |     38% |     16-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py              |       37 |       11 |     70% |1, 5, 73, 88-91, 101, 104-107, 117 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py             |       48 |       11 |     77% |43, 98-101, 125, 132-135, 143-153 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py    |       46 |       11 |     76% |79, 178, 184, 189-191, 196-197, 226-231 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py      |       56 |        9 |     84% |52-53, 60-61, 120-126 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py      |       46 |       11 |     76% |96-131, 157, 202, 208, 211-212, 233, 262-272 |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py            |       53 |       11 |     79% |17, 63-64, 73-77, 124-128 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                         |       33 |        6 |     82% |67-72, 100, 165-170, 179 |
| backend/protzilla/data\_analysis/model\_evaluation.py                            |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                     |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                        |      131 |       10 |     92% |75, 135, 285, 316, 318, 324, 366, 374-375, 390 |
| backend/protzilla/data\_analysis/protein\_graphs.py                              |      412 |       37 |     91% |32-40, 157, 163-166, 169-172, 177, 209-210, 224, 297-299, 308-310, 328-329, 378, 404-408, 452, 466, 535, 566, 573, 774, 836-839 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                                |       41 |       17 |     59% |44, 56-63, 80, 90, 100-101, 103-109, 123-128 |
| backend/protzilla/data\_analysis/ptm\_quantification.py                          |      213 |      195 |      8% |41-313, 349-405, 436-542, 553-572, 583-598, 609 |
| backend/protzilla/data\_integration/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                     |       58 |       10 |     83% |73, 101-114 |
| backend/protzilla/data\_integration/database\_query.py                           |      129 |       78 |     40% |28-81, 85-87, 91, 114, 119-127, 137-149, 151-160, 182, 185-190, 199, 201-202, 217-218, 229-237, 256, 261, 264-273 |
| backend/protzilla/data\_integration/di\_plots.py                                 |      127 |       39 |     69% |94-97, 111, 113, 125, 173, 177, 179-181, 183-184, 187, 189-194, 197, 217-221, 239-244, 288, 292, 296, 298-300, 303, 308-310, 313, 331, 363, 377, 392 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                      |      338 |       91 |     73% |24-25, 178-179, 215, 222, 277-281, 329, 397-400, 415-416, 431-432, 538-541, 550-551, 556-558, 561-565, 567, 570-576, 589-590, 602-612, 616-617, 619-622, 634-635, 638-648, 651-652, 668, 749-750, 759-760, 773-774, 776-777, 779-782, 786-787, 789-792, 805, 823-824, 836-837, 840-841, 851-854 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py                |      132 |        9 |     93% |154-156, 159, 209-211, 392, 395 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py              |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                            |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                        |       21 |        6 |     71% |35, 47-48, 58-70 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                         |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                              |      131 |        3 |     98% |47-53, 180 |
| backend/protzilla/data\_preprocessing/normalisation.py                           |       98 |       28 |     71% |14, 36, 42, 49, 79, 84, 88, 92, 98, 107, 109, 119, 142, 146, 150, 156, 163, 165-167, 171, 201, 212, 220, 227-229, 234, 282-283 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                      |       70 |       25 |     64% |116, 120, 124-126, 130, 155-187, 194-198, 212-215, 255-256, 271, 275-282 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                         |       16 |        6 |     62% |24-25, 36, 46-47, 50 |
| backend/protzilla/data\_preprocessing/plots.py                                   |      101 |       11 |     89% |248-249, 283, 294, 394-418 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                           |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                          |       26 |        8 |     69% |11, 35, 41-43, 52, 69, 79 |
| backend/protzilla/disk\_operator.py                                              |      221 |       60 |     73% |20-21, 32-33, 35, 53-56, 64-66, 114-116, 143-144, 147, 149-177, 183-184, 193-194, 197-201, 210, 219, 235, 238, 244-245, 248, 257, 260, 263-265, 268, 277, 282, 286, 290, 294, 298, 302 |
| backend/protzilla/importing/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                                  |       68 |       14 |     79% |29, 31, 45-47, 98-105, 122, 129, 147, 179-180, 187-189 |
| backend/protzilla/importing/ms\_data\_import.py                                  |      120 |       58 |     52% |28, 30-32, 82, 92-94, 104, 109-110, 122-125, 133, 152, 188, 214, 243-255, 258-299 |
| backend/protzilla/importing/peptide\_import.py                                   |       47 |        6 |     87% |17-18, 55-56, 79-80 |
| backend/protzilla/methods/data\_analysis.py                                      |      377 |      241 |     36% |21-22, 41, 46-50, 57-64, 85-86, 91, 94-101, 123-124, 129, 132-139, 160-161, 166-175, 203, 205-213, 215-216, 240-251, 273-277, 279-284, 306-307, 310-318, 320-321, 334, 342-345, 347-368, 373, 381-383, 388-391, 396, 398-399, 405, 408-411, 419, 422, 429-432, 437, 441-442, 447, 450-451, 457, 461-463, 472, 477-485, 493-501, 503, 519-532, 536-537, 555-562, 565-571, 573-574, 590-608, 631-652, 684-685, 690-696, 704, 707-710, 715, 727, 730-735, 740, 751-753, 756, 760, 781-785, 790, 792-795, 804-805, 808-809, 813-816, 835-854, 861, 868, 875-878, 891-892, 898-937 |
| backend/protzilla/methods/data\_integration.py                                   |      127 |       36 |     72% |15, 22-24, 44, 47-59, 84, 87-103, 124, 127-139, 166, 193, 205, 208-211, 223, 244, 247-253, 274, 295, 313 |
| backend/protzilla/methods/data\_preprocessing.py                                 |      205 |       40 |     80% |37, 43-44, 61, 74, 77, 88, 91, 104, 107, 118, 121, 132, 135, 146, 149, 160, 163, 174, 177, 188, 191, 202, 205, 216, 219, 230, 233, 244, 247, 272, 275, 289, 292, 307, 310, 321, 324, 336, 339 |
| backend/protzilla/methods/importing.py                                           |       85 |       24 |     72% |21, 58, 61-62, 67, 70, 73, 77-78, 83, 86, 89, 93-94, 112, 120, 125, 128, 131-132, 137, 140, 143-144 |
| backend/protzilla/run.py                                                         |      160 |       78 |     51% |28-88, 103, 107, 127-134, 145, 148, 150, 162-167, 170, 177, 181, 186, 189-191, 201, 205, 207, 217, 222, 226, 230, 235, 239, 242-243, 247, 251-261 |
| backend/protzilla/run\_helper.py                                                 |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                      |       77 |       10 |     87% |109-117, 125-127, 140-141 |
| backend/protzilla/stepfactory.py                                                 |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                       |      342 |       91 |     73% |82, 97-106, 118, 121, 132, 135, 149, 227, 234, 249, 252, 281-311, 316, 339-340, 358-371, 411, 413-425, 443-458, 469, 506-508, 513-521, 537, 549, 551-558, 563, 607-609, 638, 657-660 |
| backend/protzilla/utilities/\_\_init\_\_.py                                      |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                       |      375 |       99 |     74% |82, 97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 277-296, 315-318, 331, 383-384, 386-387, 402-403, 405-406, 486, 503, 523, 696, 698, 728-735, 744-757, 767-771, 929-941, 944-956, 982-998, 1012-1028 |
| backend/protzilla/utilities/dunn\_score.py                                       |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                    |       25 |       11 |     56% |23-44, 60-79, 83, 101, 104 |
| backend/protzilla/utilities/utilities.py                                         |       56 |       10 |     82% |29-30, 71, 82, 100, 126, 135-138 |
| backend/protzilla/workflow.py                                                    |        5 |        1 |     80% |         6 |
| backend/runner\_cli.py                                                           |       24 |        5 |     79% | 60-63, 67 |
| backend/tests/\_\_init\_\_.py                                                    |        0 |        0 |    100% |           |
| backend/tests/conftest.py                                                        |      109 |       23 |     79% |103-108, 113-117, 122-126, 487-501 |
| backend/tests/protzilla/\_\_init\_\_.py                                          |        0 |        0 |    100% |           |
| backend/tests/protzilla/data\_analysis/\_\_init\_\_.py                           |        0 |        0 |    100% |           |
| backend/tests/protzilla/data\_analysis/test\_analysis\_plots.py                  |       23 |        3 |     87% | 83, 98-99 |
| backend/tests/protzilla/data\_analysis/test\_classification.py                   |       37 |       15 |     59% |8, 51, 72-96, 125, 143-145, 155-156 |
| backend/tests/protzilla/data\_analysis/test\_clustering.py                       |       38 |        0 |    100% |           |
| backend/tests/protzilla/data\_analysis/test\_differential\_expression.py         |      178 |       25 |     86% |104, 153, 210, 432, 452, 459, 482, 497-498, 511, 522-524, 604, 617, 623, 628, 635, 660-661, 664-677 |
| backend/tests/protzilla/data\_analysis/test\_differential\_expression\_helper.py |       10 |        6 |     40% |4, 9, 17-25 |
| backend/tests/protzilla/data\_analysis/test\_dimension\_reduction.py             |       45 |        8 |     82% |91-114, 119-143 |
| backend/tests/protzilla/data\_analysis/test\_filter\_peptites\_of\_protein.py    |        6 |        3 |     50% |   1-4, 18 |
| backend/tests/protzilla/data\_analysis/test\_peptide\_analysis.py                |       26 |       13 |     50% |10, 12, 18, 30, 47-83 |
| backend/tests/protzilla/data\_analysis/test\_plots\_data\_analysis.py            |       89 |       20 |     78% |77, 86, 95, 112-113, 121-122, 130-131, 139-140, 147-150, 157, 206-213 |
| backend/tests/protzilla/data\_analysis/test\_protein\_graphs.py                  |      648 |       20 |     97% |782-810, 1570-1573 |
| backend/tests/protzilla/data\_integration/\_\_init\_\_.py                        |        0 |        0 |    100% |           |
| backend/tests/protzilla/data\_integration/test\_database\_integration.py         |       25 |        0 |    100% |           |
| backend/tests/protzilla/data\_integration/test\_database\_query.py               |       37 |        0 |    100% |           |
| backend/tests/protzilla/data\_integration/test\_enrichment\_analysis.py          |      401 |       41 |     90% |169, 181, 193, 199, 211, 214, 218, 227, 238, 242, 258, 262, 278, 282, 298, 305, 321, 325, 331, 338, 344, 351, 372, 379, 391, 398, 411-414, 429, 433, 439, 444-445, 477, 488-490, 496-498, 502, 507-509 |
| backend/tests/protzilla/data\_integration/test\_plots\_data\_integration.py      |      128 |       27 |     79% |31, 41, 56, 86, 106, 123, 155-156, 171, 181-182, 198, 264, 275, 284, 311-312, 318, 332-347 |
| backend/tests/protzilla/data\_preprocessing/\_\_init\_\_.py                      |        0 |        0 |    100% |           |
| backend/tests/protzilla/data\_preprocessing/conftest.py                          |       18 |        2 |     89% |    45, 65 |
| backend/tests/protzilla/data\_preprocessing/test\_filter\_proteins.py            |       28 |        4 |     86% | 16-42, 85 |
| backend/tests/protzilla/data\_preprocessing/test\_filter\_samples.py             |       59 |        4 |     93% |79, 132, 136, 184 |
| backend/tests/protzilla/data\_preprocessing/test\_imputation.py                  |      102 |       12 |     88% |107-108, 142-143, 177-178, 212-213, 245-246, 287-288 |
| backend/tests/protzilla/data\_preprocessing/test\_normalisation.py               |       75 |       10 |     87% |310, 328, 355, 358, 364, 372, 384, 394, 404-405 |
| backend/tests/protzilla/data\_preprocessing/test\_outlier\_detection.py          |       51 |       13 |     75% |76, 89, 96-98, 111, 115, 132-134, 138, 145, 158, 165-167 |
| backend/tests/protzilla/data\_preprocessing/test\_peptide\_preprocessing.py      |       20 |        4 |     80% |17, 56, 60-61 |
| backend/tests/protzilla/data\_preprocessing/test\_plots\_data\_preprocessing.py  |       50 |       17 |     66% |19-20, 38-39, 55-56, 65, 80-81, 91-92, 101, 133-136, 138 |
| backend/tests/protzilla/data\_preprocessing/test\_transformation.py              |       51 |        2 |     96% |  190, 227 |
| backend/tests/protzilla/importing/\_\_init\_\_.py                                |        0 |        0 |    100% |           |
| backend/tests/protzilla/importing/test\_metadata\_import.py                      |       44 |        5 |     89% |12, 25, 62, 85-86 |
| backend/tests/protzilla/importing/test\_ms\_data\_import.py                      |       84 |        9 |     89% |232-233, 256-259, 262, 271, 275-276, 315 |
| backend/tests/protzilla/importing/test\_peptide\_import.py                       |       39 |        6 |     85% |135-137, 165-167 |
| backend/tests/protzilla/test\_apihelper.py                                       |        4 |        2 |     50% |     4, 73 |
| backend/tests/protzilla/test\_run.py                                             |       74 |        0 |    100% |           |
| backend/tests/protzilla/test\_runner.py                                          |      124 |       41 |     67% |49-53, 58-66, 80, 87-89, 150, 163, 166-168, 172, 188-190, 218, 228-231, 242-245, 252, 287-288, 290-330 |
| backend/tests/protzilla/test\_runner\_cli.py                                     |       67 |       22 |     67% |16, 19-20, 26-27, 37, 41, 44, 55-56, 67-68, 80-81, 87-88, 96-97, 102, 106, 111-112 |
| backend/tests/protzilla/test\_steps.py                                           |      102 |        0 |    100% |           |
| backend/tests/protzilla/test\_transform\_dfs.py                                  |       47 |        0 |    100% |           |
| backend/tests/protzilla/test\_utilities.py                                       |        7 |        0 |    100% |           |
| backend/tests/protzilla/test\_workflow.py                                        |       12 |        2 |     83% |    12, 18 |
| backend/tests/ui/\_\_init\_\_.py                                                 |        0 |        0 |    100% |           |
| backend/tests/ui/test\_views.py                                                  |       18 |       12 |     33% |5, 106, 115-121, 127-129, 135-137, 143-145 |
| frontend/\_\_init\_\_.py                                                         |        0 |        0 |    100% |           |
|                                                                        **TOTAL** | **8528** | **2385** | **72%** |           |


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