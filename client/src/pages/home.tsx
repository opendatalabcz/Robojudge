import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Button, Card, CardContent, Collapse, TextField, Tooltip, Typography } from "@mui/material";
import { CaseCard } from "../components/CaseCard";
import { LoadingOverlay } from "../components/LoadingOverlay";

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

const DEFAULT_HELPER_TEXT = `Zadejte popis případu, pro který chcete najít již rozhodnuté
                  případy podobné. Nejlepších výsledků dosáhnete zadáním 100 a více
                  znaků. Databáze momentálně obsahuje pouze rozhodnutí civilních soudů v 1. stupni (viz "INFO").`;

const MIN_DESCRIPTION_LENGTH = 20;
const MAX_DESCRIPTION_LENGTH = 500;

const INPUT_TOO_SHORT = `Zadejte prosím delší popis případu (aspoň ${MIN_DESCRIPTION_LENGTH} znaků).`;
const INPUT_TOO_LONG = `Zadejte prosím maximálně ${MAX_DESCRIPTION_LENGTH} znaků.`;

export const SERVER_URL = process.env.REACT_APP_SERVER_URL ?? "http://localhost:4000"

type HomeProps = {
  triggerAlert: (text: string) => void;
};

export function Home({ triggerAlert }: HomeProps) {
  const [caseDescription, setCaseDescription] = useState("");
  const [cases, setCases] = useState<Case[]>([]);

  const [isLoading, setIsLoading] = useState(false);

  const [isInputInvalid, setIsInputInvalid] = useState(true);
  const [tooltipText, setTooltipText] = useState(INPUT_TOO_SHORT);

  const [queryRelevanceExplanation, setQueryRelevanceExplanation] = useState('');

  const handleTextInputChange = (value: string) => {
    if (value.length < MIN_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_SHORT);
    } else if (value.length > MAX_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_LONG);
    } else {
      setIsInputInvalid(false);
      setTooltipText("");
    }
    setCaseDescription(value);
  };

  const searchForCases = async () => {
    if (caseDescription.length < MIN_DESCRIPTION_LENGTH) {
      setTooltipText(INPUT_TOO_SHORT);
      return;
    } else if (caseDescription.length > MAX_DESCRIPTION_LENGTH) {
      setTooltipText(INPUT_TOO_LONG);
      return;
    }

    try {
      setIsLoading(true);
      setQueryRelevanceExplanation('');

      const { data } = await axios.post(
        SERVER_URL
        + '/cases/search',
        {
          query_text: caseDescription,
          limit: process.env.REACT_APP_NUMBER_OF_SEARCH_RESULTS ?? 5,
          generate_summaries: true,
        },
      );

      const cases = data['cases'];
      setCases(cases.map(convertObjectKeysToCamelCase));
      if (!data['relevance']) {
        setQueryRelevanceExplanation(data['reasoning'])
      }
    } catch (err) {
      console.error(err);
      triggerAlert(
        "Při vytváření shrnutí nastala chyba. Opakujte prosím akci za chvíli.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {isLoading ? <LoadingOverlay /> : null}
      <Grid2
        container
        style={{ padding: "1rem", opacity: isLoading ? 0.6 : 1 }}
      >
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={styles.searchCard}>
            <CardContent>
              <Grid2>
                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={5}
                  value={caseDescription}
                  onChange={(e) => handleTextInputChange(e.target.value)}
                  label="Popis případu"
                  helperText={DEFAULT_HELPER_TEXT}
                ></TextField>
              </Grid2>
              <Grid2 style={{ display: "flex", justifyContent: "flex-end" }}>
                <Tooltip title={tooltipText} placement="bottom">
                  {/* The tooltip will not display on disabled elements otherwise */}
                  <div>
                    <Button
                      onClick={searchForCases}
                      disabled={isLoading || isInputInvalid}
                      variant="outlined"
                    >
                      Hledat
                    </Button>
                  </div>
                </Tooltip>
              </Grid2>
            </CardContent>
            <Collapse in={!!queryRelevanceExplanation} timeout="auto">
              <div style={{ margin: 'auto', textAlign: 'center' }}>
                <Typography variant="subtitle2"
                >{queryRelevanceExplanation}</Typography>
              </div>
            </Collapse>
          </Card>
        </Grid2>
      </Grid2>
      <Grid2
        container
        spacing={4}
        style={{ margin: "1rem", opacity: isLoading ? 0.6 : 1 }}
      >
        {cases.map((courtCase) => (
          <CaseCard
            key={courtCase.caseId}
            courtCase={courtCase}
            triggerAlert={triggerAlert}
          />
        ))}
      </Grid2>
    </>
  );
}
