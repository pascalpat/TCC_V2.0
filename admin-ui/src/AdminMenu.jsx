import React from 'react';

export default function AdminMenu({ onSelect, activeSection }) {
  const sections = [
    { id: 'master', label: 'Master Data' },
    { id: 'documents', label: 'Documents/Media' },
    { id: 'users', label: 'User Accounts' },
    { id: 'importExport', label: 'Data Import/Export' }
  ];

  return (
    <nav id="adminMenu">
      {sections.map((sec) => (
        <button
          key={sec.id}
          id={`menu-${sec.id}`}
          onClick={() => onSelect(sec.id)}
          className={activeSection === sec.id ? 'active' : ''}
        >
          {sec.label}
        </button>
        ))}
    </nav>
  );
}