import { Row, Container, Col } from "react-grid-system";
import { Card, FlexColumn, Navbar, PlotComponent } from "./../components";
import { EditorCard, ContentCard } from "./../components";
import { data, useNavigate } from "react-router-dom";
import { lineHeight, spacing } from "../theme";

export const RunScreen: React.FC = () => {
    const navigate = useNavigate()


    // TEMPORÄR

    const plotData: Partial<Plotly.Data>[] = [
        {
          x: ["A", "B", "C", "D"],
          y: [10, 20, 30, 40],
          type: "bar",
          marker: { color: "purple" },
        },
      ];
      
      const plotLayout: Partial<Plotly.Layout> = {
        title: { text: "Title" },
        xaxis: {
          anchor: "y",
          domain: [0.0, 1.0],
          title: { text: "Categories" },
        },
        yaxis: {
          anchor: "x",
          domain: [0.0, 1.0],
          title: { text: "Values" },
        },
      };

      const plotComponent =  <PlotComponent data={plotData} layout={plotLayout} />

    return (
        <div>
            <Navbar
                allowRunEdit={true}
                title="New Run"
                onNavigateHome={() => navigate("/")}
                onOpenSettings={() => {}}
                onOpenHelp={() => {}}
            />
            <Container fluid style={{margin: 0}}>
                <Row align="stretch" style={{height: "85vh", paddingTop: '8px'}}>
                    <Col md={"content"}>
                        <EditorCard />
                    </Col>
                    <Col>
                        <ContentCard plotComponent={plotComponent}/>
                    </Col>
                </Row>
   
            </Container>
        </div>
    )
}