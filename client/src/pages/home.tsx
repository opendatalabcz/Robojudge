import { Card, CardContent, Collapse } from "@mui/material";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import axios from "axios";
import React, { useEffect, useState } from "react";

import { TransitionGroup } from "react-transition-group";

import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import { CaseCard } from "../components/CaseCard";
import {
  EMPTY_FILTER_ALERT,
  FETCH_SUMMARIES_ERROR_ALERT,
  INPUT_TOO_LONG,
  INPUT_TOO_SHORT,
  MAX_DESCRIPTION_LENGTH,
  MIN_DESCRIPTION_LENGTH,
  SERVER_URL,
  TOO_MANY_QUERIES_ALERT,
} from "../utils/consts";
import { Case } from "../utils/types";
import { SearchInput } from "../components/SearchInput";
import { ExpandedSearch } from "../components/ExpandedSearch";
import { Dayjs } from "dayjs";
import { ShowMoreButton } from "../components/ShowMoreButton";
import { SearchButton } from "../components/SearchButton";

export const styles = {
  searchCard: {
    padding: "1.5rem",

    maxWidth: "800px",
    minWidth: "250px",
  },
  caseCardsContainer: {
    display: "flex",
    gap: "30px",
    width: "100%",
  },
  casesTransitionGroup: {
    width: "100%",
    margin: "1rem",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
} as Record<string, React.CSSProperties>;

const RESULTS_COUNT =
  Number(process.env.REACT_APP_NUMBER_OF_SEARCH_RESULTS) || 5;

type HomeProps = {
  triggerAlert: (text: string) => void;
};

export function Home({ triggerAlert }: HomeProps) {
  const [caseDescription, setCaseDescription] = useState("");
  const [cases, setCases] = useState<Case[]>([]);

  const [sentenceDateFrom, setSentenceDateFrom] = useState<null | Dayjs>(null);
  const [sentenceDateTo, setSentenceDateTo] = useState<null | Dayjs>(null);

  const [publicationDateFrom, setPublicationDateFrom] = useState<null | Dayjs>(
    null,
  );
  const [publicationDateTo, setPublicationDateTo] = useState<null | Dayjs>(
    null,
  );

  const [isLoading, setIsLoading] = useState(false);

  const [isInputInvalid, setIsInputInvalid] = useState(true);
  const [tooltipText, setTooltipText] = useState(INPUT_TOO_SHORT);

  const [casesPage, setCasesPage] = useState(0);
  const [maxCasesPage, setMaxCasesPage] = useState(0);

  useEffect(() => {
    if (caseDescription.length < MIN_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_SHORT);
    } else if (caseDescription.length > MAX_DESCRIPTION_LENGTH) {
      setIsInputInvalid(true);
      setTooltipText(INPUT_TOO_LONG);
    } else {
      setIsInputInvalid(false);
      setTooltipText("");
    }
  }, [caseDescription]);

  const searchForCases = async () => {
    setMaxCasesPage(0);
    setCases([]);
    await fetchCases(0);
  };

  const createSkeletons = (skeletonCount: number = RESULTS_COUNT) => {
    const caseSkeletons = [];
    for (let i = 0; i < skeletonCount; i++) {
      caseSkeletons.push({ isLoading: true, metadata: {} });
    }
    return caseSkeletons;
  };

  const createFilters = () => {
    return {
      publication_date_from:
        publicationDateFrom?.format("YYYY-MM-DD") ?? undefined,
      publication_date_to: publicationDateTo?.format("YYYY-MM-DD") ?? undefined,
      sentence_date_from: sentenceDateFrom?.format("YYYY-MM-DD") ?? undefined,
      sentence_date_to: sentenceDateTo?.format("YYYY-MM-DD") ?? undefined,
    };
  };

  const fetchCases = async (currentPage = 0) => {
    try {
      setIsLoading(true);
      setCases((cases) => [...cases, ...createSkeletons()]);

      const filters = createFilters();

      const { data } = await axios.post(SERVER_URL + "/rulings/search", {
        query_text: caseDescription,
        page_size: RESULTS_COUNT,
        current_page: currentPage,
        generate_summaries: true,
        filters,
      });

      const { cases: casesRaw, max_page: maxPage, relevance, reasoning } = data;

      setCases((cases) => [
        ...cases.slice(0, -RESULTS_COUNT), // Remove the skeletons
        ...casesRaw.map(convertObjectKeysToCamelCase),
      ]);

      if (!relevance) {
        triggerAlert(reasoning);
        return;
      } else if (!casesRaw.length) {
        triggerAlert(EMPTY_FILTER_ALERT);
        return;
      }

      setMaxCasesPage(maxPage);
      setCasesPage(currentPage + 1);
    } catch (err) {
      console.error(err);

      if (err?.response?.status == 429) triggerAlert(TOO_MANY_QUERIES_ALERT);
      else triggerAlert(FETCH_SUMMARIES_ERROR_ALERT);

      setCases((cases) => [...cases.slice(0, -RESULTS_COUNT)]); // Remove the skeletons
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Grid2 container style={{ padding: "1rem" }}>
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={styles.searchCard}>
            <CardContent style={{ padding: 0 }}>
              <SearchInput
                isLoading={isLoading}
                caseDescription={caseDescription}
                setCaseDescription={setCaseDescription}
              />

              <ExpandedSearch
                sentenceDateFrom={sentenceDateFrom}
                sentenceDateTo={sentenceDateTo}
                publicationDateFrom={publicationDateFrom}
                publicationDateTo={publicationDateTo}
                setSentenceDateFrom={setSentenceDateFrom}
                setSentenceDateTo={setSentenceDateTo}
                setPublicationDateFrom={setPublicationDateFrom}
                setPublicationDateTo={setPublicationDateTo}
              />

              <SearchButton
                tooltipText={tooltipText}
                isButtonDisabled={isLoading || isInputInvalid}
                searchCases={searchForCases}
              />
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
      <Grid2 container spacing={4} style={{ margin: 0 }}>
        <TransitionGroup
          style={{
            ...styles.casesTransitionGroup,
            opacity: isLoading ? 0.6 : 1,
          }}
        >
          {cases.map((courtCase, index) => (
            <Collapse key={index} style={{ width: "100%" }}>
              <CaseCard courtCase={courtCase} triggerAlert={triggerAlert} />
            </Collapse>
          ))}
        </TransitionGroup>
      </Grid2>
      <ShowMoreButton
        searchMoreCases={async () => fetchCases(casesPage)}
        isButtonShowed={
          caseDescription &&
          casesPage > 0 &&
          casesPage < maxCasesPage &&
          !isLoading
        }
      />
    </>
  );
}
