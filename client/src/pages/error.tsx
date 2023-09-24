import React from "react";
import { Typography } from "@mui/material";

const styles = {
  errorPage: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
};

export function ErrorPage() {
  return (
    <div style={styles.errorPage}>
      <Typography variant="h6" margin="1rem">
        Nastala neočekávaná chyba. Zkuste prosím akci zopakovat, případně
        kontaktovat správce aplikace.
      </Typography>
    </div>
  );
}
