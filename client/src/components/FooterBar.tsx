import React from "react";
import { AppBar } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";

export function FooterBar() {
  return (
    <AppBar position="relative" style={{ background: "white" }}>
      <Grid2
        style={{
          paddingRight: "1em",
          display: "flex",
          justifyContent: "flex-end",
          gap: "1em",
          alignItems: "center",
        }}
      >
        <a href="https://fit.cvut.cz/cs">
          <img src="/fit-cvut-logo-cs.svg" style={{ width: "100px" }} />
        </a>
        <a href="https://github.com/opendatalabcz/Robojudge">
          <img src="/github-logo-black.svg" style={{ width: "30px" }} />
        </a>
        <a href="https://opendatalab.cz/">
          <img src="/opendatalab-logo.png" style={{ width: "55px" }} />
        </a>
      </Grid2>
    </AppBar>
  );
}
