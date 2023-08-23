import React from "react";
import { formatDate } from "../utils/dateFormatter";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Card, CardContent, Typography } from "@mui/material";
import { Case } from "../pages/home";

const styles = {
  caseCard: {
    minHeight: "350px",
    padding: "1rem",
  },
  caseCardHeader: {
    display: "flex",
    justifyContent: "space-between",
  },
};

export type CardCardProps = {
  courtCase: Case;
};

export const CaseCard = ({ courtCase }: CardCardProps) => {
  return (
    <Grid2 xs={12} md={6}>
      <Card style={styles.caseCard} variant="outlined">
        <CardContent>
          <div style={styles.caseCardHeader}>
            <Typography gutterBottom variant="h5" component="div">
              {(courtCase.metadata?.jednaciCislo as string) ?? ""}
            </Typography>
            <span>
              {formatDate((courtCase.metadata.sentenceDate as string) ?? "")}
            </span>
          </div>
          <Typography>{(courtCase.metadata?.court as string) ?? ""}</Typography>
          {/* TODO: improve typograhy */}
          <Typography>
            {((courtCase.metadata?.keywords as Array<string>) ?? []).join(", ")}
          </Typography>
          <Typography>{courtCase.summary}</Typography>
          <a
            href={`${process.env.REACT_APP_JUSTICE_URL}/${courtCase.id}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Celý text
          </a>
        </CardContent>
      </Card>
    </Grid2>
  );
};
