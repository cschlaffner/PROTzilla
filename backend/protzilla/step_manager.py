from __future__ import annotations
from typing import TYPE_CHECKING, Any, override

if TYPE_CHECKING:
    from backend.protzilla.disk_operator import DiskOperator

from backend.protzilla.steps import Step, Section, Output, Messages, Plots
from backend.protzilla.constants.data_types import Connection, StepID

import networkx as nx

from warnings import deprecated


class StepManager:
    """
    Manages steps within a run.

    :ivar df_mode: keep DFs in memory or write on disk (note: probably not even used correctly)
    :ivar disk_operator: disk operator to manage dumping step data to disk
    :ivar all_steps: main database for all step instances, addressed by their IDs
    :ivar graph: DiGraph representing connections between steps for easier management
    :ivar current_selected_step_id: ID of the currently selected step
    :ivar _id_clock: logical clock used for instance identifier creation
    """
    @override
    def __repr__(self):
        return f"IMP: {self.sections[Section.IMPORTING]} PRE: {self.sections[Section.DATA_PREPROCESSING]} ANA: {self.sections[Section.DATA_PREPROCESSING]} INT: {self.sections[Section.DATA_INTEGRATION]}"

    def __init__(
        self,
        steps: list[Step] | None = None,
        df_mode: str = "disk",
        disk_operator: DiskOperator | None = None,
    ):
        self.df_mode: str = df_mode
        self.disk_operator: DiskOperator | None = disk_operator

        # Saves all steps, accessible by their instance identifiers
        self.all_steps: dict[StepID, Step] = {}

        # Graph saving connections between steps.
        # All steps are represented by their instance_identifiers as nodes.
        # If an output of step X is connected to an input of step Y,
        # an edge with weight "n_connections"=1 is added. If multiple such links exist,
        # the edge's weight is incremented by 1 with every additional link
        self.graph: nx.DiGraph[StepID] = nx.DiGraph()

        # Instance identifier of the currently selected step
        self._current_selected_step_id: StepID | None = None

        # Logical clock for instance identifier creation.
        # May only be accessed via next_id_number
        self._id_clock: int = 0

        if steps is not None:
            for step in steps:
                self.add_step(step)

    ##
    ## General accessors
    ##

    def get_step_by_id(self, step_id: StepID) -> Step:
        """
        Returns the step instance of the step with the given ID.

        :param step_id: ID of step of interest
        :return: Instance corresponding to the given step ID
        """
        try:
            return self.all_steps[step_id]
        except KeyError:
            raise KeyError("The requested step does not exist.")

    @property
    def all_step_instances(self) -> list[Step]:
        return list(self.all_steps.values())

    @property
    def all_step_ids(self) -> list[StepID]:
        return list(self.all_steps.keys())

    @property
    def all_step_ids_toposorted(self) -> list[StepID]:
        """
        :return: A list of all step instance identifiers in topological order according to the current
            connections in self.graph
        """
        return list(nx.topological_sort(self.graph))

    @property
    def current_selected_step_id(self) -> StepID:
        """
        :return: ID of the currently selected step
        :raises ValueError: if there is no currently selected step
        """
        if self._current_selected_step_id is not None:
            return self._current_selected_step_id
        raise BaseException("No step currently selected.")

    ##
    ## Specific sets of steps/ids by graph properties
    ##
    
    def preceding_steps(self, step_id: StepID) -> list[Step]:
        """
        :param step_id: ID of step of interest
        :return: List of all predecessors of the given step
        """
        ancestor_ids = list(nx.ancestors(self.graph, step_id))
        return [self.all_steps[step_id] for step_id in ancestor_ids]

    def succeeding_steps(self, step_id: StepID) -> list[Step]:
        """
        :param step_id: ID of step of interest
        :return: List of all successors of the given step
        """
        descendant_ids = list(nx.descendants(self.graph, step_id))
        return [self.all_steps[id] for id in descendant_ids]

    @property
    def previous_steps(self) -> list[Step]:
        return self.preceding_steps(self.current_selected_step_id)

    @property
    def following_steps(self) -> list[Step]:
        return self.succeeding_steps(self.current_selected_step_id)

    def calc_dependencies_met_for_step(self, step_id: StepID) -> bool:
        """
        Checks calculation status of all preceding steps in the graph.
        :return: True iff all preceding steps have been calculated
        """
        return all([step.calculation_status == "complete" for step in self.preceding_steps(step_id)])


    def get_step_output(
        self,
        step_type: Step | None = None,
        output_key: str = "",  # TODO remove step_type and default empty string
        instance_identifier: str | None = None,
        include_current_step: bool = False,
    ) -> pd.DataFrame | Any | None:
        """
        Get the specific output of the outputs of a specific step type. The step type can also a parent class of the
        step type, in which case the output of the most recent step of the specific type is returned.

        :param step_type: The type of the step as a class object
        :param output_key: The key of the desired output in the output dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the output from
        :param include_current_step: Whether to include the current step in the search
        :return: The value of the output of the step or None
        """

        if step_type is not None:
            raise NotImplementedError("Passing the step type is deprecated")

        if include_current_step:
            steps_to_search = self.all_steps.values()
        else:
            steps_to_search = self.previous_calculated_steps

        # TODO: this is stupid. iterating over all steps should now only be necessary if for whatever reason the instance identifier is unknown
        # if an instance identifier is present, self.all_steps should be used
        for step in reversed(steps_to_search):
            if (
                StepManager.check_instance_identifier(step, instance_identifier)
                and output_key in step.output
            ):
                val = step.output[output_key]
                if val is None:
                    continue
                if isinstance(val, str) and Path(val).exists():
                    if Path(val).suffix == ".csv":
                        from backend.protzilla.disk_operator import DataFrameOperator

                        df_operator = DataFrameOperator()
                        df = df_operator.read(Path(val))
                        if df.empty:
                            logging.warning(
                                f"Could not read DataFrame from {val}, continuing"
                            )
                            continue
                        return df
                    else:
                        raise ValueError(f"Unsupported file format {Path(str).suffix}")
                return val
        return None

    def get_step_input(
        self,
        step_type: Step | None = None,
        input_key: str = "",  # TODO same as get_step_output
        instance_identifier: str | None = None,
        default: Any = None,
    ):
        """
        Get the specific input of the inputs of a specific step type. The step type can also a parent class of the
        step type, in which case the input of the most recent step of the specific type is returned.
        :param step_type: The type of the step as a class object
        :param input_key: The key of the desired input in the input dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the input from
        :param default: The default value to return if the input is not found
        :return: The value of the input of the step or None
        """

        if step_type is not None:
            raise NotImplementedError("Passing the step type is deprecated")

        for step in reversed(self.previous_calculated_steps):
            if (
                StepManager.check_instance_identifier(step, instance_identifier)
                and input_key in step.inputs
            ):
                return step.inputs[input_key]
        return default

    def get_step_operation(self, step_iid: str) -> str:
        try:
            return self.all_steps[step_iid].operation
        except KeyError: # TODO: Should really not happen and should be caught in a different way
            raise ValueError(f"No step associated with ID {step_iid}")

    def all_steps_in_section(self, section: Section) -> list[Step]:
        """
        Get all steps in a specific section via the section name
        :param section: The section name
        :return: A list of steps in the section
        """
        if section in self.sections:
            return self.sections[section]
        else:
            raise ValueError(f"Unknown section {section}")

    def invalidate_succeeding_steps(self) -> int:
        if self.current_selected_step_iid is None:
            return 0
        steps_to_remove = self.succeeding_steps(self.current_selected_step_iid)
        steps_to_remove.append(self.current_step)
        for step in steps_to_remove:
            step.calculation_status = "outdated"
        return len(steps_to_remove)


    @property
    def previous_calculated_steps(self) -> list[Step]:
        return list(
            filter(
                lambda step: step.calculation_status == "complete", self.previous_steps
            )
        )

    @property
    def current_step(self) -> Step | None:
        return self.all_steps.get(self.current_selected_step_iid)

    @property
    def current_operation(self) -> str:
        return self.current_step.operation

    @property
    def current_section(self) -> Section:
        return self.current_step.section

    @property
    def current_location(self) -> tuple[str, str, str]:
        return (
            self.current_section,
            self.current_operation,
            self.current_selected_step_iid,
        )


    def step_is_terminal(self, step_iid: str) -> bool:
        return int(self.graph.out_degree(step_iid)) == 0
    
    def step_is_source(self, step_iid: str) -> bool:
        return int(self.graph.in_degree(step_iid)) == 0

    @property
    def fallback_step_iid(self) -> str:
        return list(self.all_steps.keys())[0]

    @property
    def is_at_terminal_step(self) -> bool:
        return self.step_is_terminal(self.current_selected_step_iid)

    @property
    def is_at_source_step(self) -> bool:
        return self.step_is_source(self.current_selected_step_iid)

    def add_step(self, step: Step) -> None:
        if not step.section in self.sections:
            raise ValueError(f"Unknown section {step.section}")

        self.all_steps[step.instance_identifier] = step

        if len(self.all_steps) == 1:
            self.current_selected_step_iid = step.instance_identifier
        
        self.graph.add_node(step.instance_identifier)

    def remove_step(self, step_iid: str | None) -> None:
        """
        Removes a step.
        :param step_iid: instance identifier of the step to delete
        """
        if step_iid is None:
            raise ValueError("")
        if step_iid not in self.all_steps.keys():
            raise ValueError(f"No step with iid {str(step_iid)} found")
        if len(self.all_steps) == 1:
            raise ValueError("At least one step must exist")

        self._clear_succeeding_steps(step_iid)
        
        # Navigate to a predecessor if step was selected
        mustNavigateToFallback = False
        if self.current_selected_step_iid == step_iid:
            try:
                self.previous_step()
            except ValueError: # No previous step
                mustNavigateToFallback = True
    
        # Remove all dangling references
        for step in self.all_steps.values():
            step.input_sources = {
                data_key: mapped_step_iid 
                for data_key, mapped_step_iid 
                in step.input_sources.items() 
                if mapped_step_iid != step_iid
            }

        self.graph.remove_node(step_iid)
        del self.all_steps[step_iid]

        if mustNavigateToFallback:
            self.goto_step(self.fallback_step_iid)
    
    @property
    def recommended_next_step_iid(self) -> str | None:
        """
        Mainly for front-end. Instance identifier of the next step to naviagte to when pressing the "Next" button.

        :return: The recommended next step identifier or None if we are at a terminal step
        """
        if self.is_at_terminal_step:
            return None
        return list(self.graph.successors(self.current_selected_step_iid))[0]

    def next_step(self) -> None:
        """
        Go to the next step in the workflow. Depending on the df_mode, the dataframes of the previous output are
        replaced with the respective paths on the disk where they are saved to save memory.

        :return: None
        """
        if not self.is_at_terminal_step:
            self.disk_operator.clear_upload_dir()  # TODO this could be a problem when using protzilla for multiple users
            if self.df_mode == "disk":
                # TODO maybe this doesnt really need to be written to disk anymore,
                # as it is preceeded by a calculation, after which everything is written to
                # disk anyway. Better would be if it would just replace the dfs with their respective paths
                self.current_step.output = Output(
                    self.disk_operator._write_output(self.current_step)
                )
            next_step_iid = self.recommended_next_step_iid
            self.current_selected_step_iid = next_step_iid
        else:
            raise ValueError("Cannot go to the next step from a terminal step")

    def previous_step(self) -> None:
        """
        Go to the previous step in the workflow. If the previous step is in disk mode, the respective dataframes are
        loaded from disk and replaced in the output dictionary of the step.

        :return: None
        """
        if not self.is_at_source_step:
            prev_step_iid = list(self.graph.predecessors(self.current_selected_step_iid))[0]
            self.current_selected_step_iid = prev_step_iid
        else:
            raise ValueError("Cannot go back from a step with no predecessors")

    def goto_step(self, step_iid: str) -> None:
        """
        Go to a specific step in the workflow.
        :param step_iid: The step to navigate to
        """
        if step_iid not in self.all_steps.keys():
            raise ValueError(f"Step {step_iid} not found")

        if self.df_mode == "disk":
            self.disk_operator._write_output(self.current_step)

        self.current_selected_step_iid = step_iid
    
    ## 
    ## Connection management
    ## 

    def connect_steps(self, connection: Connection) -> Step:
        try:
            source = connection["source"]
            sourceHandle = connection["sourceHandle"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
            # do we allow these keys to differ?
            # TODO: yes, we need a compatibility matrix. ~ Joris
            if sourceHandle != targetHandle:
                raise ValueError(
                    f"The output key {sourceHandle} does not match the input key {targetHandle}"
                )
            target_instance = self.all_steps[target]

            # Skip connection if already connected
            if target_instance.input_sources.get(targetHandle) == source:
                return target_instance

            # Delete old connection in graph if input source changes from existing connection
            old_source = target_instance.input_sources.get(targetHandle) 
            if old_source is not None:
                self.remove_graph_connection(old_source, target)

            target_instance.input_sources[targetHandle] = source
            if not self.graph.has_edge(source, target):
                self.graph.add_edge(source, target, n_connections=1)
            else:
                self.graph[source][target]["n_connections"] += 1

            return target_instance
        except KeyError as e:
            raise KeyError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle" + str(e)
            ) from e

    def remove_graph_connection(self, source_iid: str, target_iid: str) -> None:
        """
        Removes a connection between two steps. If multiple connections between these
        steps existed (i.e. 2+ outputs of source mapping to inputs on target), 
        the connetion counter is decremented. If no more such connections exist,
        the edge is deleted from the graph.

        :param source_iid: instance identifier of source step
        :param target_iid: instance identifier of target step
        """
        self.graph[source_iid][target_iid]["n_connections"] -= 1

        # Remove edge if no more connections exist
        if self.graph[source_iid][target_iid]["n_connections"] == 0:
            self.graph.remove_edge(source_iid, target_iid)

    def disconnect_steps(self, connection: Connection) -> Step:
        try:
            source = connection["source"]
            target = connection["target"]
            targetHandle = connection["targetHandle"]
        except KeyError as e:
            raise KeyError(
                "The supplied connection parameter does not adhere to the specification. Expected keys are source, sourceHandle, target and targetHandle"
            ) from e

        target_instance = self.all_steps.get(target)
        if target_instance is None:
            raise ValueError(f"No step with id {target} found")
        existing_source = target_instance.input_sources.get(targetHandle)
        if existing_source == source:
            self.remove_graph_connection(source, target)
            del target_instance.input_sources[targetHandle]
        return target_instance

    def get_edges(self) -> list[Connection]:
        """
        For front-end
        :return: List of connections between steps as interpretable by front-end
        """
        return [
            {
                "source": source,
                "sourceHandle": key,
                "target": step.instance_identifier,
                "targetHandle": key,
                "key": f"{source}->{step.instance_identifier}: {key}",
                "id": f"{source}->{step.instance_identifier}: {key}",
            }
            for step in self.all_steps.values()
            for key, source in step.input_sources.items()
        ]

    def _clear_succeeding_steps(self, step_id: StepID) -> None:
        """
        Voids outputs, messages and plots of all steps succeeding a given step
        :param step_iid: instance identifier of step of interest
        """
        for step in self.succeeding_steps(step_id):
            step.clear_generated_artifacts()

    ##
    ## Other methods
    ##

    def next_id_number(self) -> int:
        """
        Logical clock implementation for step instance identifier generation
        :return: The next instance identifier clock value
        """
        self._id_clock += 1
        return self._id_clock

    ##
    ## Deprecated stuff, B179: delete these when rewrite is complete
    ##

    @property
    @deprecated("Use the flat hierarchy .all_step_instances() instead")
    def sections(self) -> dict[Section, list[Step]]:
        """
        For front-end compatibility.

        :return: Dict mapping section titles to lists of step objects
        """
        return {section: [step for step in self.all_steps.values() if step.section == section] for section in Section}

    # TODO B179: make obsolete and delete
    # Left from old code and slightly adjusted to keep functionality as much as possible
    @deprecated("cringe")
    def get_instance_identifiers(
        self, step_type: type[Step], output_key: str | list[str] | None = None
    ) -> list[str]:
        if isinstance(output_key, str):
            output_key = [output_key]

        instance_identifiers = [
            step.instance_identifier
            for step in self.all_steps.values()
            if isinstance(step, step_type)
            and (output_key is None or all(k in step.output for k in output_key))
        ]
        if not instance_identifiers:
            logging.warning(
                f"No instance identifiers found with step type {step_type} and output_key{'s' if len(output_key) > 1 else ''} {output_key}"
            )
        return instance_identifiers

    # TODO WTAF is this?
    # It only makes sense in the context in which it is used,
    # which is a stupid context that will be deprecated with B179.
    # Looking forward to it @Tarek
    @staticmethod
    def check_instance_identifier(step: Step, instance_identifier: str | None):
        return (
            step.instance_identifier == instance_identifier
            or instance_identifier is None
        )

    # TODO B179
    @property
    def protein_df(self) -> pd.DataFrame:
        return self.get_step_output(output_key="protein_df")

    # TODO B179
    @property
    def metadata_df(self) -> pd.DataFrame | None:
        return self.get_step_output(output_key="metadata_df")
