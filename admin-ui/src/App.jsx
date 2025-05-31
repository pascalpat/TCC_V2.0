import React, { useState } from 'react';
import ProjectForm from './pages/ProjectForm';
import AdminMenu from './AdminMenu';
import WorkerForm from './WorkerForm';
import UploadMedia from './UploadMedia';
import UserAccountForm from './UserAccountForm';
import DatabaseBackup from './DatabaseBackup';
import './admin.css';

function App() {

  const [activeSection, setActiveSection] = useState('project');

  let content;
  switch (activeSection) {
    case 'master':
      content = <WorkerForm />;
      break;
    case 'documents':
      content = <UploadMedia />;
      break;
    case 'users':
      content = <UserAccountForm />;
      break;
    case 'importExport':
      content = <DatabaseBackup />;
      break;
    default:
      content = <ProjectForm />;
  }

  return (
    <>
      <AdminMenu onSelect={setActiveSection} activeSection={activeSection} />
      {content}
    </>
  );

}

export default App;