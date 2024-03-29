import React from "react";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";

import { SERVER_URL } from "../utils/consts";

export function Api() {
  return (
    <>
      <Grid2 container>
        <iframe
          style={{ width: "100%", height: "calc(100vh - 125px)" }}
          src={SERVER_URL + "/docs"}
        ></iframe>
      </Grid2>
    </>
  );
}
