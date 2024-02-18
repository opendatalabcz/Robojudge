import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Button, Card, CardContent, TextField, Tooltip, Typography } from "@mui/material";
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

type InfoProps = {
  triggerAlert: (text: string) => void;
};

export function Info({ triggerAlert }: InfoProps) {
  const [caseDescription, setCaseDescription] = useState("");
  const [cases, setCases] = useState<Case[]>([]);

  const [isLoading, setIsLoading] = useState(false);


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
              Aplikace vznikla jako součást bakalářského projektu na <a href="https://fit.cvut.cz/cs">Fakultě informačních technologií ČVUT</a> ve spolupráci s <a href="https://opendatalab.cz/">OpenDataLab</a>.
              <br />
              <br />
              Cílem práce bylo vytvořit webovou aplikaci, která využije LLM (Large Language Model) modely k analýze získaných soudních rozsudků a zobrazí výsledky prostřednictvím webového rozhraní. Aplikace je schopna vyhledávat předchozí soudní rozhodnutí na základě zadaného popisu případu, který se týká podobné problematiky. Výstupem aplikace jsou shrnutí nejpodobnějších případů a odkazy na jejich celý text. Aplikace také nabízí možnost dotazovat se na obsah konkrétního rozhodnutí, odpověď je generována pomocí LLM.
              <br />
              <br />
              Tvůrce aplikace neodpovídá za správnost či úplnost zpracovaných rozhodnutí a nenese odpovědnost za újmu způsobenou v souvislosti s použitím informací získaných z této aplikace.
              <br />
              <br />
              <Typography padding="0.5rem" noWrap variant="h5" component="div">
                Příklady dotazů
              </Typography>
              <ul>
                <li></li>
                <li></li>
                <li></li>
              </ul>
            </CardContent>
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
