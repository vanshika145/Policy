import { Header } from '@/components/Header';
import { QueryInterface } from '@/components/QueryInterface';

const QueryPage = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <div className="pt-16">
        <QueryInterface />
      </div>
    </div>
  );
};

export default QueryPage;