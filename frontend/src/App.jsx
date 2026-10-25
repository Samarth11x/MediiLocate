import React, { useState } from 'react';
import SplashScreen from './components/common/SplashScreen';
import MainLayout from './layouts/MainLayout';
import HomePage from './pages/HomePage';
import UserPortalPage from './pages/UserPortalPage';
import PharmacistDashboardPage from './pages/PharmacistDashboardPage';
import PharmacistRegisterPage from './pages/PharmacistRegisterPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';
import ProtectedRoute from './components/common/ProtectedRoute';
import { RouterProvider, useRouter } from './context/RouterContext';
import { AuthProvider } from './context/AuthContext';

/**
 * Route switcher matching currentPath to the appropriate page.
 */
function AppRoutes() {
  const { currentPath } = useRouter();

  // Normalize path (strip query, hash, and trailing slashes if not root)
  const cleanPath = (currentPath || '/').split('?')[0].split('#')[0] || '/';
  const normalizedPath = cleanPath.length > 1 && cleanPath.endsWith('/')
    ? cleanPath.slice(0, -1)
    : cleanPath;

  let pageContent;
  switch (normalizedPath) {
    case '':
    case '/':
      pageContent = <HomePage />;
      break;

    case '/app':
      pageContent = (
        <ProtectedRoute allowedRoles={['USER', 'PHARMACIST', 'ADMIN']}>
          <UserPortalPage />
        </ProtectedRoute>
      );
      break;

    case '/login':
      pageContent = <LoginPage />;
      break;

    case '/register':
      pageContent = <RegisterPage />;
      break;

    case '/pharmacist/register':
      pageContent = <PharmacistRegisterPage />;
      break;

    case '/pharmacist/dashboard':
      pageContent = (
        <ProtectedRoute allowedRoles={['PHARMACIST', 'ADMIN']}>
          <PharmacistDashboardPage />
        </ProtectedRoute>
      );
      break;

    case '/admin/dashboard':
      pageContent = (
        <ProtectedRoute allowedRoles={['ADMIN']}>
          <AdminDashboardPage />
        </ProtectedRoute>
      );
      break;

    default:
      pageContent = <NotFoundPage />;
      break;
  }

  return <MainLayout>{pageContent}</MainLayout>;
}

/**
 * App Root Component
 * Coordinates brief branded splash presentation, router context,
 * auth context, and mounts the active application route.
 */
export default function App() {
  const [showSplash, setShowSplash] = useState(true);

  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  return (
    <RouterProvider>
      <AuthProvider>
        {showSplash && <SplashScreen onFinish={handleSplashFinish} />}
        <AppRoutes />
      </AuthProvider>
    </RouterProvider>
  );
}
