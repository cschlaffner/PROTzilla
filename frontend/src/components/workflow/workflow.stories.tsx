import { Workflow } from "./workflow";
import { WorkflowProps } from "./workflow.props";

export default {
  component: Workflow,
  workflow: "default",
  icon: "trashcan",
  onPress: { action: "pressed" },
};

export const workflow = (args: WorkflowProps): React.ReactNode => <Workflow {...args} />;
workflow.args = {
  icon: "add",
  workflow: "test_workflowsssssssssssuuuuuuuuuuuuuuuuuuuuuuppperlang",
  onPress: {},
};
