import { Header } from '@/components/Header';
import { DocumentUpload } from '@/components/DocumentUpload';

const DocumentsPage = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <div className="pt-16">
        <DocumentUpload />
      </div>
    </div>
  );
};

export default DocumentsPage;