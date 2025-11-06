import React from 'react';
import ContactCard from './ContactCard';

const ContactList = ({ contacts, onEdit, onDelete }) => {
  if (contacts.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-8 text-center">
        <p className="text-gray-500 text-lg">No contacts yet. Add your first contact to get started!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {contacts.map(contact => (
        <ContactCard
          key={contact._id}
          contact={contact}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
};

export default ContactList;