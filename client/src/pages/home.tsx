import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import {
  Button,
  Card,
  CardContent,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { css } from '@emotion/react';
import { CaseCard } from "../components/CaseCard";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { FloatingAlert } from "../components/FloatingAlert";

export type Case = {
  id: string;
  summary: string;
  metadata: Record<string, unknown>;
  reasoning: string;
  verdict: string;
};

// TODO: disuse emotion
const styles = {
  searchCard: css`
    padding: "1rem";
    maxWidth: "750px";
    minWidth: "50vw";
  `,
  caseCardsContainer: css`
    display: "flex";
    gap: "30px";
    width: "100%";
  `,

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
  const [isErrorAlertShown, setIsErrorAlertShown] = useState(false);

  const [isInputInvalid, setIsInputInvalid] = useState(true);
  const [tooltipText, setTooltipText] = useState(INPUT_TOO_SHORT);

  const handleTextInputChange = (value: string) => {
    if (value.length < MIN_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_SHORT);
    } else if (value.length > MAX_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_LONG);
    } else {
      setIsInputInvalid(false);
      setTooltipText('')
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

      const { data } = await axios.post(
        `${process.env.REACT_APP_SERVER_URL ?? ""}/summary/search`,
        {
          query_text: caseDescription,
          limit: process.env.REACT_APP_NUMBER_OF_SEARCH_RESULTS ?? 5,
        },
      );

      setCases(data.map(convertObjectKeysToCamelCase));
    } catch (err) {
      console.error(err);
      setIsErrorAlertShown(true);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <FloatingAlert isShown={isErrorAlertShown} setShown={setIsErrorAlertShown} text="Při vytváření shrnutí nastala chyba. Opakujte prosím akci za chvíli." />

      {isLoading ? (
        <LoadingOverlay />
      ) : null
      }
      <Grid2
        container
        style={{ padding: "1rem", opacity: isLoading ? 0.6 : 1 }}
      >
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card css={styles.searchCard}>
            <CardContent>
              <Typography gutterBottom variant="h5" component="div">
                RoboJudge
              </Typography>

              <Grid2>
                <TextField
                  fullWidth
                  multiline
                  minRows={2}
                  maxRows={5}
                  value={caseDescription}
                  onChange={(e) => handleTextInputChange(e.target.value)}
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
                    >
                      Hledat
                    </Button>
                  </div>
                </Tooltip>
              </Grid2>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
      <Grid2
        container
        spacing={3}
        style={{ margin: "1rem", opacity: isLoading ? 0.6 : 1 }}
      >
        {cases.map((courtCase) => (
          <CaseCard key={courtCase.id} courtCase={courtCase} />
        ))}
      </Grid2>
    </>
  );
}
