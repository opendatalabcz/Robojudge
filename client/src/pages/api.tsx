import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Button, Card, CardContent, TextField, Tooltip, Typography } from "@mui/material";
import { CaseCard } from "../components/CaseCard";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { SERVER_URL } from "./home";

export type Case = {
  caseId: string;
  summary: string;
  title: string;
  metadata: Record<string, unknown>;
  reasoning: string;
  verdict: string;
};

const styles = {
  searchCard: {
    padding: "1rem",
    maxWidth: "750px",
    minWidth: "50vw",
  },
  caseCardsContainer: {
    display: "flex",
    gap: "30px",
    width: "100%",
  },
} as Record<string, React.CSSProperties>;

type ApiProps = {
  triggerAlert: (text: string) => void;
};

export function Api({ triggerAlert }: ApiProps) {

  return (
    <>
      <Grid2
        container
      >
        <iframe style={{ width: '100%', height: 'calc(100vh - 125px)' }} src={SERVER_URL + '/docs'}></iframe>
      </Grid2>
    </>
  );
}
