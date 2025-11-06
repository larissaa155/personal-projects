import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './components/Login';
import Register from './components/Register';
import ContactList from './components/ContactList';
import ContactForm from './components/ContactForm';
import { contactsAPI } from './services/api';

function AppContent() {
  const { user, logout, loading } = useAuth();
  const [contacts, setContacts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [currentView, setCurrentView] = useState('login');

  useEffect(() => {
    if (user) {
      loadContacts();
    }
  }, [user]);

  const loadContacts = async () => {
    try {
      const data = await contactsAPI.getAll();
      setContacts(data);
    } catch (error) {
      console.error('Error loading contacts:', error);
    }
  };

  const handleCreateContact = async (contactData) => {
    try {
      await contactsAPI.create(contactData);
      await loadContacts();
      setShowForm(false);
    } catch (error) {
      console.error('Error creating contact:', error);
    }
  };

  const handleUpdateContact = async (id, contactData) => {
    try {
      await contactsAPI.update(id, contactData);
      await loadContacts();
      setEditingContact(null);
    } catch (error) {
      console.error('Error updating contact:', error);
    }
  };

  const handleDeleteContact = async (id) => {
    try {
      await contactsAPI.delete(id);
      await loadContacts();
    } catch (error) {
      console.error('Error deleting contact:', error);
    }
  };

  if (loading) {
    return <div className="min-h-screen bg-gray-100 flex items-center justify-center">Loading...</div>;
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        {currentView === 'login' ? (
          <Login onSwitchToRegister={() => setCurrentView('register')} />
        ) : (
          <Register onSwitchToLogin={() => setCurrentView('login')} />
        )}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">ContactKeeper</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-600">Hello, {user.name}</span>
            <button
              onClick={logout}
              className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Your Contacts</h2>
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Add Contact
          </button>
        </div>

        {showForm && (
          <ContactForm
            onSubmit={handleCreateContact}
            onCancel={() => setShowForm(false)}
          />
        )}

        {editingContact && (
          <ContactForm
            contact={editingContact}
            onSubmit={(data) => handleUpdateContact(editingContact._id, data)}
            onCancel={() => setEditingContact(null)}
          />
        )}

        <ContactList
          contacts={contacts}
          onEdit={setEditingContact}
          onDelete={handleDeleteContact}
        />
      </main>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;