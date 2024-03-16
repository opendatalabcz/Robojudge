import React, { useState } from "react";
import { formatDate } from "../utils/dateFormatter";
import Grid2 from "@mui/material/Unstable_Grid2/Grid2";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Collapse,
  IconButton,
  IconButtonProps,
  LinearProgress,
  Skeleton,
  TextField,
  Tooltip,
  Typography,
} from "@mui/material";
import { Case } from "../pages/home";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import axios from "axios";

const styles = {
  caseCard: {
    minHeight: "200px",
    minWidth: "250px",
    maxWidth: "1200px",
    padding: "1rem",
    position: "relative",
    margin: 'auto',
    marginTop: '2rem',
    marginBottom: '2rem',
    overflow: "visible",
  },
  caseCardHeader: {
    display: "flex",
    justifyContent: "space-between",
  },
  caseCardSticker: {
    position: "absolute",
    borderBottom: "26px solid #597081",
    color: 'white',
    cursor: 'pointer',
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

export const ExpandMore = (props: ExpandMoreProps) => {
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
        `${process.env.REACT_APP_SERVER_URL ?? "http://localhost:4000"}/cases/${courtCase.caseId
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
    <Card style={styles.caseCard} variant="outlined">
      <Tooltip placement="right" title='Kliknutím zkopírujete číslo jednací.'>
        <div style={styles.caseCardSticker} onClick={() => {
          !courtCase.isLoading ? navigator.clipboard.writeText(courtCase?.metadata?.jednaciCislo as string ?? "") : null
        }}>
          < Typography variant="button" >
            {!courtCase.isLoading ? (courtCase.metadata?.jednaciCislo as string) ?? "" : null}
          </Typography>
        </div>
      </Tooltip >
      <CardContent>
        <div style={styles.caseCardHeader}>
          {courtCase.isLoading ?
            <Skeleton animation="wave" variant='text' width={'50%'} height={'2rem'} />

            : <Typography variant="h5">
              {(courtCase.title as string) ?? ""}
            </Typography>}

          {courtCase.isLoading ? <Skeleton animation="wave" width={'50px'} />
            :
            <span style={{ whiteSpace: 'nowrap', marginTop: '-1rem', marginRight: '-1rem' }} >
              Datum vydání:{" "}
              {formatDate((courtCase.metadata.sentenceDate as string) ?? "")}
            </span>
          }
        </div>

        {!courtCase.isLoading ?
          ((courtCase.metadata?.keywords as Array<string>) ?? []).map((keyword) => <Chip key={keyword} label={keyword} style={{marginRight: '0.75rem', marginBottom: '0.75rem', marginTop: '0.75rem'}} />)
          : <Skeleton animation="wave" variant='text' width={'60%'} height={'1rem'} />
        }

        {!courtCase.isLoading ?
          <Typography gutterBottom>{courtCase.summary}</Typography>
          : <Skeleton animation="wave" height={'8rem'} width={'100%'} />}

        {!courtCase.isLoading ?
          <a
            href={`${process.env.REACT_APP_JUSTICE_URL}/${courtCase.caseId}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Celý text
          </a>
          : null}
      </CardContent>
      {
        !courtCase.isLoading ?

          <>

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
          </>
          : null
      }
    </Card >
  );
};
