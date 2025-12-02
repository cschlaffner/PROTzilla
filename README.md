# Repository Coverage



| Name                                                                                       |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| backend/\_\_init\_\_.py                                                                    |        0 |        0 |    100% |           |
| backend/main/\_\_init\_\_.py                                                               |        0 |        0 |    100% |           |
| backend/main/upload\_handler.py                                                            |       39 |       39 |      0% |      1-70 |
| backend/main/urls.py                                                                       |        5 |        5 |      0% |     17-23 |
| backend/main/views.py                                                                      |      353 |      353 |      0% |     1-715 |
| backend/main/views\_helper.py                                                              |       90 |       63 |     30% |16-23, 27-37, 41-57, 61, 74-97, 115-140, 152-155, 159-160, 176-178, 184 |
| backend/main/views\_settings.py                                                            |      194 |      118 |     39% |37-38, 60, 64-79, 85-89, 93-106, 121-122, 133-135, 138-141, 152, 182, 190, 216-217, 228-246, 250-322, 328-347, 353 |
| backend/protzilla/\_\_init\_\_.py                                                          |        0 |        0 |    100% |           |
| backend/protzilla/all\_steps.py                                                            |       13 |        0 |    100% |           |
| backend/protzilla/data\_analysis/\_\_init\_\_.py                                           |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/classification.py                                         |       65 |       32 |     51% |36-55, 57, 59-75, 347-404 |
| backend/protzilla/data\_analysis/classification\_helper.py                                 |       82 |       15 |     82% |41, 81-82, 103-114, 131, 166-169 |
| backend/protzilla/data\_analysis/clustering.py                                             |       69 |       11 |     84% |139, 362-377, 381-385 |
| backend/protzilla/data\_analysis/differential\_expression.py                               |       13 |        7 |     46% |     17-23 |
| backend/protzilla/data\_analysis/differential\_expression\_anova.py                        |       37 |       10 |     73% |1, 5, 71-76, 86, 91, 101, 104-107 |
| backend/protzilla/data\_analysis/differential\_expression\_helper.py                       |       48 |        2 |     96% |   43, 104 |
| backend/protzilla/data\_analysis/differential\_expression\_kruskal\_wallis.py              |       46 |        1 |     98% |       199 |
| backend/protzilla/data\_analysis/differential\_expression\_linear\_model.py                |       56 |        9 |     84% |52-53, 60-61, 116-122 |
| backend/protzilla/data\_analysis/differential\_expression\_mann\_whitney.py                |       46 |        1 |     98% |       236 |
| backend/protzilla/data\_analysis/differential\_expression\_t\_test.py                      |       53 |       11 |     79% |17, 63-64, 73-77, 124-128 |
| backend/protzilla/data\_analysis/dimension\_reduction.py                                   |       33 |        6 |     82% |67-72, 100, 165-170, 179 |
| backend/protzilla/data\_analysis/model\_evaluation.py                                      |       10 |        0 |    100% |           |
| backend/protzilla/data\_analysis/model\_evaluation\_plots.py                               |       19 |        0 |    100% |           |
| backend/protzilla/data\_analysis/plots.py                                                  |      135 |        9 |     93% |79, 139, 293, 324, 330, 372, 380-381, 396 |
| backend/protzilla/data\_analysis/ptm\_analysis.py                                          |       41 |        2 |     95% |   103-104 |
| backend/protzilla/data\_analysis/ptm\_quantification/\_\_init\_\_.py                       |        0 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_quantification/flexiquant.py                         |      201 |        1 |     99% |       125 |
| backend/protzilla/data\_analysis/ptm\_quantification/multiflex.py                          |      214 |        9 |     96% |225, 264, 305-309, 356, 626, 689 |
| backend/protzilla/data\_analysis/ptm\_visualization/\_\_init\_\_.py                        |        3 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_bar\_plot.py                      |       20 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_details\_plot.py                  |       34 |        2 |     94% |     50-51 |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_overview\_plot.py                 |       25 |        0 |    100% |           |
| backend/protzilla/data\_analysis/ptm\_visualization/ptm\_vis\_utils.py                     |       49 |        0 |    100% |           |
| backend/protzilla/data\_integration/\_\_init\_\_.py                                        |        0 |        0 |    100% |           |
| backend/protzilla/data\_integration/database\_integration.py                               |       58 |       10 |     83% |73, 101-114 |
| backend/protzilla/data\_integration/database\_query.py                                     |      129 |       60 |     53% |28-81, 85-87, 91, 114-117, 120-138, 142-146, 150-157, 195-200, 211-214 |
| backend/protzilla/data\_integration/di\_plots.py                                           |      123 |       49 |     60% |47, 57, 60, 64, 69, 76, 81-83, 87, 90-92, 95, 106-107, 121-123, 168, 172, 174-176, 178-179, 182, 184-189, 192, 212-216, 234-239, 283, 287, 291, 293-295, 298, 303-305, 308, 325, 357, 371, 385 |
| backend/protzilla/data\_integration/enrichment\_analysis.py                                |      359 |      138 |     62% |25-26, 179-180, 216, 223, 278-282, 330, 395, 398-401, 416-433, 539-540, 557-560, 566-696, 789-790, 799-800, 813-814, 816-817, 819-822, 826-827, 829-832, 842-843, 853-857, 861-862, 874-875, 887-888, 891-892, 902-905 |
| backend/protzilla/data\_integration/enrichment\_analysis\_gsea.py                          |      147 |       17 |     88% |145-146, 149-150, 157-158, 161-163, 166, 216-218, 408-409, 413, 420 |
| backend/protzilla/data\_integration/enrichment\_analysis\_helper.py                        |       73 |        6 |     92% |137-139, 145, 150-151 |
| backend/protzilla/data\_preprocessing/\_\_init\_\_.py                                      |        0 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/filter\_proteins.py                                  |       19 |        2 |     89% |     59-60 |
| backend/protzilla/data\_preprocessing/filter\_samples.py                                   |       47 |        0 |    100% |           |
| backend/protzilla/data\_preprocessing/imputation.py                                        |      131 |        3 |     98% |47-53, 175 |
| backend/protzilla/data\_preprocessing/normalisation.py                                     |       98 |        1 |     99% |       280 |
| backend/protzilla/data\_preprocessing/outlier\_detection.py                                |       63 |        3 |     95% |185, 202, 265 |
| backend/protzilla/data\_preprocessing/peptide\_filter.py                                   |       16 |        2 |     88% |     48-49 |
| backend/protzilla/data\_preprocessing/plots.py                                             |      102 |       10 |     90% |207-208, 241, 252, 328-347 |
| backend/protzilla/data\_preprocessing/plots\_helper.py                                     |       17 |       13 |     24% |15-24, 38-47 |
| backend/protzilla/data\_preprocessing/transformation.py                                    |       24 |        2 |     92% |    48, 64 |
| backend/protzilla/disk\_operator.py                                                        |      267 |       47 |     82% |24-25, 36-37, 39, 57-60, 113-115, 130, 152, 157, 174-179, 182-190, 196-214, 243, 296-299, 322-325 |
| backend/protzilla/form.py                                                                  |      154 |       35 |     77% |102, 112-116, 200-202, 206, 209-212, 215-228, 231, 239, 246, 253, 256-279 |
| backend/protzilla/form\_helper.py                                                          |       18 |       11 |     39% |7, 15-16, 31-34, 40-48 |
| backend/protzilla/importing/\_\_init\_\_.py                                                |        0 |        0 |    100% |           |
| backend/protzilla/importing/example\_dataset\_import.py                                    |       15 |        9 |     40% |     13-45 |
| backend/protzilla/importing/import\_utils.py                                               |       24 |        0 |    100% |           |
| backend/protzilla/importing/metadata\_import.py                                            |       72 |       38 |     47% |28, 30, 32, 34, 48, 52-53, 74, 85-95, 100, 106-113, 128-153, 179-204 |
| backend/protzilla/importing/ms\_data\_import.py                                            |      121 |       22 |     82% |34-35, 110-112, 152-154, 282-300 |
| backend/protzilla/importing/peptide\_import.py                                             |       44 |        6 |     86% |13-14, 44-45, 63-64 |
| backend/protzilla/methods/data\_analysis.py                                                |      624 |      384 |     38% |53, 57-58, 73-74, 87, 89-92, 94, 99, 112, 127-128, 135, 141-142, 149-150, 156-157, 165-166, 172-173, 180-181, 187-188, 193-195, 200, 203-209, 212-221, 250-252, 256-260, 271-277, 333-355, 379-385, 388-397, 431-451, 471-473, 477-479, 485-494, 538-560, 569-577, 584-585, 589-591, 597-606, 650-676, 695-697, 701-703, 709-716, 744-745, 747, 749-753, 763-764, 768-770, 776-783, 811-814, 821-824, 831-837, 871-889, 893-913, 919, 921-933, 949-951, 972, 977-987, 1011-1012, 1024-1025, 1051, 1081-1098, 1119, 1123-1128, 1133-1142, 1147-1154, 1156, 1159-1168, 1248-1253, 1255, 1258-1267, 1341-1342, 1344-1348, 1350-1360, 1422-1429, 1432-1441, 1566-1573, 1576-1585, 1709, 1711, 1715-1725, 1742, 1744-1754, 1810, 1812-1822, 1871-1872, 1875-1877, 1881-1890, 1895-1899, 1904-1912, 1936-1938, 1945-1954, 1976-1978, 1995-1997, 2023-2032, 2063-2098, 2111-2137, 2149, 2151-2157, 2162-2172, 2177-2181, 2187, 2193, 2195-2201, 2206-2216, 2221-2225, 2234-2242, 2273, 2280, 2284-2289, 2296-2305, 2319-2323, 2331, 2338-2348 |
| backend/protzilla/methods/data\_integration.py                                             |      295 |      200 |     32% |43, 48-49, 56-57, 61-62, 66, 71, 76, 81, 85-90, 95, 102-106, 113, 121, 164, 166-179, 194-202, 277-320, 332-340, 352, 356-369, 426-442, 447-455, 467, 471-483, 562-602, 611-619, 631-640, 718-745, 748-756, 769-778, 798-799, 805, 809, 813-823, 842, 887-898, 903-910, 919-931, 999-1008, 1062-1063, 1068, 1072-1085 |
| backend/protzilla/methods/data\_preprocessing.py                                           |      207 |      102 |     51% |29-30, 34-35, 40, 45, 50-51, 55-56, 61, 68, 72, 78, 84-85, 119-129, 151, 155-161, 188-189, 223, 256-266, 291, 317-327, 343, 353, 380-388, 414-422, 448, 493-501, 537-545, 596-599, 645-653, 695-707, 744-745, 749, 800-808, 862-863 |
| backend/protzilla/methods/importing.py                                                     |      122 |       63 |     48% |21-23, 33, 38, 41-43, 46-51, 90, 127, 129-135, 163, 173, 194, 198-204, 228, 230-236, 251-270, 279-284, 289, 293-299, 315-316, 325, 329-335, 351-354, 363-364, 372-380 |
| backend/protzilla/run.py                                                                   |      208 |       46 |     78% |54-100, 194, 199, 206, 210-213, 220-221, 232-237, 276-278, 314, 341, 355, 363 |
| backend/protzilla/run\_helper.py                                                           |       12 |        1 |     92% |        26 |
| backend/protzilla/runner.py                                                                |       79 |        7 |     91% |113-121, 145-146 |
| backend/protzilla/stepfactory.py                                                           |       15 |        3 |     80% |21, 26, 35 |
| backend/protzilla/steps.py                                                                 |      381 |       65 |     83% |116, 143, 146, 162, 188, 199, 202, 216, 219-221, 250, 276, 298-303, 354-356, 366, 377, 384, 392, 399, 402, 433, 457-458, 480, 490-503, 531, 543, 557, 593, 604, 666-674, 690, 702, 704-711, 716, 757-759, 788, 807-810, 817-820 |
| backend/protzilla/utilities/\_\_init\_\_.py                                                |        1 |        0 |    100% |           |
| backend/protzilla/utilities/clustergram.py                                                 |      376 |       83 |     78% |97, 99, 106, 150-151, 153, 155, 190, 205, 209, 213, 217, 227, 231-236, 244, 246, 248, 259-270, 273, 275, 315-318, 383-384, 386-387, 402-403, 405-406, 486, 503, 696, 698, 728-735, 744-757, 930-942, 945-957, 983-999, 1013-1029 |
| backend/protzilla/utilities/dunn\_score.py                                                 |       10 |        6 |     40% | 25, 41-48 |
| backend/protzilla/utilities/transform\_dfs.py                                              |       25 |        0 |    100% |           |
| backend/protzilla/utilities/utilities.py                                                   |       56 |        9 |     84% |29-30, 71, 82, 100, 135-138 |
| backend/protzilla/workflow.py                                                              |       11 |        6 |     45% |  6, 15-20 |
| frontend/\_\_init\_\_.py                                                                   |        0 |        0 |    100% |           |
| runner\_cli.py                                                                             |       24 |        5 |     79% | 60-63, 67 |
| src/protein-sequencing/protein\_sequencing/\_\_init\_\_.py                                 |        1 |        0 |    100% |           |
| src/protein-sequencing/protein\_sequencing/bar\_plot.py                                    |      250 |       77 |     69% |50-52, 80-83, 139-179, 233-267, 290, 303-321, 339, 342, 344, 361, 373, 376, 378, 416-417, 419-420, 446-450 |
| src/protein-sequencing/protein\_sequencing/data\_preprocessing/max\_quant\_preprocessor.py |      128 |        8 |     94% |98, 100, 102, 105-106, 111-112, 137 |
| src/protein-sequencing/protein\_sequencing/data\_preprocessing/preprocessor\_helper.py     |      205 |       18 |     91% |133, 160, 185-187, 190, 195, 202-207, 257-258, 277-278, 283 |
| src/protein-sequencing/protein\_sequencing/details\_plot.py                                |      582 |      181 |     69% |22, 45-48, 86, 97, 113-141, 154, 167-181, 236-277, 311-327, 409-423, 450-460, 465-466, 506-532, 542-543, 561-569, 578, 586-587, 589-590, 600, 608-616, 635-643, 666-676, 681-682, 696-697, 712-725, 738-739, 758-766, 799-805, 822-823, 841-842, 860, 862, 864, 897, 900-906, 914, 933-935, 937-939, 944, 970, 994, 996 |
| src/protein-sequencing/protein\_sequencing/exon\_helper.py                                 |       99 |       10 |     90% |16, 59, 73, 79-80, 120, 125-130 |
| src/protein-sequencing/protein\_sequencing/overview\_plot.py                               |      281 |       48 |     83% |34, 36, 68, 71, 73, 126-153, 303, 348-365, 409-410, 412-413 |
| src/protein-sequencing/protein\_sequencing/plotter.py                                      |      317 |       82 |     74% |52, 58, 72-73, 99-103, 116-119, 121, 131, 144, 146-149, 205, 212-218, 220, 238-242, 265, 272-273, 295, 363-378, 382, 394, 424, 427-433, 442-443, 463-464, 466-471, 477-492, 516-517, 533-534 |
| src/protein-sequencing/protein\_sequencing/uniprot\_align.py                               |       40 |        9 |     78% |12, 14, 28, 32-39, 52 |
|                                                                                  **TOTAL** | **8463** | **2603** | **69%** |           |


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