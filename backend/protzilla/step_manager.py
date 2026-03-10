from __future__ import annotations
from typing import TYPE_CHECKING, Any
import pandas as pd

if TYPE_CHECKING:
    from backend.protzilla.disk_operator import DiskOperator

from backend.protzilla.steps import Step, Section, Output
from backend.protzilla.constants.data_types import (
    Connection,
    DataKey,
    StepID,
    parse_connection,
)

import networkx as nx


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
        *,
        disk_operator: DiskOperator,
        df_mode: str = "disk",
    ):
        self.df_mode: str = df_mode
        self.disk_operator: DiskOperator = disk_operator

        # Saves all steps, accessible by their instance identifiers
        self.all_steps: dict[StepID, Step] = {}

        # Graph saving connections between steps.
        # All steps are represented by their instance_identifiers as nodes.
        # The edges specify which source/target handles (or outputs/inputs)
        # they refer to as a dict {"source_handle": <>, "target_handle": <>}
        # in their data attribute
        self.graph: nx.MultiDiGraph[StepID] = nx.MultiDiGraph()

        # Instance identifier of the currently selected step
        self._current_selected_step_id: StepID | None = None

        # Logical clock for instance identifier creation.
        # May only be accessed via next_id_number
        self._id_clock: int = 0

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
        return [self.all_steps[step_id] for step_id in descendant_ids]

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

    def incoming_edges_for_handle(
        self,
        source: StepID | None,
        source_handle: DataKey | None,
        target: StepID,
        target_handle: DataKey,
    ) -> list[tuple[StepID, StepID, int, dict[str, str]]]:
        """
        Helper function that allows retrieving all incoming connections for a given target node and target_handle.
        Allows optionally passing a source and source_handle for further filtering

        :param source: ID of a source node (optional)
        :param source_handle: handle of the source (optional)
        :param target: ID of the target node
        :param target_handle: the connection handle of the target
        :return: list of edges (ebunch) - should never be more than one, but we return a list just in case
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

        self._current_selected_step_id = step_id

        # TODO: We'll keep this for now, but I assume this is unneccessary
        if self.df_mode == "disk":
            self.disk_operator._write_output(self.current_step)


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
        must_goto_fallback = False
        try:
            self.previous_step()
        except ValueError:  # No previous step
            must_goto_fallback = True

        self.graph.remove_node(step_id)
        del self.all_steps[step_id]

        if must_goto_fallback:
            self.goto_step(self.fallback_step_id)

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

        # Abort if the exact connection is already present
        if self.incoming_edges_for_handle(source, source_handle, target, target_handle):
            return

        # Abort if connection creates cycle
        probe_graph = self.graph.copy()
        probe_graph.add_edge(source, target)
        if not nx.is_directed_acyclic_graph(probe_graph):
            raise ValueError(
                "The connection you try to add would lead to a circular dependency. Circular dependencies are not permitted."
            )

        # retrieve all incoming edges to the target
        old_edges = self.incoming_edges_for_handle(None, None, target, target_handle)

        # Delete any existing connection to the target handle that isn't equal to the current one
        self.graph.remove_edges_from(old_edges)  # pyright: ignore[reportArgumentType].

        self.graph.add_edge(
            source, target, source_handle=source_handle, target_handle=target_handle
        )

    def disconnect_steps(self, connection: Connection) -> None:
        source, source_handle, target, target_handle = parse_connection(connection)
        # retrieve edges that have exactly this combination of source, target and handles
        edges = self.incoming_edges_for_handle(
            source, source_handle, target, target_handle
        )
        if not edges:
            raise ValueError(
                f"No connection from {source}.{source_handle} to {target}.{target_handle} found"
            )
        # pyright is wrong here - it expects 3-tuples (u, v, data) like for a DiGraph
        # but since we have a MultiDiGraph, our edges are of format (u, v, key, data)
        self.graph.remove_edges_from(edges)  # pyright: ignore[reportArgumentType]

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
                "key": f"{source}:{data['source_handle']}->{target}:{data['target_handle']}",
                "id": f"{source}:{data['source_handle']}->{target}:{data['target_handle']}",
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
    ## Input/Output accessors
    ##

    def get_step_output(
        self,
        output_key: str,
        instance_identifier: StepID,
    ) -> pd.DataFrame | Any | None:
        """
        Get the specific output of the outputs of a specific step type. The step type can also a parent class of the
        step type, in which case the output of the most recent step of the specific type is returned.

        :param output_key: The key of the desired output in the output dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the output from
        :return: The value of the output of the step or None
        """

        step = self.get_step_by_id(instance_identifier)
        try:
            return step.output[output_key]
        # TODO: this is really ugly, but Output does not have a .get() method
        except KeyError:
            return None

    def get_step_input(
        self,
        input_key: DataKey,
        instance_identifier: StepID,
    ):
        """
        Get the specific input from the step with the given instance_identifier.

        :param input_key: The key of the desired input in the input dictionary of the step
        :param instance_identifier: The instance identifier of the step to get the input from
        :return: The value of the input of the step or None
        """

        step = self.get_step_by_id(instance_identifier)

        return step.inputs.get(input_key)

    def get_step_operation(self, step_id: str) -> str:
        try:
            return self.all_steps[step_id].operation
        except (
            KeyError
        ):  # TODO: Should really not happen and should be caught in a different way
            raise ValueError(f"No step associated with ID {step_id}")
