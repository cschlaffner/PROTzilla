from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pandas as pd

if TYPE_CHECKING:
    from backend.protzilla.disk_operator import DiskOperator

from backend.protzilla.steps import Step, Section, Output
from backend.protzilla.constants.data_types import (
    Connection,
    DataKeys,
    OutputLocator,
    StepID,
    parse_connection,
)

import networkx as nx
import logging


class StepManager:
    """
    Manages steps within a run.

    :ivar df_mode: keep DFs in memory or write on disk (note: probably not even used correctly)
    :ivar disk_operator: disk operator to manage dumping step data to disk
    :ivar all_steps: main database for all step instances, addressed by their IDs
    :ivar graph: MultiDiGraph representing connections between steps for easier management
    :ivar current_selected_step_id: ID of the currently selected step
    :ivar _id_clock: logical clock used for instance identifier creation
    """

    def __repr__(self):
        return f"StepManager with {str(len(self.all_steps))} steps: {str(self.all_step_ids_toposorted)}"

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
        self.graph: nx.MultiDiGraph[StepID] = nx.MultiDiGraph()

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
    ## Specific sets of steps/ids or step attributes by graph properties
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

    def step_is_terminal(self, step_id: StepID) -> bool:
        return int(self.graph.out_degree(step_id)) == 0

    def step_is_source(self, step_id: StepID) -> bool:
        return int(self.graph.in_degree(step_id)) == 0

    def calc_dependencies_met_for_step(self, step_id: StepID) -> bool:
        """
        Checks calculation status of all preceding steps in the graph.
        :return: True iff all preceding steps have been calculated
        """
        return all(
            [
                step.calculation_status == "complete"
                for step in self.preceding_steps(step_id)
            ]
        )

    def edges_with_exact_data(
        self,
        source: StepID | None,
        source_handle: DataKeys | None,
        target: StepID,
        target_handle: DataKeys,
    ) -> list[tuple[StepID, StepID, int, dict[str, str]]]:
        """
        Helper function that allows retrieving all incoming connections for a given target node and target_handle.
        Allows optionally passing a source and source_handle for further filtering

        :param source: ID of a source node (optional)
        :param source_handle: handle of the source (optional)
        :param target: ID of the target node
        :param target_handle: the connection handle of the target
        :return: list of edges (ebunch)
        """
        return [
            edge
            for edge in self.graph.in_edges(target, data=True, keys=True)
            # edge is a 4-tuple in the format (u, v, key, data)
            if edge[3]["target_handle"] == target_handle
            and (source is None or source == edge[0])
            and (source_handle is None or source_handle == edge[3]["source_handle"])
        ]

    ##
    ## Batch invalidation
    ##

    def invalidate_current_and_following_steps(self) -> int:
        """
        Invalidates the current step and all dependent/following steps.

        :return: the amount of invalidated steps
        """
        steps_to_remove = [self.current_step] + self.following_steps
        for step in steps_to_remove:
            step.invalidate()
        return len(steps_to_remove)

    def _clear_succeeding_steps(self, step_id: StepID) -> None:
        """
        Voids outputs, messages and plots of all steps succeeding a given step
        :param step_id: instance identifier of step of interest
        """
        for step in self.succeeding_steps(step_id):
            step.clear_generated_artifacts()

    ##
    ## "Current step" management and navigation info
    ##

    @property
    def previous_steps(self) -> list[Step]:
        return self.preceding_steps(self.current_selected_step_id)

    @property
    def following_steps(self) -> list[Step]:
        return self.succeeding_steps(self.current_selected_step_id)

    @property
    def previous_calculated_steps(self) -> list[Step]:
        return list(
            filter(
                lambda step: step.calculation_status == "complete", self.previous_steps
            )
        )

    @property
    def current_step(self) -> Step:
        return self.all_steps[self.current_selected_step_id]

    @property
    def current_operation(self) -> str:
        return self.current_step.operation

    @property
    def current_section(self) -> Section:
        return self.current_step.section

    @property
    def current_location(self) -> tuple[str, str, StepID]:
        return (
            self.current_section,
            self.current_operation,
            self.current_selected_step_id,
        )

    @property
    def is_at_terminal_step(self) -> bool:
        return self.step_is_terminal(self.current_selected_step_id)

    @property
    def is_at_source_step(self) -> bool:
        return self.step_is_source(self.current_selected_step_id)

    @property
    def fallback_step_id(self) -> StepID:
        """
        Used for automatic naviagtion if no sufficient step to navigate to exists (e.g. after deletion)

        :return: some available step (make no assumptions which one)
        """
        return list(self.all_steps.keys())[0]

    ##
    ## Navigation
    ##

    @property
    def recommended_next_step_id(self) -> StepID | None:
        """
        Mainly for front-end. Instance identifier of the next step to navigate to when pressing the "Next" button.

        :return: The recommended next step identifier or None if we are at a terminal step
        """
        if self.is_at_terminal_step:
            return None
        return list(self.graph.successors(self.current_selected_step_id))[0]

    def goto_step(self, step_id: StepID) -> None:
        """
        Go to a specific step in the workflow.
        :param step_id: The ID of the step to navigate to
        """
        if step_id not in self.all_steps:
            raise ValueError(f"Step {step_id} not found")

        # TODO: We'll keep this for now, but I assume this is unneccessary
        if self.df_mode == "disk":
            self.disk_operator._write_output(self.current_step)

        self._current_selected_step_id = step_id

    def next_step(self) -> None:
        """
        Go to the next step in the workflow. Depending on the df_mode, the dataframes of the previous output are
        replaced with the respective paths on the disk where they are saved to save memory.
        Note: Kept from legacy, not used by front-end but TODO to be used by runner

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
            next_step_id = self.recommended_next_step_id
            self._current_selected_step_id = next_step_id
        else:
            raise ValueError("Cannot go to the next step from a terminal step")

    def previous_step(self) -> None:
        """
        Go to the previous step in the workflow. If the previous step is in disk mode, the respective dataframes are
        loaded from disk and replaced in the output dictionary of the step.
        Note: Kept from legacy

        :return: None
        """
        if not self.is_at_source_step:
            prev_step_id = list(self.graph.predecessors(self.current_selected_step_id))[
                0
            ]
            self._current_selected_step_id = prev_step_id
        else:
            raise ValueError("Cannot go back from a step with no predecessors")

    ##
    ## Add/remove steps
    ##

    def add_step(self, step: Step) -> None:
        """
        Adds a step.

        :param step: The step instance to add
        :raises ValueError: If another step with the same ID is already present
        :raises ValueError: If the given step has no instance identifier
        :return: None
        """
        if step.instance_identifier in self.all_steps:
            raise ValueError(f"Step with ID {step.instance_identifier} already exists")

        if step.instance_identifier is None:
            raise ValueError("The given step has no instance identifier")

        self.all_steps[step.instance_identifier] = step

        # Reset current step if this is the only existing step
        if len(self.all_steps) == 1:
            self._current_selected_step_id = step.instance_identifier

        self.graph.add_node(step.instance_identifier)

    def remove_step(self, step_id: StepID) -> None:
        """
        Removes a step.
        :param step_id: instance identifier of the step to delete
        :raises ValueError: if there is no step with the given ID
        :raises ValueError: if the step to delete is the last step in the run
        """
        if step_id not in self.all_steps:
            raise ValueError(f"No step with id {str(step_id)} found")
        if len(self.all_steps) == 1:
            raise ValueError("At least one step must exist")

        # Note: this reproduces the old approach
        # It's questionable whether or not we need this
        self._clear_succeeding_steps(step_id)

        # Navigate to a predecessor if step was selected
        # Else navigate to a fallback option
        try:
            self.previous_step()
        except ValueError:  # No previous step
            self.goto_step(self.fallback_step_id)

        self.graph.remove_node(step_id)
        del self.all_steps[step_id]

    ##
    ## Connection management
    ##

    def connect_steps(self, connection: Connection) -> None:
        """
        Connects an output of one source step to an input of another target step.
        Creates/updates the corresponding link in the graph and sets the handles as edge data.

        :param connection: the connection to establish
        :return: the target step instance
        :raises KeyError: if the connection parameters are incorrect
        """
        source, source_handle, target, target_handle = parse_connection(connection)

        # TODO: We currently allow arbitrary connections between all kinds of input.
        # Technical restrictions would make this cleaner

        # retrieve all incoming edges to the target
        old_edges = self.edges_with_exact_data(None, None, target, target_handle)
        # Abort if the exact connection is already present
        for old_source, _, _, data in old_edges:
            if (
                old_source == source
                and data["source_handle"] == source_handle
                and data["target_handle"] == target_handle
            ):
                return

        # Abort if connection creates cycle
        probe_graph = self.graph.copy()
        probe_graph.add_edge(source, target)
        if not nx.is_directed_acyclic_graph(probe_graph):
            raise ValueError(
                "The connection you try to add would lead to a circular dependency. Circular dependencies are not permitted."
            )

        # Delete any existing connection to the target handle that isn't equal to the current one
        self.graph.remove_edges_from(old_edges)

        self.graph.add_edge(
            source, target, source_handle=source_handle, target_handle=target_handle
        )

    def disconnect_steps(self, connection: Connection) -> None:
        source, source_handle, target, target_handle = parse_connection(connection)
        # retrieve edges that have exactly this combination of source, target and handles
        edges = self.edges_with_exact_data(source, source_handle, target, target_handle)
        if not edges:
            raise ValueError(
                f"No connection from {source}.{source_handle} to {target}.{target_handle} found"
            )
        self.graph.remove_edges_from(edges)

    def get_edges(self) -> list[Connection]:
        """
        For front-end
        :return: List of connections between steps as interpretable by front-end
        """
        return [
            {
                "source": source,
                "sourceHandle": data["source_handle"],
                "target": target,
                "targetHandle": data["target_handle"],
                "key": f"{source}:{data['source_handle']}->{target}: {data['target_handle']}",
                "id": f"{source}:{data['source_handle']}->{target}: {data['target_handle']}",
            }
            for source, target, data in self.graph.edges(data=True)
        ]

    ##
    ## Step ID clock management
    ##

    def next_id_number(self) -> int:
        """
        Logical clock implementation for step instance identifier generation
        :return: The next instance identifier clock value
        """
        self._id_clock += 1
        return self._id_clock

    ##
    ## Deprecated stuff largely unchanged (thus bad), TODO B179: delete these when rewrite is complete
    ##

    def get_step_output(
        self,
        step_type: Step | None = None,
        output_key: str = "",  # TODO remove step_type and default empty string
        instance_identifier: StepID | None = None,
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

        if instance_identifier is not None:
            step = self.get_step_by_id(instance_identifier)
            return step.output[output_key]

        # TODO: legacy - check if any calls without an explicit instance_identifier remain
        for step in reversed(steps_to_search):
            if (
                StepManager.check_instance_identifier(step, instance_identifier)
                and output_key in step.output
            ):
                val = step.output[output_key]
                if val is None:
                    continue
                # TODO: when are outputs ever stored as paths?
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

    @property
    def sections(self) -> dict[Section, list[Step]]:
        """
        For front-end compatibility.

        :return: Dict mapping section titles to lists of step objects
        """
        return {
            section: [
                step for step in self.all_steps.values() if step.section == section
            ]
            for section in Section
        }

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

    # TODO B179: make obsolete and delete
    # Left from old code and slightly adjusted to keep functionality as much as possible
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

    def get_step_operation(self, step_id: str) -> str:
        try:
            return self.all_steps[step_id].operation
        except (
            KeyError
        ):  # TODO: Should really not happen and should be caught in a different way
            raise ValueError(f"No step associated with ID {step_id}")
