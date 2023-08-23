import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import {
  Button,
  Card,
  CardContent,
  CircularProgress,
  TextField,
  Typography,
} from "@mui/material";
import { CaseCard } from "../components/CaseCard";

export type Case = {
  id: string;
  summary: string;
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
};

const DEFAULT_HELPER_TEXT = `Zadejte popis případu, pro který chcete najít již rozhodnuté
                  případy podobné. Nejlepších výsledků dosáhnete zadáním ca. 200
                  znaků a použitím právní terminologie.`;

const MIN_DESCRIPTION_LENGTH = 20;
const MAX_DESCRIPTION_LENGTH = 500;

const INPUT_TOO_SHORT = `Zadejte prosím delší popis případu (aspoň ${MIN_DESCRIPTION_LENGTH} znaků).`;
const INPUT_TOO_LONG = `Zadejte prosím maximálně ${MAX_DESCRIPTION_LENGTH} znaků.`;

export function Home() {
  const [caseDescription, setCaseDescription] = useState("");
  const [cases, setCases] = useState<Case[]>([]);

  const [isLoading, setIsLoading] = useState(false);

  const [helperText, setHelperText] = useState(DEFAULT_HELPER_TEXT);

  const handleTextInputChange = (value: string) => {
    if (value.length == 0) setHelperText(DEFAULT_HELPER_TEXT);
    setCaseDescription(value);
  };

  const searchForCases = async () => {
    if (caseDescription.length < MIN_DESCRIPTION_LENGTH) {
      setHelperText(INPUT_TOO_SHORT);
      return;
    } else if (caseDescription.length > MAX_DESCRIPTION_LENGTH) {
      setHelperText(INPUT_TOO_LONG);
      return;
    }

    try {
      setIsLoading(true);

      const { data } = await axios.post(
        `${process.env.REACT_APP_SERVER_URL ?? ""}/summary/search`,
        {
          query_text: caseDescription,
          limit: process.env.REACT_APP_NUMBER_OF_SEARCH_RESULTS ?? 5,
        },
      );

      console.log(data.map(convertObjectKeysToCamelCase));

      setCases(data.map(convertObjectKeysToCamelCase));
      setIsLoading(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      {isLoading ? (
        <div
          style={{
            position: "absolute",
            display: "flex",
            justifyContent: "center",
            flexDirection: "column",
            alignItems: "center",
            width: "100%",
            height: "100%",
            zIndex: 1,
          }}
        >
          <CircularProgress />
          <Typography variant="body2" color="text.secondary">
            Hledám rozhodnutí a připravuji shrnutí...
          </Typography>
        </div>
      ) : null}
      <Grid2
        container
        style={{ padding: "1rem", opacity: isLoading ? 0.6 : 1 }}
      >
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={styles.searchCard}>
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                RoboJudge
              </Typography>

              <Grid2>
                {/*  TODO: test the optimal number of words */}
                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={5}
                  value={caseDescription}
                  onChange={(e) => handleTextInputChange(e.target.value)}
                  helperText={helperText}
                  error={helperText !== DEFAULT_HELPER_TEXT}
                ></TextField>
              </Grid2>
              <Button
                style={{ float: "right" }}
                onClick={searchForCases}
                disabled={isLoading}
              >
                Hledat
              </Button>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
      <Grid2 container spacing={3} style={{ padding: "1rem" }}>
        {cases.map((courtCase) => (
          <CaseCard key={courtCase.id} courtCase={courtCase} />
        ))}
      </Grid2>
    </>
  );
}
