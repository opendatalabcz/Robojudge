import { ThemeProvider, createTheme } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import React from "react";

import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

export const theme = createTheme({
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
      <LocalizationProvider dateAdapter={AdapterDayjs} adapterLocale='cz'>
        <App />
      </LocalizationProvider>
    </ThemeProvider>
  </React.StrictMode>,
);
