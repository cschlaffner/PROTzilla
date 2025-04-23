import "@mui/material/styles";

declare module "@mui/material/styles" {
  interface Mixins {
    MuiDataGrid: {
      containerBackground: string;
    };
  }
  interface MixinsOptions {
    MuiDataGrid?: {
      containerBackground?: string;
    };
  }

  interface Components {
    MuiDataGrid?: {
      styleOverrides?: {
        root?: Record<string, React.CSSProperties>;
      };
    };
  }
}

declare module "plotly.js-dist";
declare module "plotly.js-dist-min";
declare module "file-saver";
