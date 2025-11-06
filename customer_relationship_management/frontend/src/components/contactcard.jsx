import React from 'react';

const ContactCard = ({ contact, onEdit, onDelete }) => {
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete ${contact.name}?`)) {
      onDelete(contact._id);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-gray-800">{contact.name}</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => onEdit(contact)}
            className="text-blue-500 hover:text-blue-700"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="text-red-500 hover:text-red-700"
          >
            Delete
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {contact.email && (
          <p className="text-gray-600">
            <span className="font-medium">Email:</span> {contact.email}
          </p>
        )}
        
        {contact.phone && (
          <p className="text-gray-600">
            <span className="font-medium">Phone:</span> {contact.phone}
          </p>
        )}
        
        {contact.company && (
          <p className="text-gray-600">
            <span className="font-medium">Company:</span> {contact.company}
          </p>
        )}

        {contact.tags && contact.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {contact.tags.map((tag, index) => (
              <span
                key={index}
                className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {contact.notes && (
          <p className="text-gray-600 mt-3 text-sm">
            <span className="font-medium">Notes:</span> {contact.notes}
          </p>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
        Last contacted: {new Date(contact.lastContact).toLocaleDateString()}
      </div>
    </div>
  );
};

export default ContactCard;