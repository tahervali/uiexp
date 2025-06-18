import React from 'react';
import { User } from 'lucide-react';

const Dashboard = ({ user, onLogout }) => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <User className="w-10 h-10 text-green-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800">Welcome!</h2>
          <p className="text-gray-600 mt-2">You are successfully logged in</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-gray-800 mb-2">Profile Information</h3>
          <p className="text-sm text-gray-600"><strong>Email:</strong> {user.email}</p>
          <p className="text-sm text-gray-600"><strong>Name:</strong> {user.name || 'Not provided'}</p>
          <p className="text-sm text-gray-600"><strong>Provider:</strong> {user.provider || 'Email'}</p>
        </div>

        <button
          onClick={onLogout}
          className="w-full bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-300 font-medium"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
