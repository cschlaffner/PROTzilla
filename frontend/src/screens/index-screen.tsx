import React, { useEffect, useState } from "react";
import { Col, Container, Row } from "react-grid-system";

import { Button, Card, Dropdown, TextField } from "../components";
import "bootstrap/dist/css/bootstrap.min.css";
import { defaultPalette } from "../theme";
import { callApi, callApiWithParameters } from "../utils";

export const IndexScreen: React.FC = () => {
  const [newRunName, setNewRunName] = useState("");
  const [workflow, setWorkflow] = useState("standard");
  const [memoryMode, setMemoryMode] = useState("standard");
  const [existingRun, setExistingRun] = useState("nothing here yet");
  const [runs, setRuns] = useState<{ value: string; label: string }[]>([
    { value: "run", label: "run" },
  ]);
  const [title, setTitle] = useState("Loading...");

  useEffect(() => {
    const fetchData = async () => {
      const data = await callApi("step_name_list");
      if (data) {
        setTitle(data);
      }
    };

    void fetchData();
  }, []);

  const handleCreateRun = () => {
    if (runs.some((run: { value: string }) => run.value === newRunName)) {
      alert("A run with this name already exists!");
      return;
    }
    setRuns([...runs, { value: newRunName, label: newRunName }]);
    setNewRunName("");
    console.log(runs);
    void callApiWithParameters("add_run/", {
      run_name: newRunName,
      workflow_name: "standard",
      df_mode_name: "disk_memory",
    });
  };

  const handleContinueRun = () => {
    console.log("Continue Run:", existingRun);
  };

  const handleDeleteRun = () => {
    setRuns(runs.filter((run: { value: string }) => run.value !== existingRun));
    setExistingRun(runs[0]?.value || "");
    console.log(runs);
  };

  return (
    <div className="min-vh-100 w-100 bg-light">
      <header
        style={{
          backgroundColor: defaultPalette.primary, // Verwendung der Theme-Farbe
          color: defaultPalette.onPrimary,
        }}
        className=" text-white py-3 px-4 d-flex justify-content-between align-items-center"
      >
        <h1 className="h4 mb-0">PROTzilla</h1>
        <a href="https://github.com" className="text-white">
          GitHub
        </a>
      </header>
      <Container>
        <Row
          gutterWidth={16}
          justify="between"
          align="center"
          style={{ height: "80vh" }}
        >
          <Col md={4}>
            <Card title="Work on a new run:">
              <TextField
                label="Add run name:"
                placeholder="Enter run name"
                value={newRunName}
                onChange={(e) => {
                  setNewRunName(e.target.value);
                }}
                className="mb-3"
              />
              <Dropdown
                label="With workflow:"
                options={[
                  { value: "standard", label: "Standard" },
                  { value: "example-workflow", label: "Example" },
                ]}
                value={workflow}
                onChange={(value) => {
                  setWorkflow(value);
                }}
                className="mb-3"
              />
              <Dropdown
                label="Memory mode:"
                options={[
                  { value: "standard", label: "Standard" },
                  { value: "low-memory", label: "Low Memory" },
                ]}
                value={memoryMode}
                onChange={(value) => {
                  setMemoryMode(value);
                }}
                className="mb-3"
              />
              <Button
                className="btn btn-primary w-100"
                onClick={handleCreateRun}
              >
                Create
              </Button>
            </Card>
          </Col>
          {/* Continue Run Section */}
          <Col md={4}>
            <Card title="Continue an existing run:">
              <Dropdown
                label="Select run:"
                options={runs}
                value={existingRun}
                onChange={(value) => {
                  setExistingRun(value);
                }}
                className="mb-3"
              />
              <Button
                className="btn btn-primary w-100 mb-2"
                onClick={handleContinueRun}
              >
                Continue
              </Button>
              <Button
                className="btn btn-primary w-100 mb-2"
                onClick={() =>
                  void callApiWithParameters("delete_tag/", {
                    run_name: "BingChilling",
                    tag_name: "test",
                  })
                }
              >
                Delete Tag: test
              </Button>
              <Button className="btn btn-secondary w-100">
                Manage databases
              </Button>
            </Card>
          </Col>

          {/* Delete Run Section "Delete an existing run:"*/}
          <Col md={4}>
            <Card title={title}>
              <Dropdown
                label="Select run:"
                options={runs}
                value={existingRun}
                onChange={(value) => {
                  setExistingRun(value);
                }}
                className="mb-3"
              />
              <Button
                className="btn btn-danger w-100"
                onClick={handleDeleteRun}
              >
                Delete
              </Button>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
};
