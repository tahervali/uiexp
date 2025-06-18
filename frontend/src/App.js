import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

const App = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [user, setUser] = useState(null);

  // Check if user is already logged in or handle OAuth redirect
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    const errorFromUrl = urlParams.get('error');
    
    if (tokenFromUrl) {
      setCookie('auth_token', tokenFromUrl);
      fetchUserProfile(tokenFromUrl);
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (errorFromUrl) {
      setMessage(`Authentication error: ${errorFromUrl}`);
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      const token = getCookie('auth_token');
      if (token) {
        fetchUserProfile(token);
      }
    }
  }, []);

  const setCookie = (name, value, days = 7) => {
    const expires = new Date(Date.now() + days * 864e5).toUTCString();
    document.cookie = `${name}=${value}; expires=${expires}; path=/`;
  };

  const getCookie = (name) => {
    return document.cookie.split('; ').reduce((r, v) => {
      const parts = v.split('=');
      return parts[0] === name ? decodeURIComponent(parts[1]) : r;
    }, '');
  };

  const deleteCookie = (name) => {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
  };

  const fetchUserProfile = async (token) => {
    try {
      const response = await fetch('http://localhost:8000/api/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        deleteCookie('auth_token');
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      deleteCookie('auth_token');
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    setLoading(true);
    setMessage('');

    if (!formData.email || !formData.password) {
      setMessage('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (!isLogin && formData.password !== formData.confirmPassword) {
      setMessage('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const endpoint = isLogin ? '/api/login' : '/api/signup';
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`${isLogin ? 'Login' : 'Signup'} successful!`);
        if (data.token) {
          setCookie('auth_token', data.token);
          setUser(data.user);
        }
        setFormData({ email: '', password: '', confirmPassword: '' });
      } else {
        setMessage(data.error || 'An error occurred');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSSOLogin = (provider) => {
    setLoading(true);
    window.location.href = `http://localhost:8000/api/auth/${provider}`;
  };

  const handleLogout = async () => {
    try {
      const token = getCookie('auth_token');
      await fetch('http://localhost:8000/api/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      deleteCookie('auth_token');
      setUser(null);
      setMessage('Logged out successfully');
    }
  };

  return (
    user ?
      <Dashboard user={user} onLogout={handleLogout} /> :
      <Login 
        onSubmit={handleSubmit} 
        onSSOLogin={handleSSOLogin} 
        isLogin={isLogin} 
        toggleLoginMode={() => {
          setIsLogin(!isLogin);
          setFormData({ email: '', password: '', confirmPassword: '' });
          setMessage('');
        }}
        loading={loading} 
        message={message} 
        formData={formData} 
        handleInputChange={handleInputChange} 
      />
  );
};

export default App;
