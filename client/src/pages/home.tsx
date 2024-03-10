import React, { useRef, useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Button, Card, CardContent, Collapse, Fade, TextField, Tooltip, Typography, useTheme } from "@mui/material";
import { CaseCard } from "../components/CaseCard";
import { LoadingOverlay } from "../components/LoadingOverlay";
import { ArrowDropDown } from "@mui/icons-material";
import { TransitionGroup } from 'react-transition-group';

export type Case = {
  caseId: string;
  summary: string;
  title: string;
  metadata: Record<string, unknown>;
  reasoning: string;
  verdict: string;
  isLoading: boolean;
};

export const styles = {
  searchCard: {
    padding: "1rem",
    maxWidth: "800px",
    minWidth: "250px",
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

  const [casesPage, setCasesPage] = useState(0);
  const [maxCasesPage, setMaxCasesPage] = useState(0);

  const [queryRelevanceExplanation, setQueryRelevanceExplanation] = useState('');

  const bottomRef = useRef(null);

  const theme = useTheme()

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

  const searchForCases = async (currentPage = 0) => {
    if (caseDescription.length < MIN_DESCRIPTION_LENGTH) {
      setTooltipText(INPUT_TOO_SHORT);
      return;
    } else if (caseDescription.length > MAX_DESCRIPTION_LENGTH) {
      setTooltipText(INPUT_TOO_LONG);
      return;
    }

    const resultsCount = Number(process.env.REACT_APP_NUMBER_OF_SEARCH_RESULTS) ?? 5;
    try {

      const caseSkeletons = [];
      for (let i = 0; i < resultsCount; i++) {
        caseSkeletons.push({ isLoading: true, metadata: {} })
      }

      setIsLoading(true);
      setCases(cases => [...cases, ...caseSkeletons]);
      setQueryRelevanceExplanation('');

      const { data } = await axios.post(
        SERVER_URL
        + '/cases/search',
        {
          query_text: caseDescription,
          page_size: resultsCount,
          page: currentPage,
          generate_summaries: true,
        },
      );

      const casesRaw = data['cases'];
      setCases(cases => [...cases.slice(0, -resultsCount), ...casesRaw.map(convertObjectKeysToCamelCase)]);

      if (!data['relevance']) {
        setQueryRelevanceExplanation(data['reasoning'])
      }
      setMaxCasesPage(data['max_page'])
      setCasesPage(currentPage + 1)
    } catch (err) {
      console.error(err);

      if (err?.response?.status == 429)
        triggerAlert(
          "Zaslali jste příliš mnoho dotazů v krátkém čase. Opakujte prosím akci za chvíli.",
        );
      else
        triggerAlert(
          "Při vytváření shrnutí nastala chyba. Opakujte prosím akci za chvíli.",
        );

      setCases(cases => [...cases.slice(0, -resultsCount)])
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* {isLoading ? <LoadingOverlay /> : null} */}
      <Grid2
        container
        style={{ padding: "1rem" }}
      >
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={styles.searchCard}>
            <CardContent>
              <Grid2>
                <TextField
                  fullWidth
                  multiline
                  disabled={isLoading}
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
                      onClick={async () => {
                        setMaxCasesPage(0)
                        setCases([]);
                        await searchForCases(0)
                      }}
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
      <Grid2 container spacing={4} style={{ margin: 0 }}>
        <TransitionGroup style={{ width: "100%", margin: '1rem', opacity: isLoading ? 0.6 : 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }} >
          {
            cases.map((courtCase, index) => (
              <Collapse key={index} style={{ width: '100%' }}>
                <CaseCard
                  courtCase={courtCase}
                  triggerAlert={triggerAlert}
                />
              </Collapse>
            ))
          }
        </TransitionGroup >
      </Grid2 >
      <Fade in={casesPage > 0 && casesPage < maxCasesPage}>
        <div ref={bottomRef} style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center', cursor: 'pointer', margin: 'auto', width: '48px', height: '48px', marginTop: '2rem', }} onClick={async () => {
          await searchForCases(casesPage);
          // bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }}>
          <Typography variant="overline">Další</Typography>
          <ArrowDropDown style={{ fontSize: '8rem', marginTop: '-3.5rem', }} />
        </div>
      </Fade>
    </>
  );
}
