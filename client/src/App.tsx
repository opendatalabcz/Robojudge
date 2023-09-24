import React, { useState } from 'react';
import { Home } from './pages/home';
import { AppBar, Typography } from '@mui/material';
import { FloatingAlert } from './components/FloatingAlert';
import { ErrorPage } from './pages/error';
import { ErrorBoundary } from 'react-error-boundary';

const styles = {
  app: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
  mainPageContainer: { height: '100%', position: 'relative', flex: 1 },
} as Record<string, React.CSSProperties>;

function App() {
  const [isErrorAlertShown, setIsErrorAlertShown] = useState(false);
  const [alertText, setAlertText] = useState('');

  const triggerAlert = (text: string) => {
    setIsErrorAlertShown(true);
    setAlertText(text);
  }

  return (
    <div className="App" style={styles.app}>
      <AppBar position='relative' >
        <Typography padding="0.5rem" noWrap variant="h5" component="div">
          RoboJudge
        </Typography>
      </AppBar>
      <div style={styles.mainPageContainer}>
        <ErrorBoundary FallbackComponent={ErrorPage} onError={(err) => console.error(err)}>
          <Home triggerAlert={triggerAlert} />
        </ErrorBoundary>
      </div>
      <AppBar position='relative'>
        <Typography padding="0.5rem" noWrap component="div">
          © 2023
        </Typography>
      </AppBar>
      <FloatingAlert isShown={isErrorAlertShown} setShown={setIsErrorAlertShown} text={alertText} />
    </div>
  );
}

export default App;
