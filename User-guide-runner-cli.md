{should be added to updated ReadMe for first release when approved}
## PROTzilla Command line interface
A command line based runner for PROTzilla workflows is available via `runner_cli.py`. 
It allows you to run PROTzilla workflows from the command line, which can be useful for batch processing or automation tasks. 
The runner calculates a given dataset on a given workflow without the need for a graphical user interface.
It is recommended to adjust one of the template workflows `standard`, `only_import` and `only_import_and_filter_proteins` for your calculation needs via the PROTzilla webpage and then save it as a new workflow with the save icon right of the run's name.

Please be aware of the fact that the template workflows do not have all necessary fields specified and will fail if you try to run them without adjusting them first.

The command line interface can be started with the following command:

```bash
python runner_cli.py -h
```
This will display the help message with all available options and arguments.
An example execution could be like this:

```bash
python runner_cli.py --meta-data-path /path/to/meta_data.csv -n MyRunForTheRunner -d disk -v my_modified_standard_workflow /path/to/proteinGroups.txt
```

This command will run the workflow `my_modified_standard_workflow` on the input file `/path/to/proteinGroups.txt` with the metadata provided in `/path/to/meta_data.csv`. The workflow `my_modified_standard_workflow` will be used, and the run will be saved to disk. The run will be named `MyRunForTheRunner`. During execution more console information is shown due to the `-v` flag.
