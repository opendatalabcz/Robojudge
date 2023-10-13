import React, { useState } from "react";
import { formatDate } from "../utils/dateFormatter";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  Collapse,
  IconButton,
  IconButtonProps,
  LinearProgress,
  TextField,
  Typography,
} from "@mui/material";
import { Case } from "../pages/home";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import axios from "axios";

const styles = {
  caseCard: {
    minHeight: "200px",
    minWidth: "500",
    padding: "1rem",
    position: "relative",
    overflow: "visible",
  },
  caseCardHeader: {
    display: "flex",
    justifyContent: "space-between",
  },
  caseCardSticker: {
    position: "absolute",
    borderBottom: "26px solid #d3d0d0",
    borderLeft: "12px solid transparent",
    borderRight: "12px solid transparent",
    height: 0,
    top: "-26px",
    width: "140px",
    textAlign: "center",
  },
  questionAnswerBox: {},
  questionContainer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "1rem",
  },
} as Record<string, React.CSSProperties>;

interface ExpandMoreProps extends IconButtonProps {
  expand: boolean;
}

const ExpandMore = (props: ExpandMoreProps) => {
  const { expand, ...other } = props;
  return (
    <IconButton
      style={{
        transform: !expand ? "rotate(0deg)" : "rotate(180deg)",
        marginLeft: "auto",
        float: "right",
      }}
      {...other}
    />
  );
};

export type CardCardProps = {
  courtCase: Case;
  triggerAlert: (text: string) => void;
};

export const CaseCard = ({ courtCase, triggerAlert }: CardCardProps) => {
  const [isCardExpanded, setIsCardExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [caseQuestion, setCaseQuestion] = useState("");
  const [caseAnswer, setCaseAnswer] = useState("");

  const sendCaseQuestion = async () => {
    try {
      setIsLoading(true);

      const { data } = await axios.post(
        `${process.env.REACT_APP_SERVER_URL ?? "http://localhost:4000"}/cases/${
          courtCase.caseId
        }/question`,
        {
          question: caseQuestion,
        },
      );

      setCaseAnswer(data?.answer);
    } catch (err) {
      console.error(err);
      triggerAlert(
        "Při dotazování nastala chyba. Opakujte prosím akci za chvíli.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Grid2 xs={12}>
      <Card style={styles.caseCard} variant="outlined">
        <div style={styles.caseCardSticker}>
          <Typography variant="button">
            {(courtCase.metadata?.jednaciCislo as string) ?? ""}
          </Typography>
        </div>
        <CardContent>
          <div style={styles.caseCardHeader}>
            <Typography variant="h5">
              {(courtCase.title as string) ?? ""}
            </Typography>
            <span>
              Datum vydání:{" "}
              {formatDate((courtCase.metadata.sentenceDate as string) ?? "")}
            </span>
          </div>

          <Typography variant="overline" gutterBottom>
            {((courtCase.metadata?.keywords as Array<string>) ?? []).join(", ")}
          </Typography>
          <Typography gutterBottom>{courtCase.summary}</Typography>
          <a
            href={`${process.env.REACT_APP_JUSTICE_URL}/${courtCase.caseId}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Celý text
          </a>
        </CardContent>
        <CardActions style={{ margin: "-1rem" }}>
          <ExpandMore
            expand={isCardExpanded}
            onClick={() => setIsCardExpanded(!isCardExpanded)}
            aria-expanded={isCardExpanded}
            aria-label="show more"
          >
            <ExpandMoreIcon />
          </ExpandMore>
        </CardActions>
        <Collapse in={isCardExpanded} timeout="auto" unmountOnExit>
          <Grid2 style={styles.questionContainer}>
            <TextField
              fullWidth
              label="Dotaz týkající se obsahu rozhodnutí"
              placeholder="např. Jak vysokou náhradu škody soud žalobci přiznal?"
              value={caseQuestion}
              onChange={(e) => setCaseQuestion(e.target.value)}
              onKeyDown={(e) =>
                e.key === "Enter" && caseQuestion ? sendCaseQuestion() : null
              }
            />
            <div>
              <Button
                variant="outlined"
                disabled={isLoading || !caseQuestion}
                onClick={sendCaseQuestion}
              >
                Odeslat
              </Button>
            </div>
          </Grid2>
          <Grid2>
            {isLoading ? (
              <>
                <LinearProgress />
                <Typography
                  variant="body2"
                  color="text.secondary"
                  style={{ marginTop: "1rem" }}
                >
                  Hledám odpověď
                </Typography>
              </>
            ) : (
              <>
                <Typography variant="h6" gutterBottom>
                  {caseAnswer ? "Odpověď:" : ""}
                </Typography>
                <Typography variant="body1"> {caseAnswer}</Typography>
              </>
            )}
          </Grid2>
        </Collapse>
      </Card>
    </Grid2>
  );
};
