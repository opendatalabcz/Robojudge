import React, { useState } from "react";
import axios from "axios";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import { Button, Card, CardContent, TextField, Tooltip, Typography } from "@mui/material";
import { CaseCard } from "../components/CaseCard";
import { LoadingOverlay } from "../components/LoadingOverlay";

import { styles } from './home';

export type Case = {
  caseId: string;
  summary: string;
  title: string;
  metadata: Record<string, unknown>;
  reasoning: string;
  verdict: string;
};

type InfoProps = {
  triggerAlert: (text: string) => void;
};

export function Info({ triggerAlert }: InfoProps) {

  return (
    <>
      <Grid2
        container
        style={{ padding: "1rem" }}
      >
        <Grid2 xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={{ ...styles.searchCard, minWidth: '200px' }}>
            <CardContent>
              <div>
                <Typography noWrap variant="h4" component="div">
                  O aplikaci
                </Typography>
                <p>Aplikace vznikla jako součást bakalářského projektu na <a href="https://fit.cvut.cz/cs">Fakultě informačních technologií ČVUT</a> ve spolupráci s <a href="https://opendatalab.cz/">OpenDataLab</a>.</p>
                <p>Cílem práce bylo vytvořit webovou aplikaci, která využije LLM (Large Language Model) modely k analýze soudních rozsudků automaticky scrapovaných z webu justice.cz a zobrazí výsledky prostřednictvím webového rozhraní. Aplikace je schopna vyhledávat předchozí soudní rozhodnutí na základě zadaného popisu případu, který se týká podobné problematiky. Výstupem aplikace jsou shrnutí nejpodobnějších případů a odkazy na jejich celý text. Aplikace také nabízí možnost dotazovat se na obsah konkrétního rozhodnutí, odpověď je generována pomocí LLM.</p>
                <p>K dispozici je také API, pomocí kterého je možné získat scrapovaná rozhodnutí včetně metadat. API také umožňuje scrapovat rozhodnutí na základě filtrů odpovídajících filtrům na webu justice.cz.</p>
                <p>Tvůrce aplikace neodpovídá za správnost či úplnost zpracovaných rozhodnutí a nenese odpovědnost za újmu způsobenou v souvislosti s použitím informací získaných z této aplikace.</p>
              </div>
              <div style={{ marginTop: '42px' }}>
                <Typography noWrap variant="h4" component="div">
                  Návod k použití
                </Typography>
                <p>Do hlavního textového okna popište případ, pro který mají být nalezeny soudní rozhodnutí řešící podobnou věc. Popis je možné formulovat přirozeným jazykem, ale také heslovitě; pro vyhledávání je důležitý význam nikoli forma.</p>
                <p>Databáze Ministerstva spravedlnosti, ze které jsou rozhodnutí získávána, obsahuje bohužel v současnosti pouze rozhodnutí civilních soudů v prvním stupni. Aplikace tedy nabídne smysluplné výsledky pouze pro oblasti spadající pod tuto agendu (např. spory o zaplacení částky, rozvod manželství atd.).</p>
                <p>Výsledkem vyhledávání bude několik nejpodobnějších soudních rozhodnutí. K dispozici je shrnutí rozhodnutí generované pomocí LLM a metadata. Celý text je dostupný po kliknutí na příslušný odkaz.</p>
                <p>Vpravo dole je možné po rozkliknutí lišty formulovat dotazy ohledně obsahu rozhodnutí. Tímto způsobem je možné doptat se na obsah rozhodnutí nad rámec shrnutí, aniž by bylo třeba jej nutně číst.</p>
              </div>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
    </>
  );
}
