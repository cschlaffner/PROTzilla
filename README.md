# Repository Coverage



| Name                                                                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                       |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                  |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                               |       36 |       36 |      0% |      1-67 |
| backend/main/urls.py                                                          |        5 |        5 |      0% |     16-22 |
| backend/main/views.py                                                         |      327 |      327 |      0% |     1-635 |
| backend/main/views\_helper.py                                                 |       70 |       58 |     17% |7-37, 41, 50, 55-56, 69-131, 135-138, 148-154 |
| backend/main/views\_settings.py                                               |      137 |      137 |      0% |     1-219 |
| backend/protzilla/\_\_init\_\_.py                                             |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                               |        7 |        1 |     86% |         1 |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                              |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                            |       65 |       35 |     46% |36-55, 57, 59-67, 99, 207, 237-239, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                    |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                  |       13 |        8 |     38% |     16-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py           |       37 |       11 |     70% |1, 5, 73, 88-91, 101, 104-107, 117 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py          |       48 |       11 |     77% |43, 98-101, 125, 132-135, 143-153 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py |       46 |       11 |     76% |79, 178, 184, 189-191, 196-197, 226-231 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py   |       56 |        9 |     84% |52-53, 60-61, 120-126 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py   |       46 |       11 |     76% |96-131, 157, 202, 208, 211-212, 233, 262-272 |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py         |       53 |       11 |     79% |17, 63-64, 73-77, 124-128 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                      |       33 |        6 |     82% |67-72, 100, 165-170, 179 |
| backend/protzilla/data\_analysis/model\_evaluation.py                         |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                  |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                     |      131 |       33 |     75% |28-44, 55, 62, 67, 75-78, 83, 88, 136-137, 189, 211, 229, 241, 244, 266-267, 272, 287, 317-318, 320, 336, 363, 372-374, 391, 464 |
| backend/protzilla/data\_analysis/protein\_graphs.py                           |      412 |       37 |     91% |32-40, 157, 163-166, 169-172, 177, 209-210, 224, 297-299, 308-310, 328-329, 378, 404-408, 452, 466, 535, 566, 573, 774, 836-839 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                             |       41 |       17 |     59% |44, 56-63, 80, 90, 100-101, 103-109, 123-128 |
| backend/protzilla/data\_analysis/ptm\_quantification.py                       |      213 |      195 |      8% |41-313, 349-405, 436-542, 553-572, 583-598, 609 |
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
| backend/protzilla/data\_preprocessing/outlier\_detection.py                   |       67 |        3 |     96% |200, 217, 280 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                      |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                |      102 |       25 |     75% |17, 73, 140, 154, 158-159, 200, 203, 206-207, 210, 221, 239-240, 250-251, 257, 298, 328-350 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                        |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                       |       24 |        7 |     71% |11, 35, 41-43, 63, 73 |
| backend/protzilla/disk\_operator.py                                           |      260 |       73 |     72% |23-24, 35-36, 38, 56-59, 117-119, 134, 156, 161, 175-177, 179-192, 197-216, 218-220, 238, 240-243, 247-248, 251, 265, 276, 279, 288-291, 293, 302, 305, 309-310, 313, 322, 331, 335, 339, 343, 347, 351-366 |
| backend/protzilla/form.py                                                     |      148 |       67 |     55% |11, 21, 29-30, 35-36, 48-49, 61-62, 68-69, 75-76, 82, 88-89, 95, 97-98, 104, 106-112, 120, 131-132, 136, 156-159, 163, 174-179, 182-185, 188-196, 205-207, 218-254 |
| backend/protzilla/form\_helper.py                                             |       13 |        6 |     54% |7, 15-16, 28-29, 33 |
| backend/protzilla/importing/\_\_init\_\_.py                                   |        0 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                               |       70 |       30 |     57% |28, 30, 32, 34, 50-51, 92, 98-104, 115, 126-151, 177-202 |
| backend/protzilla/importing/ms\_data\_import.py                               |      121 |       61 |     50% |29, 31-33, 83, 93-95, 105, 110-111, 123-126, 134, 153, 189, 215, 240-300 |
| backend/protzilla/importing/peptide\_import.py                                |       47 |        6 |     87% |17-18, 55-56, 79-80 |
| backend/protzilla/methods/data\_analysis.py                                   |      443 |      229 |     48% |22-23, 29, 47, 57-58, 62-63, 67-70, 72, 77-78, 83, 101, 113, 119-120, 143-144, 151, 158-159, 169, 171, 178, 182-189, 192-196, 210, 220, 277-283, 291, 299-300, 320-321, 325-328, 339, 345-351, 368, 372-374, 378, 380, 394-397, 399-404, 417-419, 421, 425-427, 451, 466-485, 507-509, 521, 525-530, 535-541, 549-550, 561, 565, 580-603, 634-636, 638, 648, 667-669, 673-677, 685-687, 691, 693-697, 704, 706-707, 716-718, 725-727, 736-740, 745, 747, 759-762, 767, 779-782, 787, 789, 804, 806-812, 818-826, 830-834, 839, 844, 846, 849-851, 857-863, 873, 882-883, 891-902, 913, 918, 922-924, 932, 937-939, 943-1000 |
| backend/protzilla/methods/data\_integration.py                                |      295 |      186 |     37% |30, 40-41, 46, 53, 58, 63-64, 69, 74, 79, 86, 90, 94, 99-103, 110, 118, 165, 168-179, 189-202, 277-320, 332-345, 356-359, 361-369, 426-447, 452-467, 475, 477-483, 562-619, 625-626, 634-758, 764-769, 774-778, 798, 801-809, 813-817, 823, 839-844, 891, 898-912, 919-925, 988, 1009, 1063-1068, 1072-1076 |
| backend/protzilla/methods/data\_preprocessing.py                              |      209 |      103 |     51% |30-31, 35-36, 41, 46, 51-52, 56-57, 62, 69, 73, 79, 85-86, 120-130, 153-162, 188, 222, 255, 259-266, 290, 316, 320-327, 342, 379-388, 413-422, 447, 492-501, 537-546, 591-592, 645-654, 696-708, 760, 800-809, 863-864 |
| backend/protzilla/methods/importing.py                                        |       97 |       17 |     82% |55, 119, 124, 150-151, 156, 163-165, 179-184, 189, 194, 199, 204 |
| backend/protzilla/run.py                                                      |      206 |       91 |     56% |31-89, 92, 95, 103, 110, 114, 117, 119, 136-138, 155, 161, 163, 169, 171, 183, 188, 190, 194-196, 202-205, 210, 214-218, 226, 230-236, 252-254, 262-263, 271, 275, 287, 305, 310, 313-314, 320, 324, 327-328, 332, 336, 340-364 |
| backend/protzilla/run\_helper.py                                              |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                   |       79 |        7 |     91% |111-119, 143-144 |
| backend/protzilla/stepfactory.py                                              |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                    |      379 |      165 |     56% |20-22, 29, 46, 53, 69, 71-73, 87, 98, 102, 109, 113, 117, 120-124, 127, 143, 164, 169, 172, 182, 184, 189-197, 200-202, 209-216, 219, 230-231, 242, 256-257, 264, 278-281, 286-315, 330-338, 342, 347-350, 353, 356-359, 362, 365-366, 373, 375, 378-384, 387, 390, 393, 400, 403, 406, 410, 414-415, 438-440, 443, 456, 469-482, 505, 512, 523, 527, 536-537, 540, 557, 571, 574-581, 590, 594, 598, 612, 616, 623-624, 639-647, 662-665, 669-685, 690-692, 694-705, 717-721, 731-751, 762-774, 783, 786-790, 796-804 |
| backend/protzilla/utilities/\_\_init\_\_.py                                   |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                    |      375 |       99 |     74% |82, 97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 277-296, 315-318, 331, 383-384, 386-387, 402-403, 405-406, 486, 503, 523, 696, 698, 728-735, 744-757, 767-771, 929-941, 944-956, 982-998, 1012-1028 |
| backend/protzilla/utilities/dunn\_score.py                                    |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                 |       25 |       11 |     56% |23-44, 60-79, 83, 101, 104 |
| backend/protzilla/utilities/utilities.py                                      |       56 |        9 |     84% |29-30, 71, 82, 100, 135-138 |
| backend/protzilla/workflow.py                                                 |        5 |        1 |     80% |         6 |
| frontend/\_\_init\_\_.py                                                      |        0 |        0 |    100% |           |
| runner\_cli.py                                                                |       24 |        5 |     79% | 60-63, 67 |
|                                                                     **TOTAL** | **6256** | **2606** | **58%** |           |


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