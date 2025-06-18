import { render, screen } from '@testing-library/react';
import App from './App';

test('renders login form', () => {
  render(<App />);
  const loginHeader = screen.getByText(/welcome back/i);
  expect(loginHeader).toBeInTheDocument();
});

test('renders dashboard when user is logged in', () => {
  // Mocking user state for testing
  const originalUseState = React.useState;
  jest.spyOn(React, 'useState').mockImplementationOnce(() => [{ email: 'test@example.com' }, jest.fn()]);

  render(<App />);
  const dashboardHeader = screen.getByText(/welcome!/i);
  expect(dashboardHeader).toBeInTheDocument();

  // Restore original useState
  React.useState = originalUseState;
});
