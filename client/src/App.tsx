import React, { useState } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Link
} from "react-router-dom";

import { Home } from './pages/home';
import { AppBar, Button, ButtonGroup, Typography } from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';
import { FloatingAlert } from './components/FloatingAlert';
import { ErrorPage } from './pages/error';
import { ErrorBoundary } from 'react-error-boundary';
import { Info } from './pages/info';
import Grid2 from '@mui/material/Unstable_Grid2/Grid2';
import { Api } from './pages/api';

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
    <Router>
      <div className="App" style={styles.app}>
        <AppBar position='relative' style={{ justifyContent: 'space-between', flexDirection: 'row' }}>
          <Button component={Link} to='/' type='text' style={{ color: 'white' }}>
            <Typography padding="0.5rem" noWrap variant="h4" component="div" style={{ display: 'flex', alignItems: 'center', letterSpacing: '0.03REM' }}>
              <GavelIcon style={{ marginRight: '10px', fontSize: '30px' }} />
              RoboJudge
            </Typography>
          </Button>
          <ButtonGroup variant='text'>
            <Button component={Link} to='/info' style={{ color: 'white' }}>
              <Typography padding="0.5rem" variant='h6' noWrap component="div">
                Info
              </Typography>
            </Button>
            <Button component={Link} to='/api' style={{ color: 'white' }}>
              <Typography padding="0.5rem" variant="h6" noWrap component="div">
                API
              </Typography>
            </Button>
          </ButtonGroup>
        </AppBar>
        <div style={styles.mainPageContainer}>
          <ErrorBoundary FallbackComponent={ErrorPage} onError={(err) => console.error(err)}>
            <Routes>
              <Route path='/' element={<Home triggerAlert={triggerAlert} />} />
              <Route path='/info' element={<Info triggerAlert={triggerAlert} />} />
              <Route path='/api' element={<Api triggerAlert={triggerAlert} />} />
            </Routes>
          </ErrorBoundary>
        </div>
        <AppBar position='relative' style={{ 'background': 'white' }}>
          <Grid2 style={{ paddingRight: '1em', display: 'flex', justifyContent: 'flex-end', gap: '1em', alignItems: 'center' }}>
            <a href='https://fit.cvut.cz/cs'>
              <img src="/fit-cvut-logo-cs.svg" style={{ width: '100px' }} />
            </a>
            <a href="https://github.com/opendatalabcz/Robojudge">
              <img src="/github-logo-black.svg" style={{ width: '30px' }} />
            </a>
            <a href="https://opendatalab.cz/">
              <img src="/opendatalab-logo.png" style={{ width: '55px' }} />
            </a>
          </Grid2>
        </AppBar>
        <FloatingAlert isShown={isErrorAlertShown} setShown={setIsErrorAlertShown} text={alertText} />
      </div>
    </Router >
  );
}

export default App;
