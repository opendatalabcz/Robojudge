import React, { useEffect, useState } from "react";
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
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import axios from "axios";
import { Close } from "@mui/icons-material";

import { Case } from "../utils/types";
import {
  CLICK_TO_COPY_PROMPT,
  FETCH_ANSWER_ERROR_ALERT,
  MAX_QUESTION_LENGTH,
  QUESTION_INPUT_TOO_LONG,
} from "../utils/consts";

const styles = {
  caseCard: {
    minHeight: "200px",
    minWidth: "250px",
    maxWidth: "1200px",
    padding: "1rem",
    position: "relative",
    margin: "auto",
    marginTop: "2rem",
    marginBottom: "2rem",
    overflow: "visible",
  },
  caseCardHeader: {
    display: "flex",
    justifyContent: "space-between",
  },
  caseCardSticker: {
    position: "absolute",
    borderBottom: `26px solid #597081`,
    color: "white",
    cursor: "pointer",
    userSelect: "none",
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

function ExpandMore(props: ExpandMoreProps) {
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
}

export type CaseCardQuestionInterfaceProps = {
  courtCase: Case;
  triggerAlert: (text: string) => void;
};

function CaseCardQuestionInterface({
  courtCase,
  triggerAlert,
}: CaseCardQuestionInterfaceProps) {
  const [isCardExpanded, setIsCardExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const [caseQuestion, setCaseQuestion] = useState("");
  const [caseAnswer, setCaseAnswer] = useState("");

  const [tooltipText, setTooltipText] = useState("");

  useEffect(() => {
    if (courtCase.isLoading) {
      setIsCardExpanded(false);
      setCaseQuestion("");
      setCaseAnswer("");
    }
  }, [courtCase]);

  useEffect(() => {
    if (caseQuestion.length > MAX_QUESTION_LENGTH) {
      setTooltipText(QUESTION_INPUT_TOO_LONG);
    } else {
      setTooltipText("");
    }
  }, [caseQuestion]);

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
      triggerAlert(FETCH_ANSWER_ERROR_ALERT);
    } finally {
      setIsLoading(false);
    }
  };

  return (
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
            InputProps={{
              endAdornment: (
                <IconButton
                  sx={{
                    visibility: caseQuestion ? "visible" : "hidden",
                    padding: "0",
                  }}
                  onClick={() => {
                    setCaseQuestion("");
                  }}
                >
                  <Close />
                </IconButton>
              ),
            }}
          />
          <div>
            <Tooltip title={tooltipText} placement="bottom">
              <div>
                <Button
                  variant="outlined"
                  disabled={isLoading || !caseQuestion || !!tooltipText}
                  onClick={sendCaseQuestion}
                >
                  Odeslat
                </Button>
              </div>
            </Tooltip>
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
  );
}

export type CardCardProps = {
  courtCase: Case;
  triggerAlert: (text: string) => void;
};

export function CaseCard({ courtCase, triggerAlert }: CardCardProps) {
  return (
    <Card style={styles.caseCard} variant="outlined">
      <Tooltip placement="right" title={CLICK_TO_COPY_PROMPT}>
        <div
          style={styles.caseCardSticker}
          onClick={() => {
            !courtCase.isLoading
              ? navigator.clipboard.writeText(
                  (courtCase?.metadata?.jednaciCislo as string) ?? "",
                )
              : null;
          }}
        >
          <Typography variant="button">
            {!courtCase.isLoading
              ? (courtCase.metadata?.jednaciCislo as string) ?? ""
              : null}
          </Typography>
        </div>
      </Tooltip>
      <CardContent>
        <div style={styles.caseCardHeader}>
          {courtCase.isLoading ? (
            <Skeleton
              animation="wave"
              variant="text"
              width={"50%"}
              height={"2rem"}
            />
          ) : (
            <Typography variant="h5">
              {(courtCase.title as string) ?? ""}
            </Typography>
          )}

          {courtCase.isLoading ? (
            <Skeleton animation="wave" width={"50px"} />
          ) : (
            <span
              style={{
                whiteSpace: "nowrap",
                marginTop: "-1rem",
                marginRight: "-1rem",
              }}
            >
              Datum vydání:{" "}
              {formatDate((courtCase.metadata.sentenceDate as string) ?? "")}
            </span>
          )}
        </div>

        {!courtCase.isLoading ? (
          ((courtCase.metadata?.keywords as Array<string>) ?? []).map(
            (keyword) => (
              <Chip
                key={keyword}
                label={keyword}
                style={{
                  marginRight: "0.75rem",
                  marginBottom: "0.75rem",
                  marginTop: "0.75rem",
                }}
              />
            ),
          )
        ) : (
          <Skeleton
            animation="wave"
            variant="text"
            width={"60%"}
            height={"1rem"}
          />
        )}

        {!courtCase.isLoading ? (
          <Typography gutterBottom>{courtCase.summary}</Typography>
        ) : (
          <Skeleton animation="wave" height={"8rem"} width={"100%"} />
        )}

        {!courtCase.isLoading ? (
          <a
            href={`${process.env.REACT_APP_JUSTICE_URL}/${courtCase.caseId}`}
            target="_blank"
            rel="noopener noreferrer"
          >
            Celý text
          </a>
        ) : null}
      </CardContent>
      {!courtCase.isLoading ? (
        <CaseCardQuestionInterface
          courtCase={courtCase}
          triggerAlert={triggerAlert}
        />
      ) : null}
    </Card>
  );
}
