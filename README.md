# Repository Coverage



| Name                                                                             |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                          |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                     |        0 |        0 |    100% |           |
| backend/main/asgi.py                                                             |        4 |        4 |      0% |     10-16 |
| backend/main/settings.py                                                         |       44 |       17 |     61% |32-37, 39-45, 50, 94, 125-128, 133, 168-173 |
| backend/main/upload\_handler.py                                                  |       36 |       36 |      0% |      1-67 |
| backend/main/urls.py                                                             |        6 |        6 |      0% |     16-23 |
| backend/main/views.py                                                            |        7 |        7 |      0% |      1-10 |
| backend/main/views\_settings.py                                                  |      137 |      137 |      0% |     1-219 |
| backend/main/views\_with\_api.py                                                 |      266 |      266 |      0% |     1-511 |
| backend/main/views\_with\_api\_helper.py                                         |       68 |       57 |     16% |7-37, 41, 50, 55-56, 69-131, 135-150 |
| backend/main/wsgi.py                                                             |        4 |        4 |      0% |     10-16 |
| backend/manage.py                                                                |       13 |       13 |      0% |      3-24 |
| backend/protzilla/\_\_init\_\_.py                                                |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                                  |        7 |        1 |     86% |         1 |
| backend/protzilla/constants/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| backend/protzilla/constants/colors.py                                            |        6 |        0 |    100% |           |
| backend/protzilla/constants/date\_format.py                                      |        1 |        0 |    100% |           |
| backend/protzilla/constants/paths.py                                             |       12 |        2 |     83% |     14-15 |
| backend/protzilla/constants/protzilla\_logging.py                                |       43 |       16 |     63% |5-14, 20, 36, 41, 45, 47-49, 51-53, 55-57, 59-61, 63-70 |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                                 |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                               |       65 |       35 |     46% |36-55, 57, 59-67, 99, 207, 237-239, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                       |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                   |       69 |       11 |     84% |139, 362-377, 381-385 |
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
| backend/protzilla/data\_analysis/plots.py                                        |      131 |       33 |     75% |28-44, 55, 62, 67, 75-78, 83, 88, 136-137, 189, 211, 229, 241, 244, 266-267, 272, 287, 317-318, 320, 336, 363, 372-374, 391, 464 |
| backend/protzilla/data\_analysis/protein\_graphs.py                              |      412 |       37 |     91% |32-40, 157, 163-166, 169-172, 177, 209-210, 224, 297-299, 308-310, 328-329, 378, 404-408, 452, 466, 535, 566, 573, 774, 836-839 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                                |       41 |       17 |     59% |44, 56-63, 80, 90, 100-101, 103-109, 123-128 |
| backend/protzilla/data\_analysis/ptm\_quantification.py                          |      213 |      195 |      8% |41-313, 349-405, 436-542, 553-572, 583-598, 609 |
| backend/protzilla/data\_integration/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                     |       58 |       10 |     83% |73, 101-114 |
| backend/protzilla/data\_integration/database\_query.py                           |      129 |       81 |     37% |28-81, 85-87, 91, 114, 119-127, 132-149, 151-160, 182, 185-190, 199, 201-202, 217-218, 229-237, 256, 261, 264-273 |
| backend/protzilla/data\_integration/di\_plots.py                                 |      123 |       52 |     58% |47, 57, 60, 64, 69, 76, 81-83, 87, 90-92, 95, 106-107, 123, 168-170, 174-178, 180, 183-189, 213-217, 235-239, 283-285, 289, 293-296, 299-300, 305, 327-328, 358-360, 388-389 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                      |      338 |      127 |     62% |24-25, 178-179, 215, 222, 277-281, 329, 394, 397-400, 415-432, 537-540, 546-667, 747-748, 757-758, 771-772, 774-775, 777-780, 784-785, 787-790, 803, 821-822, 834-835, 838-839, 849-852 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py                |      132 |        9 |     93% |153-155, 158, 208-210, 390, 393 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py              |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                            |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                        |       19 |        2 |     89% |     59-60 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                         |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                              |      131 |       45 |     66% |47-53, 85-86, 91, 95, 124-125, 129, 132, 136-137, 167-168, 175-178, 204-205, 209, 220, 246-247, 282, 285, 288, 291, 294, 297, 308-312, 315-319, 322, 325, 328, 341-345, 458-459, 482-483, 495 |
| backend/protzilla/data\_preprocessing/normalisation.py                           |       98 |       27 |     72% |14, 36, 42, 49, 79, 84, 88, 92, 98, 107, 109, 119, 142, 146, 150, 156, 163, 165-167, 171, 201, 212, 220, 227-229, 279, 290 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                      |       67 |        3 |     96% |200, 217, 280 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                         |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                   |      102 |       36 |     65% |29, 33-34, 65-66, 106, 112, 128, 132, 144, 147, 186-187, 195-196, 199, 202, 205, 232, 238-242, 249, 320-378 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                           |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                          |       24 |        7 |     71% |11, 35, 41-43, 63, 73 |
| backend/protzilla/disk\_operator.py                                              |      260 |       73 |     72% |23-24, 35-36, 38, 56-59, 117-119, 134, 156, 161, 175-177, 179-192, 197-216, 218-220, 238, 240-243, 247-248, 251, 265, 276, 279, 288-291, 293, 302, 305, 309-310, 313, 322, 331, 335, 339, 343, 347, 351-366 |
| backend/protzilla/form.py                                                        |      135 |       63 |     53% |11, 21, 29-30, 35-36, 44-45, 53-54, 60-61, 66-67, 73, 79-80, 86-87, 93, 95-101, 108-109, 116, 120, 144, 148, 167-169, 171-174, 179-182, 193-195, 203-239 |
| backend/protzilla/form\_helper.py                                                |       13 |        6 |     54% |7, 15-16, 28-29, 33 |
| backend/protzilla/importing/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                                  |       70 |       28 |     60% |28, 30, 32, 34, 50-51, 96, 102-109, 124-151, 177-202 |
| backend/protzilla/importing/ms\_data\_import.py                                  |      121 |       61 |     50% |29, 31-33, 83, 93-95, 105, 110-111, 123-126, 134, 153, 189, 215, 240-300 |
| backend/protzilla/importing/peptide\_import.py                                   |       47 |        6 |     87% |17-18, 55-56, 79-80 |
| backend/protzilla/methods/data\_analysis.py                                      |      443 |      229 |     48% |22-23, 29, 47, 57-58, 62-63, 67-70, 72, 77-78, 83, 101, 113, 119-120, 143-144, 151, 158-159, 169, 171, 178, 182-189, 192-196, 210, 220, 276-282, 290, 298-299, 319-320, 324-327, 338, 344-350, 367, 371-373, 377, 379, 393-396, 398-403, 416-418, 420, 424-426, 453-484, 505-507, 519, 523-528, 533-539, 547-548, 559, 563, 578-580, 583-601, 631-633, 635, 645, 664-666, 670-674, 682-684, 688, 690-694, 701, 703-704, 713-715, 722-724, 733-737, 742, 744, 756-759, 764, 776-779, 784, 786, 801, 803-809, 815-823, 827-831, 836, 841, 843, 846-848, 854-860, 870, 879-880, 888-899, 910, 915, 919-921, 929, 934-936, 940-997 |
| backend/protzilla/methods/data\_integration.py                                   |      174 |       86 |     51% |23, 27-28, 38, 42-43, 50, 55-56, 62-63, 67-68, 73, 78, 83, 90, 94-101, 104-105, 112, 114, 122, 161-163, 169-179, 191, 193-209, 216, 220-221, 224-233, 242, 246-247, 252, 256-257, 262, 266, 268-272, 278, 282-283, 288, 298, 339-343, 350-357, 366, 372-376, 382-396 |
| backend/protzilla/methods/data\_preprocessing.py                                 |      209 |      109 |     48% |30-31, 35-36, 41, 46, 51-52, 56-57, 62, 69, 73, 79, 85-86, 120-130, 150-159, 183, 187-196, 217, 247, 251-258, 279, 290, 304, 308-315, 329, 366-375, 400-409, 434, 479-488, 524-533, 578-579, 632-641, 683-695, 786-795, 846-847 |
| backend/protzilla/methods/importing.py                                           |       97 |       17 |     82% |55, 119, 124, 150-151, 156, 163-165, 179-184, 189, 194, 199, 204 |
| backend/protzilla/run.py                                                         |      200 |       85 |     58% |32-87, 91-94, 99, 102, 109, 115-116, 133-135, 152, 154, 160-162, 168, 170, 177, 184-185, 187-190, 193-195, 201, 205, 209-213, 217, 221, 225-231, 243-245, 251, 259, 267, 277, 281, 286, 290, 295, 298-299, 309, 312-313, 317, 321, 325-339 |
| backend/protzilla/run\_helper.py                                                 |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                      |       76 |        7 |     91% |109-117, 140-141 |
| backend/protzilla/stepfactory.py                                                 |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                       |      373 |      164 |     56% |20-22, 29, 46, 53, 69, 71-73, 87, 96-98, 102, 109, 113, 117-122, 125, 141, 162, 167, 170, 180, 182, 187-195, 198-200, 207-214, 217, 228-229, 240, 254-255, 262, 271, 278-307, 322-330, 334, 339-342, 345, 348-351, 354, 357-358, 365, 367, 370-376, 379, 382, 385, 392, 395, 398, 402, 406-407, 430-432, 435, 448, 461-474, 497, 504, 515, 519, 528-529, 532, 549, 563, 566-573, 582, 586, 590, 604, 608, 615-616, 631-639, 654-657, 661-677, 682-684, 686-697, 709-713, 723-743, 745, 759-771, 780, 783-787, 793-801 |
| backend/protzilla/utilities/\_\_init\_\_.py                                      |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                       |      375 |       99 |     74% |82, 97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 277-296, 315-318, 331, 383-384, 386-387, 402-403, 405-406, 486, 503, 523, 696, 698, 728-735, 744-757, 767-771, 929-941, 944-956, 982-998, 1012-1028 |
| backend/protzilla/utilities/dunn\_score.py                                       |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                    |       25 |       11 |     56% |23-44, 60-79, 83, 101, 104 |
| backend/protzilla/utilities/utilities.py                                         |       56 |        9 |     84% |29-30, 71, 82, 100, 135-138 |
| backend/protzilla/workflow.py                                                    |        5 |        1 |     80% |         6 |
| backend/runner\_cli.py                                                           |       24 |        5 |     79% | 60-63, 67 |
| backend/tests/\_\_init\_\_.py                                                    |        0 |        0 |    100% |           |
| backend/tests/conftest.py                                                        |      110 |       23 |     79% |104-109, 114-118, 123-127, 488-502 |
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
| backend/tests/protzilla/data\_integration/test\_enrichment\_analysis.py          |      406 |      120 |     70% |383, 401, 416, 434-529, 587-588, 604, 622, 629-641, 647, 663, 683, 690, 695-696, 704-707, 722-726, 742-746, 763-764, 809, 815, 818, 853-854, 859-860, 865-866, 870, 873-874, 884, 900-901, 905-909, 912-913, 964-965, 988-989, 1015, 1020, 1043, 1060-1061, 1077-1078, 1095, 1122-1123, 1138-1139, 1153-1154, 1188-1189, 1236, 1283, 1308, 1318, 1341, 1352-1353, 1366-1367, 1380, 1399-1400 |
| backend/tests/protzilla/data\_integration/test\_plots\_data\_integration.py      |      128 |       27 |     79% |31, 41, 56, 86, 106, 123, 155-156, 171, 181-182, 198, 264, 275, 284, 311-312, 318, 332-347 |
| backend/tests/protzilla/data\_preprocessing/\_\_init\_\_.py                      |        0 |        0 |    100% |           |
| backend/tests/protzilla/data\_preprocessing/conftest.py                          |       18 |        2 |     89% |    45, 65 |
| backend/tests/protzilla/data\_preprocessing/test\_filter\_proteins.py            |       28 |        6 |     79% |16-42, 88-89, 109 |
| backend/tests/protzilla/data\_preprocessing/test\_filter\_samples.py             |       59 |        9 |     85% |80, 129, 136, 141-142, 185, 188, 192, 211 |
| backend/tests/protzilla/data\_preprocessing/test\_imputation.py                  |      117 |       12 |     90% |170-171, 205-206, 240-241, 275-276, 308-309, 350-351 |
| backend/tests/protzilla/data\_preprocessing/test\_normalisation.py               |       72 |       18 |     75% |310-314, 330, 342-343, 345, 351, 356, 365, 373, 380, 390-392, 404-410 |
| backend/tests/protzilla/data\_preprocessing/test\_outlier\_detection.py          |       51 |       12 |     76% |76, 89, 96-98, 111, 115, 132-134, 138, 145, 171-172 |
| backend/tests/protzilla/data\_preprocessing/test\_peptide\_preprocessing.py      |       20 |        4 |     80% |17, 56, 60-61 |
| backend/tests/protzilla/data\_preprocessing/test\_plots\_data\_preprocessing.py  |       50 |        9 |     82% |20, 39, 56, 81, 92, 134-137 |
| backend/tests/protzilla/data\_preprocessing/test\_transformation.py              |       51 |        7 |     86% |191, 194, 228, 231, 246, 249, 261 |
| backend/tests/protzilla/importing/\_\_init\_\_.py                                |        0 |        0 |    100% |           |
| backend/tests/protzilla/importing/test\_metadata\_import.py                      |       22 |        5 |     77% |6, 22, 87-89 |
| backend/tests/protzilla/importing/test\_ms\_data\_import.py                      |       84 |        9 |     89% |232-233, 256-259, 262, 271, 275-276, 315 |
| backend/tests/protzilla/importing/test\_peptide\_import.py                       |       39 |        6 |     85% |135-137, 165-167 |
| backend/tests/protzilla/test\_apihelper.py                                       |        6 |        4 |     33% |  4, 73-75 |
| backend/tests/protzilla/test\_run.py                                             |       84 |        0 |    100% |           |
| backend/tests/protzilla/test\_runner.py                                          |      109 |       48 |     56% |12, 17, 22, 27, 32, 37, 39, 42-44, 49, 55-56, 62-64, 82, 84, 87, 170, 185, 205, 211, 234, 263-327 |
| backend/tests/protzilla/test\_runner\_cli.py                                     |       67 |       22 |     67% |16, 19-20, 26-27, 37, 41, 44, 55-56, 67-68, 80-81, 87-88, 96-97, 102, 106, 111-112 |
| backend/tests/protzilla/test\_steps.py                                           |      102 |        0 |    100% |           |
| backend/tests/protzilla/test\_transform\_dfs.py                                  |       47 |        0 |    100% |           |
| backend/tests/protzilla/test\_utilities.py                                       |        7 |        0 |    100% |           |
| backend/tests/protzilla/test\_workflow.py                                        |       12 |        2 |     83% |    12, 18 |
| backend/tests/ui/\_\_init\_\_.py                                                 |        0 |        0 |    100% |           |
| backend/tests/ui/test\_views.py                                                  |       22 |       12 |     45% |5, 106, 115, 118-122, 128, 131, 137, 140, 146, 149 |
| frontend/\_\_init\_\_.py                                                         |        0 |        0 |    100% |           |
|                                                                        **TOTAL** | **9016** | **2946** | **67%** |           |


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