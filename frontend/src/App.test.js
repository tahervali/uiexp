import { render, screen } from '@testing-library/react';
import App from './App';

test('renders welcome message', () => {
  render(<App />);
  const welcomeMessage = screen.getByText(/Welcome Back/i);
  expect(welcomeMessage).toBeInTheDocument();
});

test('renders sign up message', () => {
  render(<App />);
  const toggleButton = screen.getByText(/Sign up/i);
  toggleButton.click();
  const signupMessage = screen.getByText(/Create Account/i);
  expect(signupMessage).toBeInTheDocument();
});

test('renders login button', () => {
  render(<App />);
  const loginButton = screen.getByText(/Sign In/i);
  expect(loginButton).toBeInTheDocument();
});

test('renders logout button when logged in', () => {
  render(<App />);
  // Simulate user login
  const user = { email: 'test@example.com', name: 'Test User' };
  const setUser = jest.fn();
  App.__Rewire__('useState', jest.fn(() => [user, setUser]));
  const logoutButton = screen.getByText(/Logout/i);
  expect(logoutButton).toBeInTheDocument();
});
