import React, { useState } from 'react';
import './App.css';
import { Home } from './pages/home';
import { AppBar, Typography } from '@mui/material';
import { FloatingAlert } from './components/FloatingAlert';

const appStyle = {
  display: 'flex',
  flexDirection: 'column',
  minHeight: '100vh',
} as React.CSSProperties;

function App() {
  const [isErrorAlertShown, setIsErrorAlertShown] = useState(false);
  const [alertText, setAlertText] = useState('');

  const triggerAlert = (text: string) => {
    setIsErrorAlertShown(true);
    setAlertText(text);
  }

  return (
    <div className="App" style={appStyle}>
      <AppBar position='relative' >
        <Typography padding="0.5rem" noWrap variant="h5" component="div">
          RoboJudge
        </Typography>
      </AppBar>
      <Home triggerAlert={triggerAlert} />
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
