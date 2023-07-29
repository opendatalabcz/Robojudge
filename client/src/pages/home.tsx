import React, { useState } from "react";
import axios from "axios";
import { Col, Container, Row, Spinner } from "react-bootstrap";
import { Button } from "react-bootstrap";
import { Card } from "react-bootstrap";
import { Form } from "react-bootstrap";
import { convertObjectKeysToCamelCase } from "../utils/camelCaser";
import { formatDate } from "../utils/dateFormatter";

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
  },
  caseCard: {
    minHeight: "350px",
    padding: "1rem",
    marginTop: "1rem",
    marginBottom: "1rem",
    maxWidth: "750px",
  },
  caseCardHeader: {
    display: "flex",
    justifyContent: "space-between",
  },
};

export function Home() {
  const [caseDescription, setCaseDescription] = useState("");
  const [cases, setCases] = useState<Case[]>([]);

  const [isLoading, setIsLoading] = useState(false);

  const searchForCases = async () => {
    try {
      setIsLoading(true);

      const { data } = await axios.post(
        `${process.env.REACT_APP_SERVER_URL ?? ""}/summary/search`,
        {
          query_text: caseDescription,
          limit: 2,
        },
      );

      console.log(data.map(convertObjectKeysToCamelCase));

      // TODO: Remove for production...
      setCases([
        ...data.map(convertObjectKeysToCamelCase),
        ...data.map(convertObjectKeysToCamelCase),
        ...data.map(convertObjectKeysToCamelCase),
        ...data.map(convertObjectKeysToCamelCase),
      ]);
      setIsLoading(false);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <>
      <Container fluid style={{ padding: "1rem" }}>
        {isLoading ? (
          <div
            style={{
              position: "absolute",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              width: "100%",
              height: "100%",
              zIndex: 1,
              background: "#8080800a",
            }}
          >
            <Spinner animation="grow" variant="primary" />
          </div>
        ) : null}
        <Row xs={12} style={{ display: "flex", justifyContent: "center" }}>
          <Card style={styles.searchCard} border="primary">
            <Card.Title>RoboJudge</Card.Title>
            <Card.Body>
              <>
                <Form.Text id="search-input-help" muted>
                  Zadejte popis případu, pro který chcete najít již rozhodnuté
                  případy podobné. Nejlepších výsledků dosáhnete zadáním ca. 200
                  slov a použitím právní terminologie.
                </Form.Text>
                <Form.Control
                  as="textarea"
                  id="search-input"
                  maxLength={1800}
                  rows={10}
                  aria-describedby="search-input-help"
                  value={caseDescription}
                  onChange={(e) => setCaseDescription(e.target.value)}
                />
              </>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <hr />
                  <span>Dislcaimer: ...</span>
                </div>
                <div>
                  <Button
                    variant="primary"
                    onClick={searchForCases}
                    disabled={isLoading}
                  >
                    Hledat
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>
        </Row>
        <Row>
          {cases.map(({ id, summary, metadata }) => (
            <Col xs={12} lg={4} key={id}>
              <Card style={styles.caseCard}>
                <div style={styles.caseCardHeader}>
                  <Card.Title>
                    {(metadata?.jednaciCislo as string) ?? ""}
                  </Card.Title>
                  <span>
                    {formatDate((metadata.sentenceDate as string) ?? "")}
                  </span>
                </div>
                <Card.Subtitle>
                  {(metadata?.court as string) ?? ""}
                </Card.Subtitle>
                <span>
                  {((metadata?.keywords as Array<string>) ?? []).join(", ")}
                </span>
                <hr />
                <Card.Text>{summary}</Card.Text>
                <a
                  href={`${process.env.REACT_APP_JUSTICE_URL}/${id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Celý text
                </a>
              </Card>
            </Col>
          ))}
        </Row>
      </Container>
    </>
  );
}
