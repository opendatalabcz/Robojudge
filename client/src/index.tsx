import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

import { ThemeProvider, createTheme } from "@mui/material";

const theme = createTheme({
  palette: {
    primary: {
      main: "#597081",
    },
  },
  typography: {
    fontFamily: 'Noto Serif'
  },
});

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement,
);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
