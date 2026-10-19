import React, { useState } from 'react';
import SplashScreen from './components/common/SplashScreen';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';

/**
 * App Root Component
 * Coordinates brief branded splash presentation and mounts main application shell.
 */
export default function App() {
  const [showSplash, setShowSplash] = useState(true);

  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  return (
    <>
      {showSplash && <SplashScreen onFinish={handleSplashFinish} />}
      <MainLayout>
        <HomePage />
      </MainLayout>
    </>
  );
}
