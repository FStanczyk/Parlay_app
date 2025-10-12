import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Mock react-router-dom to avoid issues with routing in tests
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Routes: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Route: ({ element }: { element: React.ReactNode }) => <div>{element}</div>,
  useNavigate: () => jest.fn(),
}));

// Mock axios to avoid ES module issues
jest.mock('axios', () => ({
  post: jest.fn(),
  get: jest.fn(),
}));

test('renders parlay app', () => {
  render(<App />);
  const navbarElement = screen.getByRole('banner');
  expect(navbarElement).toBeInTheDocument();
  
  const welcomeElement = screen.getByText(/Welcome to Parlay App/i);
  expect(welcomeElement).toBeInTheDocument();
});
