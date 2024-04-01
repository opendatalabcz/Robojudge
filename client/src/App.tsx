import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import { Home } from "./pages/home";
import { FloatingAlert } from "./components/FloatingAlert";
import { ErrorPage } from "./pages/error";
import { ErrorBoundary } from "react-error-boundary";
import { Info } from "./pages/info";
import { Api } from "./pages/api";
import { HeaderBar } from "./components/HeaderBar";
import { FooterBar } from "./components/FooterBar";

const styles = {
  app: {
    display: "flex",
    flexDirection: "column",
    minHeight: "100vh",
  },
  mainPageContainer: { height: "100%", position: "relative", flex: 1 },
} as Record<string, React.CSSProperties>;

function App() {
  const [isErrorAlertShown, setIsErrorAlertShown] = useState(false);
  const [alertText, setAlertText] = useState("");

  const triggerAlert = (text: string) => {
    setIsErrorAlertShown(true);
    setAlertText(text);
  };

  return (
    <Router>
      <div className="App" style={styles.app}>
        <HeaderBar />
        <div style={styles.mainPageContainer}>
          <ErrorBoundary
            FallbackComponent={ErrorPage}
            onError={(err) => console.error(err)}
          >
            <Routes>
              <Route path="/" element={<Home triggerAlert={triggerAlert} />} />
              <Route path="/info" element={<Info />} />
              <Route path="/docs" element={<Api />} />
            </Routes>
          </ErrorBoundary>
        </div>
        <FooterBar />
        <FloatingAlert
          isShown={isErrorAlertShown}
          setShown={setIsErrorAlertShown}
          text={alertText}
          positionHorizontal="center"
          positionVertical="top"
        />
      </div>
    </Router>
  );
}

export default App;
